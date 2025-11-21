from django.db import models

# Create your models here.
class Webtoon(models.Model):
    provider = models.CharField(max_length=15)
    title = models.CharField(max_length=255)
    authors = models.CharField(max_length=255)
    update_days = models.CharField(max_length=50)
    thumbnail = models.URLField()
    url = models.URLField()
    is_end = models.BooleanField(default=False)