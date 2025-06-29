from django.db import models

# Create your models here.
class WebsiteHTML(models.Model):
    app_name  = models.CharField(max_length=255)
    app_url = models.URLField(max_length=500)
    html_content = models.TextField()

    def __str__(self):
        return self.app_name
