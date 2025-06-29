from django.shortcuts import render, redirect
import requests
from django.http import JsonResponse
from .models import WebsiteHTML


def index(request):
    return render(request, 'index.html')
    

def search(request):
    return redirect('de-defender')

def save_website_html(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        html_content = response.text
        WebsiteHTML.objects.create(url=url, html=html_content)
        return True
    except Exception:
        return False
    
def chart_data(request):
    labels = ['January', 'February', 'March', 'April', 'May']
    data = [100, 200, 150, 300, 250]
    return JsonResponse({
        'labels': labels,
        'data': data
    })
