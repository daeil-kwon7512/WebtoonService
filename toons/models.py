from django.db import models
from django.conf import settings

# Create your models here.
class Webtoon(models.Model):
    provider = models.CharField(max_length=15)
    title = models.CharField(max_length=255)
    authors = models.CharField(max_length=255)
    update_days = models.CharField(max_length=50)
    thumbnail = models.URLField()
    url = models.URLField()
    is_end = models.BooleanField(default=False)

    # ManyToMany로 즐겨찾기 관계 설정
    favorited_by = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='favorite_webtoons',
        blank=True
    )
    
    def __str__(self):
        return self.title