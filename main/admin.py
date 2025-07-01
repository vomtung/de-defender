from django.contrib import admin
from .models import WebsiteHTML

@admin.register(WebsiteHTML)
class WebsiteHTMLAdmin(admin.ModelAdmin):
    list_display = ('app_name', 'app_url', 'html_content','app_created_date')
    readonly_fields = ('app_created_date',) 
