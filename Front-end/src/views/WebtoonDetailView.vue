<script setup>
import { ref, onMounted } from 'vue';
import { useRoute } from 'vue-router';
import { useAuthStore } from '@/stores/auth';
import axios from '@/api/axios';

const route = useRoute();
const authStore = useAuthStore();
const webtoon = ref(null);
const loading = ref(true);

// 1. 상세 정보 조회
const fetchWebtoonDetail = async () => {
  try {
    const webtoonId = route.params.id;
    // toons/urls.py에 정의된 상세 조회 API 호출
    const response = await axios.get(`/api/webtoons/${webtoonId}/`);
    webtoon.value = response.data;
  } catch (error) {
    console.error('상세 정보 로드 실패:', error);
  } finally {
    loading.value = false;
  }
};

// 2. 즐겨찾기 토글 (기능 이관)
const toggleFavorite = async () => {
  if (!webtoon.value) return;

  if (!authStore.isAuthenticated) {
    alert('로그인이 필요한 서비스입니다.');
    return;
  }

  // UI 즉시 반영 (낙관적 업데이트)
  const previousState = webtoon.value.is_favorited;
  webtoon.value.is_favorited = !webtoon.value.is_favorited;

  try {
    await axios.post(`/api/webtoons/${webtoon.value.id}/favorite/`);
    // 성공 시 별도 처리 없음
  } catch (error) {
    console.error('즐겨찾기 실패:', error);
    // 실패 시 롤백
    webtoon.value.is_favorited = previousState;
    if (error.response && error.response.status === 401) {
      alert('로그인이 필요한 서비스입니다.');
    }
  }
};

// 3. 플랫폼으로 이동 (보러가기)
const goToPlatform = () => {
  if (webtoon.value && webtoon.value.url) {
    window.open(webtoon.value.url, '_blank');
  } else {
    alert('이동할 주소가 없습니다.');
  }
};

onMounted(() => {
  fetchWebtoonDetail();
});
</script>

