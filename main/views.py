from django.shortcuts import render, redirect
import requests
from django.http import JsonResponse
from .models import HistoryScan, WebsiteHTML, BigramData
import logging
import csv
import io
import re
from collections import Counter

logger = logging.getLogger(__name__)

def create_bigrams(text):
    """
    Tạo bigrams từ HTML text và đếm tần suất xuất hiện
    Returns: dictionary với bigram làm key và tần suất làm value
    """
    # Làm sạch HTML: loại bỏ tags và giữ lại nội dung text
    clean_text = re.sub(r'<[^>]+>', ' ', text)
    
    # Chuyển về lowercase và loại bỏ ký tự đặc biệt
    clean_text = re.sub(r'[^\w\s]', ' ', clean_text.lower())
    
    # Tách thành các từ
    words = clean_text.split()
    
    # Tạo bigrams
    bigrams = []
    for i in range(len(words) - 1):
        bigram = f"{words[i]} {words[i+1]}"
        bigrams.append(bigram)
    
    # Đếm tần suất xuất hiện
    bigram_counts = Counter(bigrams)
    
    return bigram_counts

def save_bigrams_to_db(bigram_counts, label):
    """
    Lưu bigrams và tần suất vào database dưới dạng JSON
    """
    try:
        # Chuyển Counter thành dict thông thường
        bigram_dict = dict(bigram_counts)
        
        # Kiểm tra xem đã có record nào cho label này chưa
        existing_record = BigramData.objects.filter(label=label).first()
        
        if existing_record:
            # Cập nhật JSON: merge với data cũ
            old_bigrams = existing_record.bigram_json
            
            # Cộng tần suất cho các bigram đã tồn tại
            for bigram, freq in bigram_dict.items():
                if bigram in old_bigrams:
                    old_bigrams[bigram] += freq
                else:
                    old_bigrams[bigram] = freq
            
            existing_record.bigram_json = old_bigrams
            existing_record.total_bigrams = len(old_bigrams)
            existing_record.save()
            
            print(f"Updated existing record with {len(bigram_dict)} new bigrams for label: {label}")
            print(f"Total bigrams now: {existing_record.total_bigrams}")
        else:
            # Tạo record mới
            BigramData.objects.create(
                bigram_json=bigram_dict,
                label=label,
                total_bigrams=len(bigram_dict)
            )
            
            print(f"Created new record with {len(bigram_dict)} bigrams for label: {label}")
        
        return len(bigram_dict)
        
    except Exception as e:
        print(f"Error saving bigrams to database: {e}")
        return 0

def index(request):
    history_list = HistoryScan.objects.order_by('-scan_time')[:10]  # Lấy 10 bản ghi mới nhất
    latest_ids = HistoryScan.objects.order_by('-scan_time').values_list('id', flat=True)[:10]
    HistoryScan.objects.exclude(id__in=latest_ids).delete()

    return render(request, 'index.html', {'history_list': history_list})

def setting(request):
    return render(request, 'setting.html')

def upload_dataset(request):
    if request.method == 'POST':
        try:
            dataset_file = request.FILES.get('dataset_file')
            
            if dataset_file:
                print(f"== Upload Dataset: {dataset_file.name}")
                print(f"== File size: {dataset_file.size} bytes")
                
                # Đọc nội dung file trực tiếp từ memory (không lưu file)
                try:
                    if dataset_file.name.endswith('.csv'):
                        # Đọc CSV từ memory
                        file_content = dataset_file.read().decode('utf-8')
                        csv_reader = csv.DictReader(io.StringIO(file_content))
                        
                        print(f"== Column names: {csv_reader.fieldnames}")
                        
                        print("== First 5 rows:")
                        for i, row in enumerate(csv_reader):
                            if i >= 5:  # Chỉ in 5 dòng đầu
                                break
                            print(f"Row {i + 1}:")
                            html_content = row.get('HTML', row.get('html', ''))
                            label_content = row.get('label', row.get('Label', ''))
                            print(f"  HTML: {html_content[:100]}...")  # In 100 ký tự đầu
                            print(f"  Label: {label_content}")
                            
                            # Tạo bigrams từ HTML content
                            bigram_counts = create_bigrams(html_content)
                            print(f"  Total bigrams: {len(bigram_counts)}")
                            print(f"  Top 5 bigrams:")
                            for bigram, count in list(bigram_counts.most_common(5)):
                                print(f"    '{bigram}': {count}")
                            
                            # Lưu bigrams vào database
                            save_bigrams_to_db(bigram_counts, label_content)
                            
                            print("---")
                    
                    # Đọc file text/json từ memory
                    elif dataset_file.name.endswith(('.txt', '.json')):
                        content = dataset_file.read().decode('utf-8')
                        print(f"== File content (first 500 chars): {content[:500]}...")
                        
                except Exception as read_error:
                    print(f"== Error reading file content: {read_error}")
                
        except Exception as e:
            logger.exception(f"Error processing dataset: {e}")
    
    return redirect('setting')
    

def search(request):
    return redirect('de-defender')

def save_website_html(request):
    if request.method == 'POST':
        url = request.POST.get('weburl', '').strip()
        try:
            print(f"== save_website_html Saving HTML for URL: {url}")
            response = requests.get(url)
            response.raise_for_status()
            html_content = response.text
            print(f"== html_content: {html_content}")

            WebsiteHTML.objects.create(app_name = url, app_url=url, html_content=html_content)
        except Exception as e:
            logger.exception(f"Error save_website_html {url}: {e}")
    return redirect('de-defender')
    
def chart_data(request):
    labels = ['January', 'February', 'March', 'April', 'May', 'June', 'July']
    data = [100, 200, 150, 300, 250, 400, 350]
    return JsonResponse({
        'labels': labels,
        'data': data
    })
