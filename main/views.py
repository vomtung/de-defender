from django.shortcuts import render, redirect
import requests
from django.http import JsonResponse
from .models import HistoryScan, WebsiteHTML
import logging

logger = logging.getLogger(__name__)

def index(request):
    history_list = HistoryScan.objects.order_by('-scan_time')[:10]  # Lấy 10 bản ghi mới nhất
    return render(request, 'index.html', {'history_list': history_list})
    

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
    labels = ['January', 'February', 'March', 'April', 'May', 'June']
    data = [100, 200, 150, 300, 250, 400]
    return JsonResponse({
        'labels': labels,
        'data': data
    })
