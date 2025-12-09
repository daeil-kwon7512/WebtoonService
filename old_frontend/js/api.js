// js/api.js

const API_BASE = 'http://127.0.0.1:8000/api';

// 1) csrftoken 쿠키 읽기
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

// 2) 공통 API 호출 함수
async function apiCall(path, options = {}) {
    const csrftoken = getCookie('csrftoken');

    const baseHeaders = {
        'Content-Type': 'application/json',
    };

    // POST/PUT/PATCH/DELETE 같은 변경 요청에만 CSRF 헤더 추가
    const method = (options.method || 'GET').toUpperCase();
    if (['POST', 'PUT', 'PATCH', 'DELETE'].includes(method)) {
        baseHeaders['X-CSRFToken'] = csrftoken || '';
    }

    const mergedHeaders = {
        ...baseHeaders,
        ...(options.headers || {}),
    };

    const res = await fetch(`${API_BASE}${path}`, {
        credentials: 'include',
        ...options,
        headers: mergedHeaders,
    });

    if (!res.ok) {
        const text = await res.text();
        throw new Error(`API ${res.status}: ${text}`);
    }
    return res.json();
}

// 3) 실제 API 래퍼들
const Api = {
    signup: (data) => apiCall('/accounts/signup/', {
        method: 'POST',
        body: JSON.stringify(data),
    }),
    login: (data) => apiCall('/accounts/login/', {
        method: 'POST',
        body: JSON.stringify(data),
    }),
    logout: () => apiCall('/accounts/logout/', { method: 'POST' }),
    me: () => apiCall('/accounts/me/'),

    getWebtoons: (params = {}) => {
        const query = new URLSearchParams(params).toString();
        return apiCall(`/webtoons/${query ? '?' + query : ''}`);
    },
    toggleFavorite: (id) =>
        apiCall(`/webtoons/${id}/favorite/`, { method: 'POST' }),
    myFavorites: (params = {}) => {
        const query = new URLSearchParams(params).toString();
        return apiCall(`/me/favorites/${query ? '?' + query : ''}`);
    },
};
