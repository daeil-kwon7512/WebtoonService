from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.db import transaction
from .models import UserGenrePreference, UserWebtoonRating

User = get_user_model()

# ------------------------------------------------------------------
# 1. 회원가입 및 유저 정보용 Serializer (기존 코드 통합)
# ------------------------------------------------------------------
class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password', 'gender', 'birth_year', 'onboarding_completed')
        read_only_fields = ('id', 'onboarding_completed') # 이 필드들은 직접 수정 불가
    
    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            gender=validated_data.get('gender', ''),
            birth_year=validated_data.get('birth_year', None)
        )
        return user


# ------------------------------------------------------------------
# 2. 설문조사 결과 저장용 Serializer (신규 추가)
# ------------------------------------------------------------------
class SurveyInputSerializer(serializers.Serializer):
    # 1. 인적 사항 업데이트용
    gender = serializers.ChoiceField(choices=['M', 'F'], required=False)
    birth_year = serializers.IntegerField(required=False)
    
    # 2. 선호 장르 (예: ['로맨스', '판타지'])
    preferred_genres = serializers.ListField(
        child=serializers.CharField(max_length=50)
    )
    
    # 3. 웹툰 평가 (예: [{'webtoon_id': 1, 'rating': 'LIKE'}, ...])
    webtoon_ratings = serializers.ListField(
        child=serializers.DictField()
    )

    def save(self, user):
        """
        검증된 데이터를 받아 User 정보 업데이트 및 취향 데이터 저장
        """
        validated_data = self.validated_data
        
        with transaction.atomic():
            # (1) 유저 추가 정보 업데이트 (입력된 경우만)
            if 'gender' in validated_data:
                user.gender = validated_data['gender']
            if 'birth_year' in validated_data:
                user.birth_year = validated_data['birth_year']
            
            user.onboarding_completed = True # 설문 완료 마킹
            user.save()
            
            # (2) 선호 장르 저장
            genres_list = validated_data.get('preferred_genres', [])
            # 기존 데이터 초기화 (재설문 시)
            UserGenrePreference.objects.filter(user=user).delete()
            
            UserGenrePreference.objects.bulk_create([
                UserGenrePreference(user=user, genre_name=g_name) 
                for g_name in genres_list
            ])

            # (3) 웹툰 평가 저장
            ratings_data = validated_data.get('webtoon_ratings', [])
            UserWebtoonRating.objects.filter(user=user).delete()

            UserWebtoonRating.objects.bulk_create([
                UserWebtoonRating(
                    user=user,
                    webtoon_id=str(item['id']), # 프론트에서 넘어오는 id
                    rating=item['rating']       # LIKE, DISLIKE 등
                ) for item in ratings_data
            ])
            
        return user


# 3. 로그인용
class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
