import requests
import os

# HTML에서 찾은 파비콘 URL
favicon_dict = {
    "NAVER": {
        "FAVICON_URL": "https://shared-comic.pstatic.net/favicon/favicon_96x96.ico",
        "SAVE_FILENAME": "naver_webtoon_favicon.ico"
    },
    "KAKAO":{
        "FAVICON_URL": "https://webtoon.kakao.com/ico/icon192_210521.png",
        "SAVE_FILENAME": "kakao_webtoon_favicon.ico"   
    },
    "KAKAOPAGE":{
        "FAVICON_URL": "https://page.kakaocdn.net/pageweb/resources/favicon/ico_web_square_192.png",
        "SAVE_FILENAME": "kpage_webtoon_favicon.ico"   
    },
}

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

def download_specific_favicon(url, save_path):
    print(f"파비콘 다운로드 시도: {url}")
    
    try:
        # HTTP GET 요청을 보내 이미지 데이터를 가져옵니다.
        response = requests.get(url, headers=HEADERS, timeout=5)
        response.raise_for_status() # 4xx, 5xx 에러 발생 시 예외 처리

        # 응답이 성공적이면 파일로 저장합니다.
        if response.status_code == 200 and 'image' in response.headers.get('Content-Type', ''):
            with open(save_path, 'wb') as f:
                f.write(response.content)
            print(f"다운로드 성공: {os.path.abspath(save_path)}")
            return True
        else:
            print(f"다운로드 실패: HTTP 상태 코드 {response.status_code} 또는 파일 형식이 이미지가 아님.")
            return False

    except requests.exceptions.RequestException as e:
        print(f"요청 중 오류 발생: {e}")
        return False

for provider_info in favicon_dict.values():
    download_specific_favicon(
        provider_info.get("FAVICON_URL"), 
        provider_info.get("SAVE_FILENAME")
    )