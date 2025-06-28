from django.shortcuts import render, redirect
import requests
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
