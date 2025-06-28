from django.db import models

# Create your models here.
class WebsiteHTML(models.Model):
    APP_NAME = models.CharField(max_length=255)
    APP_URL = models.URLField(max_length=500)
    HTML_CONTENT = models.TextField()

    def __str__(self):
        return self.APP_NAME
