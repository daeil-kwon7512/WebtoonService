import pandas as pd
import joblib
from sklearn.feature_extraction.text import CountVectorizer

def build_model():
    print("=== 데이터 로딩 중 ===")
    try:
        df_webtoon = pd.read_csv("data_webtoon.csv")
        df_author = pd.read_csv("data_author.csv")
        df_genre = pd.read_csv("data_genre.csv")
        df_tag = pd.read_csv("data_tag.csv")
    except FileNotFoundError:
        print("CSV 파일이 없습니다. 01_crawler.py를 먼저 실행하세요.")
        return

    # 1. 데이터 전처리 (Soup 만들기)
    print("=== 특징(Soup) 생성 중 ===")
    
    # 각 정보를 문자열로 합치기
    # titleId를 인덱스로 설정하면 매핑하기 편함
    
    # 장르: 중요하니까 2번 반복
    s_genre = df_genre.groupby('titleId')['genre'].apply(lambda x: " ".join(x) + " " + " ".join(x))
    
    # 태그
    s_tag = df_tag.groupby('titleId')['tag'].apply(lambda x: " ".join(x))
    
    # 작가
    s_author = df_author.groupby('titleId')['authorName'].apply(lambda x: " ".join(x))

    # 메인 데이터프레임에 합치기
    df_main = df_webtoon.set_index('titleId')
    df_main['soup'] = (s_genre.fillna('') + " " + 
                       s_tag.fillna('') + " " + 
                       s_author.fillna(''))
    
    # NaN 값이나 빈 데이터 처리
    df_main = df_main[df_main['soup'].str.strip() != '']
    
    print(f"학습 데이터 준비 완료: {len(df_main)}개")

    # 2. 벡터화 (CountVectorizer)
    print("=== 벡터화 진행 중 ===")
    vectorizer = CountVectorizer(min_df=1)
    count_matrix = vectorizer.fit_transform(df_main['soup'])
    
    # 3. 모델 파일로 저장
    # 나중에 추천할 때 필요한 모든 것을 딕셔너리로 묶어서 저장
    model_data = {
        'vectorizer': vectorizer,      # 사용자 입력 변환용
        'matrix': count_matrix,        # 미리 계산된 웹툰 벡터
        'df': df_main[['titleName', 'thumbnailUrl', 'soup']].reset_index() # 결과 출력용 메타데이터
    }
    
    joblib.dump(model_data, 'webtoon_recommender.pkl')
    print("✅ 모델 생성 완료: webtoon_recommender.pkl")

if __name__ == "__main__":
    build_model()