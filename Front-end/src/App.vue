<script setup>
import { ref, onMounted } from 'vue'

// --- [상태 관리 (State)] ---
const webtoons = ref([])
const loading = ref(false)
const isLoggedIn = ref(false)
const currentProvider = ref('NAVER')
const API_BASE = 'http://127.0.0.1:8000' // Django API 주소

// --- [유틸리티 함수] ---
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

// 공통 API 호출 함수
async function apiCall(path, options = {}) {
  const csrftoken = getCookie('csrftoken');
  const headers = {
    'Content-Type': 'application/json',
    ...(csrftoken && { 'X-CSRFToken': csrftoken }), // CSRF 토큰 자동 추가
    ...options.headers,
  };

  const res = await fetch(`${API_BASE}${path}`, {
    credentials: 'include', // 세션 쿠키 포함
    ...options,
    headers,
  });

  if (!res.ok) {
    if (res.status === 401 || res.status === 403) {
      throw new Error('AUTH_REQUIRED'); // 로그인 필요 에러 식별용
    }
    const text = await res.text();
    throw new Error(`API ${res.status}: ${text}`);
  }
  return res.json();
}

// --- [기능 로직 (Actions)] ---

// 1. 웹툰 목록 불러오기
async function loadWebtoons(provider) {
  currentProvider.value = provider;
  loading.value = true;
  webtoons.value = [];

  try {
    const query = new URLSearchParams({
      provider,
      page: 1,
      per_page: 100, // 한 번에 많이 가져오기
    }).toString();

    const data = await apiCall(`/api/webtoons/?${query}`);
    webtoons.value = data.results;
    console.log(`불러온 웹툰 개수: ${data.count}`);
  } catch (error) {
    console.error('웹툰 로드 실패:', error);
    alert('웹툰 정보를 가져오는 데 실패했습니다.');
  } finally {
    loading.value = false;
  }
}

// 2. 즐겨찾기 토글 (좋아요)
async function toggleFavorite(toon) {
  if (!isLoggedIn.value) {
    alert('로그인이 필요한 서비스입니다.');
    return;
  }

  // 낙관적 업데이트 (UI 먼저 변경)
  const previousState = toon.is_favorited;
  toon.is_favorited = !toon.is_favorited;

  try {
    await apiCall(`/api/webtoons/${toon.id}/favorite/`, { method: 'POST' });
    // 성공 시 아무것도 안 함 (이미 UI 바꿨으니까)
  } catch (error) {
    // 실패 시 롤백
    toon.is_favorited = previousState;
    if (error.message === 'AUTH_REQUIRED') {
      alert('로그인이 풀렸습니다. 다시 로그인해주세요.');
      isLoggedIn.value = false;
    } else {
      console.error('즐겨찾기 오류:', error);
      alert('오류가 발생했습니다.');
    }
  }
}

// 3. 로그인 상태 확인 (nav 업데이트)
async function checkAuthStatus() {
  try {
    // accounts URL은 별도이므로 API_BASE 변수 대신 전체 경로를 쓰거나
    // API_BASE가 '/api'라면 아래처럼 호출해야 합니다.
    await apiCall('/api/accounts/me/', { method: 'GET' });
    isLoggedIn.value = true;
  } catch (err) {
    isLoggedIn.value = false;
  }
}

// 4. 로그아웃 처리
async function handleLogout() {
  if (!confirm('정말 로그아웃 하시겠습니까?')) return;
  
  try {
    await apiCall('/api/accounts/logout/', { method: 'POST' });
    isLoggedIn.value = false;
    alert('로그아웃 되었습니다.');
    // 필요 시 페이지 새로고침: location.reload()
  } catch (err) {
    console.error('로그아웃 실패:', err);
  }
}

// --- [생명주기 훅 (Mounted)] ---
onMounted(() => {
  checkAuthStatus();      // 로그인 체크
  loadWebtoons('NAVER');  // 초기 데이터(네이버) 로드
});
</script>