<template>
  <div v-if="webtoon" class="animate-fade-in">
    <!-- 상단 상세 정보 섹션 -->
    <div class="flex flex-col md:flex-row gap-8 mb-12">
      
      <!-- 1. 썸네일 이미지 -->
      <div class="w-full md:w-[300px] flex-shrink-0">
        <div class="rounded-2xl overflow-hidden shadow-soft aspect-[2/3] bg-gray-100 relative group">
          <img 
            :src="webtoon.thumbnail" 
            :alt="webtoon.title" 
            class="w-full h-full object-cover transition-transform duration-500 group-hover:scale-105" 
          />
          <!-- 19세 뱃지 (필요시) -->
          <div v-if="webtoon.is_adult" class="absolute top-3 right-3 bg-red-500 text-white text-xs font-bold px-2 py-1 rounded-full shadow-sm">
            19
          </div>
        </div>
      </div>

      <!-- 2. 텍스트 정보 & 액션 버튼 -->
      <div class="flex-1 flex flex-col">
        <!-- 타이틀 및 메타 정보 -->
        <div class="mb-6">
          <div class="flex items-center gap-3 mb-2">
            <span class="px-2.5 py-0.5 text-xs font-bold rounded-md bg-primary-light text-primary border border-primary/20">
              {{ webtoon.provider }}
            </span>
            <span class="text-xs text-text-muted font-medium">
              {{ webtoon.update_days }} 연재
            </span>
          </div>
          
          <h1 class="text-3xl md:text-4xl font-extrabold text-text-main tracking-tight mb-4">
            {{ webtoon.title }}
          </h1>

          <div class="text-sm font-medium text-text-muted flex items-center gap-2 mb-6">
            <span class="material-symbols-outlined text-lg">edit</span>
            <span>{{ webtoon.authors_display || webtoon.writers }}</span>
          </div>
        </div>

        <!-- 줄거리 -->
        <p class="text-text-main/80 leading-relaxed text-base mb-8 whitespace-pre-line">
          {{ webtoon.synopsis }}
        </p>

        <!-- 태그 리스트 -->
        <div class="flex flex-wrap gap-2 mb-10">
          <span 
            v-for="tag in webtoon.genres" 
            :key="tag" 
            class="px-3 py-1.5 bg-gray-100 hover:bg-gray-200 text-text-muted text-sm rounded-full transition-colors cursor-default"
          >
            #{{ tag }}
          </span>
        </div>

        <!-- 액션 버튼 (하단 고정 느낌) -->
        <div class="mt-auto flex flex-col sm:flex-row gap-4">
          <!-- 즐겨찾기 버튼 -->
          <button 
            @click="toggleFavorite"
            class="flex-1 flex items-center justify-center gap-2 px-6 py-4 rounded-xl border-2 transition-all duration-200 font-bold text-base"
            :class="webtoon.is_favorited 
              ? 'border-accent text-accent bg-accent/5' 
              : 'border-gray-200 text-text-muted hover:border-gray-300 hover:bg-gray-50'"
          >
            <span class="material-symbols-outlined" :class="{'filled-icon': webtoon.is_favorited}">
              favorite
            </span>
            {{ webtoon.is_favorited ? '관심웹툰 취소' : '관심웹툰 등록' }}
          </button>

          <!-- 보러가기 버튼 -->
          <button 
            @click="goToPlatform"
            class="flex-1 flex items-center justify-center gap-2 px-6 py-4 rounded-xl bg-primary text-white font-bold text-base shadow-md hover:bg-opacity-90 hover:shadow-lg transition-all active:scale-[0.98]"
          >
            <span>첫화보기 / 보러가기</span>
            <span class="material-symbols-outlined text-sm">open_in_new</span>
          </button>
        </div>
      </div>
    </div>

    <!-- 하단 아레나 섹션 (준비중) -->
    <div class="border-t border-gray-100 pt-10">
      <div class="flex items-center gap-2 mb-6">
        <span class="material-symbols-outlined text-2xl text-primary">forum</span>
        <h3 class="text-2xl font-bold text-text-main">아레나</h3>
        <span class="px-2 py-0.5 bg-gray-100 text-xs text-gray-500 rounded font-bold ml-2">BETA</span>
      </div>

      <div class="bg-gray-50 rounded-2xl p-12 text-center border border-dashed border-gray-200">
        <div class="inline-flex items-center justify-center w-16 h-16 rounded-full bg-white shadow-sm mb-4">
           <span class="material-symbols-outlined text-3xl text-gray-300">lock</span>
        </div>
        <h4 class="text-lg font-bold text-gray-600 mb-2">실시간 채팅 준비 중</h4>
        <p class="text-gray-400 text-sm">
          현재 웹툰 몰입도를 분석하고 있습니다.<br/>곧 다른 독자들과 실시간으로 소통할 수 있습니다.
        </p>
      </div>
    </div>
  </div>

  <!-- 로딩 상태 -->
  <div v-else-if="loading" class="flex flex-col items-center justify-center py-32 space-y-4">
    <div class="w-10 h-10 border-4 border-primary/30 border-t-primary rounded-full animate-spin"></div>
    <p class="text-text-muted font-medium">데이터를 불러오는 중입니다...</p>
  </div>

  <!-- 에러 상태 -->
  <div v-else class="py-20 text-center">
    <p class="text-lg text-gray-500">웹툰 정보를 찾을 수 없습니다.</p>
    <router-link to="/" class="text-primary font-bold hover:underline mt-4 inline-block">
      홈으로 돌아가기
    </router-link>
  </div>
</template>

<style scoped>
/* 구글 아이콘 채우기 스타일 (filled) */
.material-symbols-outlined.filled-icon {
  font-variation-settings: 'FILL' 1, 'wght' 400, 'GRAD' 0, 'opsz' 24;
}

/* 페이드인 애니메이션 */
.animate-fade-in {
  animation: fadeIn 0.5s ease-out;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>
