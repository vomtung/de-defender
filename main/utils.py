# main/utils.py
import logging
import threading
import time
import hashlib
import requests
import re
import math
from bs4 import BeautifulSoup
from django.utils import timezone
from collections import Counter

from django.conf import settings

from main.models import HistoryScan, WebsiteHTML, BigramData
from main.models import ApplicationSetting

logger = logging.getLogger(__name__)

# Load AI/ML models từ models_ai folder
import os
import pickle

MODELS_PATH = os.path.join(os.path.dirname(__file__), 'models_ai')
MODEL_FILE = os.path.join(MODELS_PATH, 'logistic_regression.pkl')  # Đổi tên file model tại đây
VECTORIZER_FILE = os.path.join(MODELS_PATH, 'vectorizer.pkl')

try:
    with open(MODEL_FILE, 'rb') as f:
        logistic_regression_model = pickle.load(f)
    with open(VECTORIZER_FILE, 'rb') as f:
        vectorizer = pickle.load(f)
except Exception as e:
    logistic_regression_model = None
    vectorizer = None
    print(f"Không thể load model hoặc vectorizer từ models_ai: {e}")

def scanWebsite():
    websites = WebsiteHTML.objects.all()

    compare_html(websites)

    compare_checksum(websites)

    compare_dom_tree(websites)

    compare_bigrams(websites)

    #  compare_logistic_regression(websites)

            

            
def compare_html(websites):
    for site in websites:

        url = site.app_url
        old_html = site.html_content
        print(f"== scanWebsite Scanning HTML{url}")
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            new_html = response.text

            if new_html.strip() == old_html.strip():
                status = 'normal'
                HistoryScan.objects.create(
                app_id=site.id,
                app_name=site.app_name,
                app_url=site.app_url,
                method='COMPATRE-HTML',
                status='normal',
                scan_time=timezone.now()
            )
            else:
                status = 'attacked'
                HistoryScan.objects.create(
                app_id=site.id,
                app_name=site.app_name,
                app_url=site.app_url,
                method='COMPARE-HTML',
                status='attacked',
                scan_time=timezone.now()
                )
            logger.info(f"Scanned {url} - {status}")
        except Exception as e:
            logger.exception(f"Failed to scan {url}: {e}")

def compare_checksum(websites):
    for site in websites:
        url = site.app_url
        old_html = site.html_content.strip()

        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            new_html = response.text.strip()

            old_checksum = hashlib.md5(old_html.encode('utf-8')).hexdigest()
            new_checksum = hashlib.md5(new_html.encode('utf-8')).hexdigest()

            if old_checksum == new_checksum:
                status = 'normal'
            else:
                status = 'attacked'

            # Lưu kết quả vào HistoryScan
            HistoryScan.objects.create(
                app_id=site.id,
                app_name=site.app_name,
                app_url=site.app_url,
                method='COMPARE-CHECKSUM',
                status=status,
                scan_time=timezone.now()
            )

            print(f"[checksum] Scanned {url} - {status}")
        except Exception as e:
            print(f"[checksum] Failed to scan {url}: {e}")

def compare_dom_tree(websites):
    for site in websites:
        url = site.app_url
        old_html = site.html_content
        logger.info(f"== compare_dom_tree Scanning DOM for {url}")
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            new_html = response.text

            # Parse DOM trees
            old_soup = BeautifulSoup(old_html, 'html.parser')
            new_soup = BeautifulSoup(new_html, 'html.parser')

            # Serialize DOM structure (tag names only)
            def serialize_dom(soup):
                return [tag.name for tag in soup.find_all()]

            old_dom = serialize_dom(old_soup)
            new_dom = serialize_dom(new_soup)

            # So sánh
            if old_dom == new_dom:
                status = 'normal'
            else:
                status = 'attacked'

            # Lưu kết quả
            HistoryScan.objects.create(
                app_id=site.id,
                app_name=site.app_name,
                app_url=site.app_url,
                method='COMPARE-DOM',
                status=status,
                scan_time=timezone.now()
            )
            logger.info(f"DOM Tree scan {url} - {status}")

        except Exception as e:
            logger.exception(f"Error comparing DOM tree for {url}: {e}")


def create_bigrams(text):
    """
    Create bigrams from HTML text and count their frequency
    Returns: Counter object with bigram frequencies
    """
    # Clean HTML: remove tags and keep text content
    clean_text = re.sub(r'<[^>]+>', ' ', text)
    
    # Convert to lowercase and remove special characters
    clean_text = re.sub(r'[^\w\s]', ' ', clean_text.lower())
    
    # Split into words
    words = clean_text.split()
    
    # Create bigrams
    bigrams = []
    for i in range(len(words) - 1):
        bigram = f"{words[i]} {words[i+1]}"
        bigrams.append(bigram)
    
    # Count frequency of occurrence
    bigram_counts = Counter(bigrams)
    
    return bigram_counts

def cosine_similarity(vec1, vec2):
    """
    Calculate cosine similarity between two vectors (dictionaries)
    """
    # Get all unique features from both vectors
    all_features = set(vec1.keys()) | set(vec2.keys())
    
    # Create vectors with same dimensions
    v1 = [vec1.get(feature, 0) for feature in all_features]
    v2 = [vec2.get(feature, 0) for feature in all_features]
    
    # Calculate dot product
    dot_product = sum(a * b for a, b in zip(v1, v2))
    
    # Calculate magnitudes
    magnitude1 = math.sqrt(sum(a * a for a in v1))
    magnitude2 = math.sqrt(sum(b * b for b in v2))
    
    # Avoid division by zero
    if magnitude1 == 0 or magnitude2 == 0:
        return 0
    
    return dot_product / (magnitude1 * magnitude2)

