import json
from django.core.management.base import BaseCommand
from toons.models import Webtoon, Genre
from django.db import transaction, IntegrityError
import os

class Command(BaseCommand):
    help = 'JSON 파일에서 웹툰 데이터를 불러와 DB에 저장하거나 업데이트합니다.'

    def add_arguments(self, parser):
        # 실행할 때 JSON 파일 경로를 인자로 받습니다.
        parser.add_argument('json_filename', type=str, help='로드할 JSON 파일 경로')

    def handle(self, *args, **options):
        json_filename = options['json_filename']
        json_file_path = os.path.join('crawling', json_filename)
        # 1. JSON 파일 로드
        try:
            with open(json_file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except FileNotFoundError:
            self.stderr.write(self.style.ERROR(f"❌ 파일을 찾을 수 없습니다: {os.path.abspath(json_file_path)}"))
            return
        except json.JSONDecodeError:
            self.stderr.write(self.style.ERROR(f"❌ JSON 파일 디코딩 오류: {json_file_path}"))
            return

        total_count = len(data)
        self.stdout.write(self.style.SUCCESS(f"--- 총 {total_count}개의 웹툰 데이터 로드 시작 ---"))

        # 대량의 데이터를 안전하고 빠르게 처리하기 위해 트랜잭션을 사용합니다.
        with transaction.atomic():
            created_count = 0
            updated_count = 0
            
            for item in data:
                try:
                    # 🚨 필수 매핑: JSON 키를 DB 모델 필드에 맞춰 정리
                    
                    cleaned_title = item['titleName'].strip()
                
                    # 1. 🚨 고유성 검색 조건: title 필드 하나만 사용
                    lookup_kwargs = {
                        'title': cleaned_title, 
                    }
                    
                    # 2. DB에 저장할 기본 값 및 업데이트 필드 정의
                    defaults_values = {
                        # JSON 필드 -> DB 필드 매핑
                        'provider': item.get('provider', ''),
                        'writers': item.get('Writer', ''),
                        'painters': item.get('Painter', ''),
                        'original_author': item.get('Original', ''), # 👈 여기서 .get() 사용
                        'update_days': item.get('day', ''),
                        'thumbnail': item.get('thumbnailUrl', ''), 
                        'url': item.get('Url', ''),
                        'is_adult': item.get('is_adult', False), # 불리언 기본값은 False
                        'synopsis': item.get('synopsis', ''),
                        'is_up': item.get('is_up', False),
                    }

                    # 3. DB 저장 또는 업데이트 (platform_id를 기준으로 체크)
                    webtoon, created = Webtoon.objects.update_or_create(
                        **lookup_kwargs,
                        defaults=defaults_values
                    )
                    genre_text = item.get('genre', '')
                    if genre_text:
                        names = [g.strip() for g in str(genre_text).split(',') if g.strip()]
                        for name in names:
                            genre_obj, _ = Genre.objects.get_or_create(tag=name)
                            webtoon.genres.add(genre_obj)

                    if created:
                        created_count += 1
                    else:
                        updated_count += 1
                        
                # except IntegrityError as e:
                #     self.stderr.write(self.style.WARNING(f"⚠️ 무결성 오류 발생 - ID: {lookup_kwargs}. {e}"))
                except KeyError as e:
                    self.stderr.write(self.style.ERROR(f"❌ 필수 JSON 키 누락: {e}. 해당 항목 무시."))
                except Exception as e:
                    self.stderr.write(self.style.ERROR(f"🚨 예상치 못한 오류 발생: {e}"))
            
            # 최종 결과 보고
            self.stdout.write(self.style.SUCCESS(f"\n✅ 데이터 로딩 완료:"))
            self.stdout.write(self.style.SUCCESS(f"  - 총 처리 항목: {total_count}개"))
            self.stdout.write(self.style.SUCCESS(f"  - 새로 생성된 웹툰: {created_count}개"))
            self.stdout.write(self.style.SUCCESS(f"  - 업데이트된 웹툰: {updated_count}개"))