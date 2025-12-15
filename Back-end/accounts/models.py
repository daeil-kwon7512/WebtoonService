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

    # [Sub에서 병합] 나이 기반 추천을 위해 출생년도 추가
    birth_year = models.IntegerField(
        null=True, 
        blank=True, 
        verbose_name='출생년도'
    )
    
    # [추가] 설문 4단계: 주 사용 플랫폼
    main_platform = models.CharField(
        max_length=50, 
        null=True, 
        blank=True, 
        verbose_name='주 사용 플랫폼'
    )

    # [Main 유지] 회원가입 후 첫 설문조사를 완료했는지 체크하는 필드 (is_survey_completed 역할)
    onboarding_completed = models.BooleanField(
        default=False, 
        verbose_name='온보딩 완료 여부'
    )

    def __str__(self):
        return self.username


# --------------------------------------------------------------------------
# 설문조사 데이터 저장용 모델 (Webtoon 도메인으로 변경)
# --------------------------------------------------------------------------

class UserGenrePreference(models.Model):
    """
    1단계: 유저가 선호하는 웹툰 장르 저장
    (예: 로맨스, 무협, 판타지, 일상 등)
    """
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='genre_preferences')
    
    # 웹툰 장르는 보통 텍스트로 관리하거나 별도 Genre 모델이 있을 수 있습니다.
    # 여기서는 범용성을 위해 문자열로 처리하거나, 장르 모델의 PK를 저장합니다.
    genre_name = models.CharField(
        max_length=50, 
        verbose_name='선호 장르명', 
        null=True,   # DB에 NULL 저장 허용
        blank=True   # 폼 유효성 검사에서 빈 값 허용
    )
    # 만약 Genre 모델이 있다면: genre = models.ForeignKey('webtoons.Genre', ...)
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - Genre: {self.genre_name}"


class UserWebtoonRating(models.Model):
    """
    2단계: 유저가 평가한 웹툰 데이터 저장 (Taste.io 스타일)
    영화(Movie) -> 웹툰(Webtoon)으로 변경
    """
    # [수정] 사용자 흐름에 맞춘 4단계 평가 + '보지 않음'
    RATING_CHOICES = [
        ('BEST', '최고'),      # 5점
        ('GOOD', '좋음'),      # 4점
        ('BAD', '나쁨'),       # 2점
        ('WORST', '최악'),     # 1점
        ('WATCHED', '봤어요'),  # 점수 없음 (혹은 보지 않음으로 처리)
    ]

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='webtoon_ratings')
    
    # 실제 웹툰 모델의 PK를 저장 (또는 웹툰 ID)
    # webtoons 앱의 Webtoon 모델을 참조하는 것이 Best입니다.
    # 예: webtoon = models.ForeignKey('webtoons.Webtoon', on_delete=models.CASCADE)
    webtoon_id = models.CharField(max_length=100, verbose_name='웹툰 ID') 
    
    rating = models.CharField(max_length=10, choices=RATING_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # 한 유저가 같은 웹툰을 중복 평가하지 못하도록 제한
        unique_together = ('user', 'webtoon_id')
        verbose_name = '유저 웹툰 평가'
        verbose_name_plural = '유저 웹툰 평가 목록'

    def __str__(self):
        return f"{self.user.username} - Webtoon {self.webtoon_id}: {self.rating}"
