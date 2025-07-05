from django.contrib import admin
from .models import HistoryScan, WebsiteHTML

@admin.register(WebsiteHTML)
class WebsiteHTMLAdmin(admin.ModelAdmin):
    list_display = ('app_name', 'app_url','app_created_date')
    readonly_fields = ('app_created_date',) 

@admin.register(HistoryScan)
class HistoryScanAdmin(admin.ModelAdmin):
    list_display = ('id', 'app_id', 'app_name', 'app_url', 'scan_time')
    readonly_fields = ('scan_time',)
    search_fields = ('app_name', 'app_url')
    list_filter = ('scan_time',)