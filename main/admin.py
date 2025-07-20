from django.contrib import admin
from .models import HistoryScan, WebsiteHTML, BigramData

@admin.register(WebsiteHTML)
class WebsiteHTMLAdmin(admin.ModelAdmin):
    list_display = ('id','app_name', 'app_url','app_created_date')
    readonly_fields = ('app_created_date',) 

@admin.register(HistoryScan)
class HistoryScanAdmin(admin.ModelAdmin):
    list_display = ('id', 'app_id', 'app_name', 'app_url', 'status', 'method', 'scan_time')
    readonly_fields = ('scan_time',)
    search_fields = ('app_name', 'app_url')
    list_filter = ('status', 'method', 'scan_time')

@admin.register(BigramData)
class BigramDataAdmin(admin.ModelAdmin):
    list_display = ('id', 'label', 'total_bigrams', 'created_date')
    readonly_fields = ('created_date',)
    list_filter = ('label', 'created_date')
    search_fields = ('label',)