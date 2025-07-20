from django.shortcuts import render, redirect
import requests
from django.http import JsonResponse
from .models import HistoryScan, WebsiteHTML
import logging

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
                
                # Lưu file vào thư mục (có thể cần tạo thư mục trước)
                import os
                upload_dir = 'uploads/datasets'
                os.makedirs(upload_dir, exist_ok=True)
                
                file_path = os.path.join(upload_dir, dataset_file.name)
                with open(file_path, 'wb+') as destination:
                    for chunk in dataset_file.chunks():
                        destination.write(chunk)
                
                logger.info(f"Dataset uploaded successfully: {file_path}")
                # Có thể lưu thông tin vào database nếu cần
                
        except Exception as e:
            logger.exception(f"Error uploading dataset: {e}")
    
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
