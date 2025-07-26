from django.contrib import admin
from .models import HistoryScan, WebsiteHTML, BigramData, ApplicationSetting

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

@admin.register(ApplicationSetting)
class ApplicationSettingAdmin(admin.ModelAdmin):
    list_display = ('id', 'parameter_key', 'parameter_value_short', 'created_date', 'updated_date')
    readonly_fields = ('created_date', 'updated_date')
    search_fields = ('parameter_key', 'parameter_value')
    list_filter = ('created_date', 'updated_date')
    
    def parameter_value_short(self, obj):
        """Hiển thị parameter_value ngắn gọn trong list view"""
        return obj.parameter_value[:50] + '...' if len(obj.parameter_value) > 50 else obj.parameter_value
    parameter_value_short.short_description = 'Parameter Value'
    search_fields = ('label',)