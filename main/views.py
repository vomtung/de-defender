from django.shortcuts import render, redirect
import requests
from django.http import JsonResponse
from .models import HistoryScan, WebsiteHTML, BigramData
from django.conf import settings
import logging
import csv
import io
import re
from collections import Counter

logger = logging.getLogger(__name__)

def create_bigrams(text):
    """
    Create bigrams from HTML text and count their frequency
    Returns: dictionary with bigram as key and frequency as value
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

def save_bigrams_to_db(bigram_counts, label):
    """
    Save bigrams and frequency to database as JSON - Create separate record for each row
    """
    try:
        # Convert Counter to regular dictionary
        bigram_dict = dict(bigram_counts)
        
        # Create new record for each row
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
    history_list = HistoryScan.objects.order_by('-scan_time')[:10]  # Get 10 latest records
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
                
                # DELETE ALL OLD DATA IN BigramData BEFORE IMPORT
                old_count = BigramData.objects.count()
                BigramData.objects.all().delete()
                print(f"== Deleted {old_count} old BigramData records")
                
                # Read file content directly from memory (don't save file)
                try:
                    if dataset_file.name.endswith('.csv'):
                        # Read CSV from memory
                        file_content = dataset_file.read().decode('utf-8')
                        csv_reader = csv.DictReader(io.StringIO(file_content))
                        
                        print(f"== Column names: {csv_reader.fieldnames}")
                        
                        # Reset reader to read all data
                        csv_reader = csv.DictReader(io.StringIO(file_content))
                        
                        total_rows = 0
                        print("== Processing all rows:")
                        for i, row in enumerate(csv_reader):
                            html_content = row.get('HTML', row.get('html', ''))
                            label_content = row.get('label', row.get('Label', ''))
                            
                            # Only process when label = 0
                            if label_content == '0':
                                # Create bigrams from HTML content
                                bigram_counts = create_bigrams(html_content)
                                
                                # Save bigrams to database - CREATE 1 RECORD PER ROW
                                save_bigrams_to_db(bigram_counts, label_content)
                            
                            total_rows += 1
                            if i < 5:  # Print details for first 5 rows
                                print(f"Row {i + 1}:")
                                print(f"  HTML: {html_content[:100]}...")
                                print(f"  Label: {label_content}")
                                print(f"  Total bigrams: {len(bigram_counts)}")
                                print(f"  Top 5 bigrams:")
                                for bigram, count in list(bigram_counts.most_common(5)):
                                    print(f"    '{bigram}': {count}")
                                print("---")
                        
                        print(f"== Processed {total_rows} rows total")
                    
                    # Read text/json file from memory
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
