// src/stores/auth.js
import { defineStore } from 'pinia';
import axios from '@/api/axios'; // 방금 만든 axios 인스턴스 import

// axios 헤더에 토큰 심어주는 함수
function setAuthHeader(token) {
  if (token) {
    axios.defaults.headers.common.Authorization = `Bearer ${token}`
  } else {
    delete axios.defaults.headers.common.Authorization
  }
}

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null,          // 유저 정보 (username, email 등)
    isAuthenticated: false,
    loading: false,
    error: null,
  }),

  actions: {
    // 1. 로그인
    async login(username, password) {
      this.loading = true;
      this.error = null;
      try {
        const response = await axios.post('/api/accounts/login/', {
          username,
          password,
        });

        // 토큰 저장 (Access, Refresh)
        const { access, refresh } = response.data;
        localStorage.setItem('accessToken', access);
        localStorage.setItem('refreshToken', refresh);

        setAuthHeader(access)
        this.isAuthenticated = true;
        
        // 로그인 성공 후 내 정보 가져오기
        await this.fetchUser();
        return true; // 성공 반환
      } catch (err) {
        this.error = '로그인 실패: 아이디나 비밀번호를 확인하세요.';
        console.error(err);
        return false;
      } finally {
        this.loading = false;
      }
    },

    // 2. 내 정보 가져오기 (새로고침 시 상태 복구용)
    async fetchUser() {
      try {
        const response = await axios.get('/api/accounts/me/');
        this.user = response.data;
        this.isAuthenticated = true;
      } catch (err) {
        this.user = null;
        this.isAuthenticated = false;
        // 토큰이 유효하지 않으면 로그아웃 처리
        // this.logout(); 
      }
    },

    // 3. 회원가입 (+자동 로그인 처리)
    async register(userData) {
      this.loading = true;
      this.error = null;
      try {
        // 1. API 요청
        const response = await axios.post('/api/accounts/signup/', userData);
        
        // 2. [수정됨] 응답으로 온 토큰 저장 (자동 로그인)
        const { access, refresh, user } = response.data;
        
        localStorage.setItem('accessToken', access);
        localStorage.setItem('refreshToken', refresh);

        // 3. 상태 업데이트
        this.user = user;
        this.isAuthenticated = true;
        
        return true; // 성공
      } catch (err) {
        this.error = err.response?.data || '회원가입 실패';
        console.error(err);
        return false;
      } finally {
        this.loading = false;
      }
    },

    // [추가] 설문조사 완료 처리 (상태 업데이트)
    async completeSurvey() {
        if (this.user) {
            this.user.onboarding_completed = true;
        }
        // 필요하다면 다시 fetchUser()를 불러서 확실하게 서버 동기화
        await this.fetchUser();
    },

    // 4. 로그아웃
    async logout() {
      try {
        const refresh = localStorage.getItem('refreshToken');
        if (refresh) {
          // 서버 블랙리스트에 추가 (선택 사항이지만 보안상 권장)
          await axios.post('/api/accounts/logout/', { refresh });
        }
      } catch (err) {
        console.warn('로그아웃 처리 중 에러 무시', err);
      } finally {
        // 클라이언트 상태 초기화
        this.user = null;
        this.isAuthenticated = false;
        localStorage.removeItem('accessToken');
        localStorage.removeItem('refreshToken');
        setAuthHeader(null);
      }
    },
    
    // 5. 앱 시작 시 토큰 체크 (App.vue에서 호출)
    async initializeAuth() {
      const token = localStorage.getItem('accessToken')
      if (!token) {
        this.user = null
        this.isAuthenticated = false
        setAuthHeader(null)
        return
      }

      // 토큰만 있으면 우선 로그인 상태로 본다
      setAuthHeader(token)
      this.isAuthenticated = true

      try {
        const res = await axios.get('/accounts/me/')
        this.user = res.data
      } catch (err) {
        // 토큰이 진짜로 잘못됐을 때만 로그아웃
        this.user = null
        this.isAuthenticated = false
        this.logout()
      }
    },
  },
});
