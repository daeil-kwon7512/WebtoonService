from django.core.management.base import BaseCommand
from toons.models import SurveyCandidateWebtoon

class Command(BaseCommand):
    help = '설문조사 후보 웹툰 데이터를 초기화하고 적재합니다.'

    def handle(self, *args, **options):
        # 기존 데이터 삭제 (중복 적재 방지)
        SurveyCandidateWebtoon.objects.all().delete()
        self.stdout.write(self.style.WARNING('기존 데이터를 삭제했습니다.'))

        # (제목, 썸네일, 장르) 튜플 리스트
        # 제공해주신 데이터에 제가 장르를 매핑해두었습니다.
        webtoon_data = [
            ("연애혁명", "https://image-comic.pstatic.net/webtoon/570503/thumbnail/thumbnail_IMAG21_7b907ee6-a61e-495b-9b8f-be2f0a4be44b.jpeg", "로맨스"),
("유미의 세포들", "https://image-comic.pstatic.net/webtoon/651673/thumbnail/thumbnail_IMAG21_fba9683b-260e-4a07-984c-deda6d87f62d.jpg", "코미디/일상"),
("작전명 순정", "https://image-comic.pstatic.net/webtoon/793275/thumbnail/thumbnail_IMAG21_30c77a8d-ada1-40f8-b87a-d02bb05e7e13.jpg", "로맨스"),
("김비서가 왜 그럴까", "https://page-images.kakaoentcdn.com/download/resource?kid=bwPNJO/hymrftXeP0/VoUKJWehublPKZhKgletTK&filename=o1/dims/resize/384", "로맨스"),

("재혼 황후", "https://image-comic.pstatic.net/webtoon/735661/thumbnail/thumbnail_IMAG21_2e35b4aa-4459-42fd-84a8-eae732910422.jpg", "로맨스 판타지"),
("이번 생은 가주가 되겠습니다", "https://page-images.kakaoentcdn.com/download/resource?kid=V4o12/hAJrKR6ZV1/Gc3NYLC0Kf0z5qXrkJGwEK&filename=o1/dims/resize/384", "로맨스 판타지"),
("황제의 외동딸", "https://page-images.kakaoentcdn.com/download/resource?kid=fhAOt/hzmU1ucGko/dLPMISpdwGGfXNoF44MIW0&filename=o1/dims/resize/384", "로맨스 판타지"),
("악역의 엔딩은 죽음뿐", "https://page-images.kakaoentcdn.com/download/resource?kid=gmlXN/dJMcaa4JYa5/S5i8SYnLKwPmS3hvWuGw01&filename=o1/dims/resize/384", "로맨스 판타지"),

("전지적 독자 시점", "https://image-comic.pstatic.net/webtoon/747269/thumbnail/thumbnail_IMAG21_aabd9952-ff45-47a2-a543-33f19a5c6708.jpg", "판타지/이세계"),
("신의 탑", "https://image-comic.pstatic.net/webtoon/183559/thumbnail/thumbnail_IMAG21_5f3fec31-5c95-4afe-a73f-3046288edb47.jpg", "판타지/이세계"),
("나혼자만 레벨업", "https://page-images.kakaoentcdn.com/download/resource?kid=Cf0LJ/hynaH4y8E5/l5Qk7VWfAsyYkE8yKmRFdk&filename=o1/dims/resize/384", "판타지/이세계"),
("호랑이형님", "https://image-comic.pstatic.net/webtoon/650305/thumbnail/thumbnail_IMAG21_9e070729-5990-4653-90dd-1158847c1c68.jpg", "판타지/이세계"),

("화산귀환", "https://image-comic.pstatic.net/webtoon/769209/thumbnail/thumbnail_IMAG21_3511dcdd-6e33-4171-8839-598d6d266215.jpg", "액션/무협"),
("외모지상주의", "https://image-comic.pstatic.net/webtoon/641253/thumbnail/thumbnail_IMAG21_01672165-03c8-44b1-ba0e-ef82c9cfcd10.jpg", "액션/무협"),
("고수", "https://image-comic.pstatic.net/webtoon/662774/thumbnail/thumbnail_IMAG21_3618421729916171318.jpg", "액션/무협"),
("입학용병", "https://image-comic.pstatic.net/webtoon/758150/thumbnail/thumbnail_IMAG21_4135492154714961716.jpg", "액션/무협"),
("캐슬", "https://image-comic.pstatic.net/webtoon/736744/thumbnail/thumbnail_IMAG21_3905519414961792355.jpg", "액션/무협"),
("아비무쌍", "https://page-images.kakaoentcdn.com/download/resource?kid=Orluf/hyoXHBV70H/jFRvngw7KH8Pu1NR79kfj1&filename=o1/dims/resize/384", "액션/무협"),

("기기괴괴", "https://image-comic.pstatic.net/webtoon/557672/thumbnail/thumbnail_IMAG21_7365744050293924710.jpg", "스릴러/미스터리"),
("타인은 지옥이다", "https://image-comic.pstatic.net/webtoon/708378/thumbnail/thumbnail_IMAG21_7076671461120030000.jpg", "스릴러/미스터리"),
("똑닮은 딸", "https://image-comic.pstatic.net/webtoon/774866/thumbnail/thumbnail_IMAG21_b03cd4bd-bc74-4469-a501-20896bcc887f.jpg", "스릴러/미스터리"),
("지금 우리 학교는", "https://image-comic.pstatic.net/webtoon/67235/thumbnail/thumbnail_IMAG21_3546924696990934585.jpg", "스릴러/미스터리"),
("프레너미", "https://page-images.kakaoentcdn.com/download/resource?kid=buWXpB/hzVqGqpU9N/pCKKZ75dPkAk0Sy1rO1fB1&filename=o1/dims/resize/384", "스릴러/미스터리"),

("이태원 클라쓰", "https://page-images.kakaoentcdn.com/download/resource?kid=dF8eNZ/hymrlHUrEF/n57ojYGHZZoPrQkr6bNtHK&filename=o1/dims/resize/384", "드라마/휴먼드라마"),
("미생", "https://page-images.kakaoentcdn.com/download/resource?kid=pL3IT/hzb7BsGPAL/PE53oeqaBKqws5WixJysok&filename=o1/dims/resize/384", "드라마/휴먼드라마"),
("안나라수마나라", "https://image-comic.pstatic.net/webtoon/179704/thumbnail/thumbnail_IMAG21_3486178852879937589.jpg", "드라마/휴먼드라마"),

("뷰티풀 군바리", "https://image-comic.pstatic.net/webtoon/648419/thumbnail/thumbnail_IMAG21_d9398229-cbfd-47dc-9208-0a6fb936f3a7.jpg", "코미디/일상"),
("마루는 강쥐", "https://image-comic.pstatic.net/webtoon/796152/thumbnail/thumbnail_IMAG21_26b9c1d8-ca2d-4fc7-87ea-a3334634236a.jpg", "코미디/일상"),
("마음의 소리", "https://image-comic.pstatic.net/webtoon/20853/thumbnail/thumbnail_IMAG21_a715d0bd-fe55-4658-a573-669e0c0261f6.jpg", "코미디/일상"),
("선천적 얼간이들", "https://image-comic.pstatic.net/webtoon/478261/thumbnail/thumbnail_IMAG21_7fbd8610-0a97-40e3-9c63-101ea07fc4b4.jpg", "코미디/일상"),
("무직백수 계백순", "https://image-comic.pstatic.net/webtoon/811721/thumbnail/thumbnail_IMAG21_e0ccaab6-9ad2-4926-983b-c6cbb2dfecd7.jpg", "코미디/일상"),

("데뷔 못 하면 죽는 병 걸림", "https://page-images.kakaoentcdn.com/download/resource?kid=yeB5K/hAJrctDJ2U/QwDko13v1oEUFu9F1IaPEk&filename=o1/dims/resize/384", "스포츠/직업"),
("가비지타임", "https://image-comic.pstatic.net/webtoon/703844/thumbnail/thumbnail_IMAG21_5ddcb40e-1f6a-40f3-b2c4-6cd9a7eee843.jpg", "스포츠/직업"),
("더 복서", "https://image-comic.pstatic.net/webtoon/736989/thumbnail/thumbnail_IMAG21_3618985590402593377.jpg", "스포츠/직업"),
("빌드업", "https://image-comic.pstatic.net/webtoon/750826/thumbnail/thumbnail_IMAG21_d7a15cf7-bee5-4fa9-93be-19a2d0d3d6f3.jpg", "스포츠/직업")

            ]

        # 데이터 적재
        candidates = [
            SurveyCandidateWebtoon(title=title, thumbnail_url=url, genre=genre)
            for title, url, genre in webtoon_data
        ]
        SurveyCandidateWebtoon.objects.bulk_create(candidates)

        self.stdout.write(self.style.SUCCESS(f'성공적으로 {len(candidates)}개의 웹툰 데이터를 저장했습니다.'))
