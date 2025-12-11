from django.db import models
from django.conf import settings

# Create your models here.
class Genre(models.Model):
    tag = models.CharField(max_length=50, unique=True, db_index=True)

    def __str__(self):
        return self.tag
    
class Webtoon(models.Model):
    provider = models.CharField(max_length=15)
    title = models.CharField(max_length=255)
    writers = models.CharField(max_length=255)
    painters = models.CharField(max_length=255)
    original_author = models.CharField(max_length=255, blank=True)
    update_days = models.CharField(max_length=50)
    thumbnail = models.URLField()
    url = models.URLField()
    is_adult = models.BooleanField(default=False)
    synopsis = models.TextField()
    genres = models.ManyToManyField(Genre, related_name='webtoons', blank=True)

    # ManyToMany로 즐겨찾기 관계 설정
    favorited_by = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='favorite_webtoons',
        blank=True
    )
    
    def __str__(self):
        return self.title
    