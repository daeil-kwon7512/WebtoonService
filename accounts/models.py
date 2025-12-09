from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    GENDER_CHOICES = [
        ('M', '남성'),
        ('F', '여성'),
    ]
    
    gender = models.CharField(
        max_length=1,
        choices=GENDER_CHOICES,
        blank=True,
        null=True,
        verbose_name='성별'
    )

    # [추가됨] 회원가입 후 첫 설문조사를 완료했는지 체크하는 필드
    onboarding_completed = models.BooleanField(
        default=False, 
        verbose_name='온보딩 완료 여부'
    )

    def __str__(self):
        return self.username


# --------------------------------------------------------------------------
# [추가됨] Taste.io 스타일 설문조사 데이터 저장용 모델
# 유저가 선택한 데이터는 User 모델에 다 넣지 말고, 별도 테이블로 분리(1:N)해야 관리가 쉽습니다.
# --------------------------------------------------------------------------

class UserGenrePreference(models.Model):
    """
    1단계: 유저가 선호하는 장르 저장
    (예: 액션, 코미디, 로맨스 등)
    """
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='genre_preferences')
    tmdb_genre_id = models.IntegerField(verbose_name='TMDB 장르 ID') # TMDB API의 장르 ID 사용
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - Genre {self.tmdb_genre_id}"


class UserMovieRating(models.Model):
    """
    2단계: 유저가 평가한 영화 데이터 저장
    Taste 스타일은 5점 만점보다는 [좋아요/별로/봤어요] 같은 직관적인 평가를 주로 씁니다.
    """
    RATING_CHOICES = [
        ('LIKE', '좋아요'),       # 추천 가중치 높음
        ('DISLIKE', '별로예요'),   # 추천 필터링
        ('WATCHED', '봤어요'),     # 이미 봄 (평가는 보류)
    ]

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='movie_ratings')
    tmdb_movie_id = models.IntegerField(verbose_name='TMDB 영화 ID') # TMDB API의 영화 ID
    rating = models.CharField(max_length=10, choices=RATING_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # 한 유저가 같은 영화를 중복 평가하지 못하도록 제한
        unique_together = ('user', 'tmdb_movie_id')

    def __str__(self):
        return f"{self.user.username} - Movie {self.tmdb_movie_id}: {self.rating}"
