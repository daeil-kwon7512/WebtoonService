// src/api/axios.js
import axios from 'axios';

// Django 서버 주소
const instance = axios.create({
  baseURL: 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json',
  },
});

// [요청 인터셉터] 모든 요청 헤더에 Access Token 추가
instance.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('accessToken');
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// [응답 인터셉터] 401 에러(토큰 만료) 시 자동 갱신 로직
instance.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    // 401 에러이고, 아직 재시도를 안 했다면
    if (error.response.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      const refreshToken = localStorage.getItem('refreshToken');

      if (refreshToken) {
        try {
          // 토큰 갱신 요청
          const { data } = await axios.post('http://localhost:8000/api/accounts/token/refresh/', {
            refresh: refreshToken,
          });

          // 새 토큰 저장 및 헤더 설정
          localStorage.setItem('accessToken', data.access);
          originalRequest.headers['Authorization'] = `Bearer ${data.access}`;
          
          // 원래 요청 다시 시도
          return instance(originalRequest);
        } catch (refreshError) {
          // 갱신 실패 시 로그아웃 처리
          console.error('Refresh token expired');
          localStorage.removeItem('accessToken');
          localStorage.removeItem('refreshToken');
          window.location.href = '/login'; // 로그인 페이지로 리다이렉트
          return Promise.reject(refreshError);
        }
      }
    }
    return Promise.reject(error);
  }
);

export default instance;
