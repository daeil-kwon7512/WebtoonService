from rest_framework import serializers
from .models import Webtoon, SurveyCandidateWebtoon


class WebtoonSerializer(serializers.ModelSerializer):
    is_favorited = serializers.SerializerMethodField()

    class Meta:
        model = Webtoon
        fields = [
            'id',
            'provider',
            'title',
            'writers',       # authors 대신 모델 필드명에 맞게
            'update_days',
            'thumbnail',
            'url',
            'is_adult',      # is_end → is_adult 로 교체
            'is_favorited',
        ]

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.favorited_by.filter(id=request.user.id).exists()
        return False

# 설문조사용 웹툰 조회 Serializer
class SurveyCandidateSerializer(serializers.ModelSerializer):
    class Meta:
        model = SurveyCandidateWebtoon
        fields = ['id', 'title', 'thumbnail_url', 'genre']