def get_top_bigrams_profile():
    """
    Get profile of top bigrams from training data (label=0 records)
    Returns: Dictionary of top bigrams with their frequencies
    """
    # Get settings
    top_features = getattr(settings, 'BIGRAM_TOP_FEATURES', 300)
    
    # Get all normal websites (label=0) from training data
    normal_records = BigramData.objects.filter(label='0')
    
    if not normal_records.exists():
        print("No training data found (label=0)")
        return {}
    
    # Combine all bigrams from normal websites
    combined_bigrams = Counter()
    for record in normal_records:
        bigram_data = record.bigram_json
        if isinstance(bigram_data, dict):
            for bigram, count in bigram_data.items():
                combined_bigrams[bigram] += count
    
    # Get top N most frequent bigrams
    top_bigrams = dict(combined_bigrams.most_common(top_features))
    
    print(f"Profile created with {len(top_bigrams)} top bigrams")
    return top_bigrams

def compare_bigrams(websites):
    """
    Kim et al. approach: Bigram-based defacement detection using cosine similarity
    """
    # Get threshold from settings
    try:
        param = ApplicationSetting.objects.get(parameter_key='BIGRAM_COSIN_SIMILARITY_THRESHOLD')
        threshold = float(param.parameter_value)
    except (ApplicationSetting.DoesNotExist, ValueError):
        threshold = 0.7
    
    # Get profile of top bigrams from training data
    profile_bigrams = get_top_bigrams_profile()
    
    if not profile_bigrams:
        print("No bigram profile available. Please upload training dataset first.")
        return
    
    for site in websites:
        url = site.app_url
        print(f"== compare_bigrams Scanning {url}")
        
        try:
            # Get current website HTML
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            current_html = response.text
            
            # Create bigrams from current HTML
            current_bigrams = create_bigrams(current_html)
            
            # Filter current bigrams to only include features from profile
            filtered_current = {bigram: count for bigram, count in current_bigrams.items() 
                              if bigram in profile_bigrams}
            
            # Calculate cosine similarity with profile
            similarity = cosine_similarity(filtered_current, profile_bigrams)
            
            # Determine status based on similarity threshold
            if similarity >= threshold:
                status = 'normal'
            else:
                status = 'attacked'
            
            # Save result to HistoryScan
            HistoryScan.objects.create(
                app_id=site.id,
                app_name=site.app_name,
                app_url=site.app_url,
                method='COMPARE-BIGRAMS',
                status=status,
                meta="(similarity=" + str(similarity) + "),(threshold=" + str(threshold) + ")",
                scan_time=timezone.now()
            )
            
            print(f"Bigram similarity for {url}: {similarity:.4f} (threshold: {threshold}) - {status}")
            
        except Exception as e:
            print(f"Error in bigram similarity check for {url}: {e}")
            logger.exception(f"Bigram similarity error for {url}: {e}")

def compare_logistic_regression(websites):
    """
    Logistic Regression-based defacement detection
    Sử dụng model.pkl và vectorizer.pkl trong thư mục models_ai.
    """
    # Load threshold từ ApplicationSetting
    try:
        param = ApplicationSetting.objects.get(parameter_key='LOGISTIC_REGRESSION_THRESHOLD')
        threshold = float(param.parameter_value)
    except (ApplicationSetting.DoesNotExist, ValueError):
        threshold = 0.7

    if logistic_regression_model is None or vectorizer is None:
        print("Model hoặc vectorizer chưa được load. Vui lòng kiểm tra các file .pkl trong models_ai.")
        return

    for site in websites:
        url = site.app_url
        print(f"== compare_logistic_regression Scanning {url}")

        try:
            # Lấy HTML hiện tại của website
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            current_html = response.text

            # Biến đổi HTML thành feature vector bằng vectorizer
            features = vectorizer.transform([current_html])

            # Dự đoán xác suất bị deface (class 1)
            if hasattr(logistic_regression_model, "predict_proba"):
                predictions = logistic_regression_model.predict_proba(features)[:, 1]
            else:
                predictions = logistic_regression_model.predict(features)

            # Xác định trạng thái dựa trên ngưỡng
            if predictions[0] >= threshold:
                status = 'normal'
            else:
                status = 'attacked'

            # Lưu kết quả vào HistoryScan
            HistoryScan.objects.create(
                app_id=site.id,
                app_name=site.app_name,
                app_url=site.app_url,
                method='COMPARE-LOGISTIC-REGRESSION',
                status=status,
                meta="(prediction=" + str(predictions[0]) + "),(threshold=" + str(threshold) + ")",
                scan_time=timezone.now()
            )

            print(f"Logistic Regression prediction for {url}: {predictions[0]:.4f} (threshold: {threshold}) - {status}")

        except Exception as e:
            print(f"Error in logistic regression check for {url}: {e}")

def start_scheduler():
    def job():
        try:
            # Check if database tables exist before scanning
            from django.db import connection
            with connection.cursor() as cursor:
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='main_websitehtml';")
                if cursor.fetchone():
                    scanWebsite()
                else:
                    print("== Database tables not ready, skipping scan ==")
        except Exception as e:
            print(f"== Scheduler error: {e} ==")
        
        interval = settings.SCAN_INTERVAL_SECONDS
        t = threading.Timer(interval, job)
        t.daemon = True
        t.start()

    print("== Scheduler started ==")
    job()