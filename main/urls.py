from django.contrib import admin
from django.urls import path
from .views import chart_data
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('django-defender/', views.index, name='index'),
    path('search/', views.search, name='search'),
    path('save_website_html/', views.save_website_html, name='save_website_html'),
    path('api/chart-data/', chart_data, name='chart-data'),
]
