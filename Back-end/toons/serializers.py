from rest_framework import serializers
from .models import Webtoon, SurveyCandidateWebtoon


class WebtoonSerializer(serializers.ModelSerializer):
    is_favorited = serializers.SerializerMethodField()
    authors_display = serializers.SerializerMethodField()

    class Meta:
        model = Webtoon
        fields = [
            'id',
            'provider',
            'title',
            'update_days',
            'thumbnail',
            'url',
            'is_adult',
            'is_up',
            'is_favorited',
            'authors_display', # 아래 규칙에 따라 작가 표시
        ]

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.favorited_by.filter(id=request.user.id).exists()
        return False

    def get_authors_display(self, obj):
        def split_names(text):
            if not text:
                return []
            return [name.strip() for name in text.split(',') if name.strip()]

        writer_names = split_names(obj.writers)
        painter_names = split_names(obj.painters)
        original_names = split_names(obj.original_author)

        parts = []

        # 글/그림이 완전히 동일하면 한 번만
        if set(writer_names) == set(painter_names):
            if writer_names:
                parts.append(', '.join(writer_names))
        else:
            if writer_names:
                parts.append(', '.join(writer_names))
            if painter_names:
                parts.append(', '.join(painter_names))

        # 원작은 있으면만 추가
        if original_names:
            parts.append(', '.join(original_names))

        return ' / '.join(parts)  
      
      
# 설문조사용 웹툰 조회 Serializer
class SurveyCandidateSerializer(serializers.ModelSerializer):
    class Meta:
        model = SurveyCandidateWebtoon
        fields = ['id', 'title', 'thumbnail_url', 'genre']

# 웹툰 상세페이지용 정보조회 Serializer
class WebtoonDetailSerializer(WebtoonSerializer):
    # 장르(태그)를 문자열 리스트로 가져오기 (예: ["판타지", "무협"])
    genres = serializers.StringRelatedField(many=True)

    class Meta(WebtoonSerializer.Meta):
        fields = WebtoonSerializer.Meta.fields + ['synopsis', 'genres']
