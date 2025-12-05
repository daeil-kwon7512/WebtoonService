import joblib
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

class WebtoonRecommender:
    def __init__(self, model_path='webtoon_recommender.pkl'):
        print("시스템: 모델 파일을 로딩합니다...")
        try:
            data = joblib.load(model_path)
            self.vectorizer = data['vectorizer']
            self.matrix = data['matrix']
            self.df = data['df'] # titleId, titleName, thumbnailUrl 등이 들어있음
            print("시스템: 로딩 완료!")
        except FileNotFoundError:
            print("오류: 모델 파일이 없습니다. 02_model_builder.py를 실행하세요.")
            raise

    def recommend_by_input(self, genres='', tags='', top_n=10):
        """
        사용자가 입력한 장르/태그 기반 추천
        """
        # 1. 사용자 입력 벡터화
        # 콤마를 공백으로 변경하여 Soup 형식으로 만듦
        user_input = f"{genres.replace(',', ' ')} {tags.replace(',', ' ')}"
        user_vec = self.vectorizer.transform([user_input])
        
        # 2. 유사도 계산
        # user_vec(1개) vs matrix(전체 웹툰)
        sim_scores = cosine_similarity(user_vec, self.matrix).flatten()
        
        # 3. 정렬 및 Top N 추출
        # argsort는 오름차순이므로 뒤집어야 내림차순(유사도 높은 순)
        sorted_indices = sim_scores.argsort()[::-1]
        
        results = []
        for idx in sorted_indices[:top_n]:
            score = sim_scores[idx]
            if score == 0: continue # 유사도 0인 건 제외
            
            row = self.df.iloc[idx]
            results.append({
                'title': row['titleName'],
                'score': round(score * 100, 1),
                'thumbnail': row['thumbnailUrl']
            })
            
        return results

    def recommend_by_title(self, title_name, top_n=10):
        """
        특정 웹툰 제목을 넣으면 비슷한 웹툰 추천
        """
        # 해당 제목을 가진 웹툰 찾기
        target = self.df[self.df['titleName'] == title_name]
        
        if target.empty:
            return f"'{title_name}'을(를) 찾을 수 없습니다."
        
        # 해당 웹툰의 인덱스 가져오기
        target_idx = target.index[0]
        
        # 해당 웹툰 벡터와 전체 벡터 간 유사도 계산
        target_vec = self.matrix[target_idx]
        sim_scores = cosine_similarity(target_vec, self.matrix).flatten()
        
        # 정렬
        sorted_indices = sim_scores.argsort()[::-1]
        
        results = []
        # 0번은 자기 자신이므로 제외하고 1번부터 가져옴
        for idx in sorted_indices[1:top_n+1]:
            row = self.df.iloc[idx]
            results.append({
                'title': row['titleName'],
                'score': round(sim_scores[idx] * 100, 1)
            })
            
        return results

# === 실행 테스트 ===
if __name__ == "__main__":
    recommender = WebtoonRecommender()
    
    # 시나리오 1: 사용자가 "판타지, 먼치킨"을 좋아함
    print("\n[사용자 취향 기반 추천: 판타지, 먼치킨]")
    recs = recommender.recommend_by_input(genres="FANTASY", tags="먼치킨,성장물")
    for r in recs:
        print(f"- {r['title']} (일치도: {r['score']}%)")
        
    # 시나리오 2: '참교육'과 비슷한 웹툰 찾기
    print("\n[특정 웹툰 유사작: 환생천마]")
    recs_title = recommender.recommend_by_title("환생천마")
    if isinstance(recs_title, list):
        for r in recs_title:
            print(f"- {r['title']} (유사도: {r['score']}%)")
    else:
        print(recs_title)