<template>
  <div class="min-h-screen bg-background-light text-text-main font-sans selection:bg-primary/20 selection:text-primary pb-20">
    
    <!-- Navbar (Sticky) -->
    <header class="sticky top-0 z-50 w-full bg-white/90 backdrop-blur-md border-b border-gray-100 shadow-sm transition-all duration-300">
      <div class="max-w-[1200px] mx-auto px-6 h-16 flex items-center justify-between">
        <!-- Logo -->
        <a href="#" class="flex items-center gap-2 group" @click.prevent="loadWebtoons('NAVER')">
          <div class="size-8 bg-primary rounded-lg flex items-center justify-center text-white shadow-sm group-hover:bg-accent transition-colors">
            <span class="material-symbols-outlined">auto_stories</span>
          </div>
          <h1 class="text-xl font-extrabold tracking-tight text-primary group-hover:text-accent transition-colors">ToonsToon</h1>
        </a>

        <!-- Nav Links -->
        <nav class="flex items-center gap-4">
          <a href="#" class="text-sm font-semibold text-text-muted hover:text-primary transition-colors">홈</a>
          <a href="#" class="text-sm font-semibold text-text-muted hover:text-primary transition-colors">마이페이지</a>
          
          <template v-if="!isLoggedIn">
            <a href="login.html" class="text-sm font-semibold text-primary hover:underline">로그인</a>
          </template>
          <template v-else>
            <button @click="handleLogout" class="px-4 py-1.5 text-xs font-bold text-white bg-primary rounded-full hover:bg-opacity-90 shadow-sm transition-transform active:scale-95">
              로그아웃
            </button>
          </template>
        </nav>
      </div>
    </header>

    <main class="w-full max-w-[1200px] mx-auto px-6 mt-8">
      
      <!-- Title Section -->
      <div class="text-center mb-10">
        <h2 class="text-3xl font-extrabold text-text-main mb-2">오늘의 웹툰</h2>
        <p class="text-text-muted text-sm">다양한 플랫폼의 웹툰을 한눈에 모아보세요.</p>
      </div>

      <!-- Filter Buttons -->
      <div class="flex flex-wrap justify-center gap-3 mb-12">
        <button 
          v-for="provider in ['NAVER', 'KAKAO', 'KAKAOPAGE']" 
          :key="provider"
          @click="loadWebtoons(provider)"
          :class="[
            'px-6 py-2.5 rounded-full text-sm font-bold shadow-sm transition-all duration-200 transform hover:-translate-y-0.5',
            currentProvider === provider 
              ? 'bg-primary text-white ring-2 ring-primary ring-offset-2' 
              : 'bg-white text-text-muted hover:bg-gray-50 border border-gray-200'
          ]"
        >
          {{ provider === 'KAKAOPAGE' ? '카카오페이지' : (provider === 'NAVER' ? '네이버' : '카카오') }}
        </button>
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="flex flex-col items-center justify-center py-20 text-text-muted">
        <div class="size-10 border-4 border-gray-200 border-t-primary rounded-full animate-spin mb-4"></div>
        <p>웹툰을 불러오고 있습니다...</p>
      </div>

      <!-- Webtoon Grid -->
      <div v-else class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-x-6 gap-y-10">
        <div v-for="toon in webtoons" :key="toon.id" class="group flex flex-col gap-3">
          
          <!-- Image Card -->
          <div class="relative aspect-[3/4] w-full rounded-2xl overflow-hidden shadow-soft group-hover:shadow-lg group-hover:-translate-y-1 transition-all duration-300 bg-gray-100">
            <!-- Link to Webtoon -->
            <a :href="toon.url" target="_blank" class="block w-full h-full">
              <img :src="toon.thumbnail" :alt="toon.title" class="w-full h-full object-cover transition-transform duration-500 group-hover:scale-105" loading="lazy">
            </a>

            <!-- Like Button -->
            <button 
              @click.stop="toggleFavorite(toon)"
              :class="[
                'absolute top-2 right-2 p-2 rounded-full backdrop-blur-md shadow-sm transition-all duration-200 z-10',
                toon.is_favorited ? 'bg-yellow-400 text-white' : 'bg-black/30 text-white/70 hover:bg-black/50'
              ]"
            >
              <span class="material-symbols-outlined text-[20px] block" style="font-variation-settings: 'FILL' 1;">star</span>
            </button>
          </div>

          <!-- Info -->
          <div>
            <h3 class="text-base font-bold text-text-main leading-tight truncate group-hover:text-primary transition-colors">
              {{ toon.title }}
            </h3>
            <div class="flex items-center justify-between mt-1">
              <p class="text-xs text-text-muted truncate max-w-[70%]">{{ toon.authors }}</p>
              <span class="text-[10px] font-bold text-primary bg-primary-light px-1.5 py-0.5 rounded">
                {{ toon.update_days }}
              </span>
            </div>
          </div>

        </div>
      </div>

      <!-- Empty State -->
      <div v-if="!loading && webtoons.length === 0" class="text-center py-20 text-gray-400">
        <span class="material-symbols-outlined text-4xl mb-2 block">sentiment_dissatisfied</span>
        <p>표시할 웹툰이 없습니다.</p>
      </div>

    </main>
  </div>
</template>
