from django.db import models

# Create your models here.
class WebsiteHTML(models.Model):
    id = models.AutoField(primary_key=True)  # Tự tăng ID
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
    status = models.CharField(max_length=50)
    method = models.CharField(max_length=100)
    meta = models.TextField(blank=True, null=True)  # Thêm column meta
    scan_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Scan of {self.app_name} at {self.scan_time}"

class BigramData(models.Model):
    id = models.AutoField(primary_key=True)
    bigram_json = models.JSONField()  # Lưu bigrams và tần suất dưới dạng JSON
    label = models.CharField(max_length=50)  # normal/defaced
    total_bigrams = models.IntegerField(default=0)  # Tổng số bigrams
    created_date = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Bigrams ({self.label}): {self.total_bigrams} bigrams"
