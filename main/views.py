from django.shortcuts import render, redirect
import requests
from django.http import JsonResponse
from .models import HistoryScan, WebsiteHTML
import logging
import csv
import io

logger = logging.getLogger(__name__)

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
