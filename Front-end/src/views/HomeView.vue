<!-- src/views/HomeView.vue -->
<script setup>
import { ref, onMounted, computed } from 'vue';
import { useRouter } from 'vue-router'
import axios from '@/api/axios'; 
import { useAuthStore } from '@/stores/auth';
import WebtoonRow from '@/components/WebtoonRow.vue'
import { useWebtoonStore } from '@/stores/webtoons'

const router = useRouter()
const authStore = useAuthStore();
const webtoonStore = useWebtoonStore()

// Store 상태 사용
const webtoons = computed(() => webtoonStore.items)
const loading = computed(() => webtoonStore.loading)
const loadingFavorites = ref(false)
const favorites = computed(() => webtoonStore.favorites)

// [삭제됨] searchQuery, goSearch 함수 제거

// 즐겨찾기 토글 함수
async function toggleFavorite(toon) {
  if (!authStore.isAuthenticated) {
    alert('로그인이 필요한 서비스입니다.');
    return;
  }
  const previousState = toon.is_favorited;
  toon.is_favorited = !toon.is_favorited;

  try {
    await axios.post(`/api/webtoons/${toon.id}/favorite/`);
    if (!toon.is_favorited) {
      webtoonStore.removeFavorite(toon.id) 
    }
  } catch (error) {
    toon.is_favorited = previousState;
    console.error('즐겨찾기 오류:', error);
    alert('오류가 발생했습니다.');
  }
}

onMounted(async () => {
  await webtoonStore.fetchWebtoons()
  // 로그인 상태라면 관심 웹툰도 로드
  if (authStore.isAuthenticated) {
      webtoonStore.fetchFavorites()
  }
})
</script>

<template>
  <div>
    <!-- Title Section -->
    <div class="mb-8 mt-4"> <!-- [변경] flex 제거, 단순 마진 적용 -->
      <h2 class="text-3xl font-extrabold text-text-main mb-2">오늘의 웹툰</h2>
      <p class="text-text-muted text-sm">다양한 플랫폼의 웹툰을 한눈에 모아보세요.</p>
    </div>
    <!-- [삭제됨] 검색창 input 영역 제거 -->

    <!-- 1. Favorite Section -->
    <div v-if="loadingFavorites" class="py-6 text-sm text-text-muted">
      내 관심 웹툰을 불러오는 중입니다...
    </div>

    <!-- 관심 웹툰이 있을 때 -->
    <WebtoonRow
      v-else-if="favorites.length > 0"
      :title="'나의 관심 웹툰'" 
      :items="favorites"
      :showMore="false"
      @toggle-favorite="toggleFavorite"
    />

    <!-- 관심 웹툰 없을 때 (디자인 유지) -->
    <div
      v-else
      class="mb-12 py-10 flex flex-col items-center justify-center rounded-xl bg-gray-50 text-center border border-dashed border-gray-200"
    >
      <span class="material-symbols-outlined text-3xl mb-2 text-gray-400">star</span>
      <p class="text-sm font-semibold text-gray-700">관심 웹툰이 없습니다.</p>
      <p class="mt-1 text-xs text-gray-500">마음에 드는 작품을 등록해보세요!</p>
    </div>

    <!-- 2. 전체 웹툰 목록 (추가 예시) -->
    <!-- 필요하다면 WebtoonRow를 하나 더 써서 전체 목록이나 추천 목록을 보여줄 수 있습니다 -->
    <WebtoonRow
      v-if="webtoons.length > 0"
      :title="'실시간 인기 웹툰'"
      :items="webtoons.slice(0, 10)"
      :showMore="true"
      @toggle-favorite="toggleFavorite"
    />
  </div>
</template>
