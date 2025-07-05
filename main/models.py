from django.db import models

# Create your models here.
class WebsiteHTML(models.Model):
    app_name  = models.CharField(max_length=255)
    app_url = models.URLField(max_length=500)
    html_content = models.TextField()
    app_created_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.app_name

class HistoryScan(models.Model):
    id = models.AutoField(primary_key=True)  # Tự tăng ID
    app_id = models.IntegerField()
    app_name = models.CharField(max_length=255)
    app_url = models.URLField(max_length=500)
    result = models.TextField()
    scan_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Scan of {self.app_name} at {self.scan_time}"
