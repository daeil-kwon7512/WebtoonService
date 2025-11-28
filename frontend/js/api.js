const API_BASE = 'http://127.0.0.1:8000/api';

// CSRF 토큰 가져오기
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// API 호출 공통 함수
async function apiCall(endpoint, options = {}) {
    const url = `${API_BASE}${endpoint}`;
    const defaultOptions = {
        credentials: 'include',  // 쿠키 포함
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken'),
        },
    };

    const mergedOptions = {
        ...defaultOptions,
        ...options,
        headers: {
            ...defaultOptions.headers,
            ...options.headers,
        },
    };

    if (mergedOptions.body && typeof mergedOptions.body === 'object') {
        mergedOptions.body = JSON.stringify(mergedOptions.body);
    }

    const response = await fetch(url, mergedOptions);
    const data = await response.json();

    if (!response.ok) {
        throw { status: response.status, data };
    }

    return data;
}

// API 함수들
const api = {
    // 인증
    signup: (userData) => apiCall('/accounts/signup/', { method: 'POST', body: userData }),
    login: (credentials) => apiCall('/accounts/login/', { method: 'POST', body: credentials }),
    logout: () => apiCall('/accounts/logout/', { method: 'POST' }),
    getMe: () => apiCall('/accounts/me/'),

    // 웹툰
    getWebtoons: (params = {}) => {
        const query = new URLSearchParams(params).toString();
        return apiCall(`/webtoons/${query ? '?' + query : ''}`);
    },
    getWebtoon: (id) => apiCall(`/webtoons/${id}/`),
    toggleFavorite: (id) => apiCall(`/webtoons/${id}/favorite/`, { method: 'POST' }),

    // 마이페이지
    getMyFavorites: (params = {}) => {
        const query = new URLSearchParams(params).toString();
        return apiCall(`/me/favorites/${query ? '?' + query : ''}`);
    },
};
