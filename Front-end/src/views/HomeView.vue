<!-- src/views/HomeView.vue -->
<script setup>
import { ref, onMounted, computed  } from 'vue';
import { useRouter } from 'vue-router'
import axios from '@/api/axios'; // [중요] 설정해둔 axios import
import { useAuthStore } from '@/stores/auth';
import WebtoonRow from '@/components/WebtoonRow.vue'
import { useWebtoonStore } from '@/stores/webtoons'

const router = useRouter()

const authStore = useAuthStore();
const webtoonStore = useWebtoonStore()
const webtoons = computed(() => webtoonStore.items)
const loading = computed(() => webtoonStore.loading)
const error = computed(() => webtoonStore.error)
// 검색 쿼리
const searchQuery = ref('')

const loadingFavorites = ref(false)

// 웹툰 목록
async function fetchWebtoons() {
  await webtoonStore.fetchWebtoons()
}

// 검색
function goSearch() {
  if (!searchQuery.value.trim()) return
  router.push({
    name: 'Search',
    query: { q: searchQuery.value.trim() },
  })
}

// 즐겨찾기 토글(모든 카드 공통)
async function toggleFavorite(toon) {
  if (!authStore.isAuthenticated) {
    alert('로그인이 필요한 서비스입니다.');
    return;
  }

  const previousState = toon.is_favorited;
  toon.is_favorited = !toon.is_favorited;

  try {
    // Axios 요청 (토큰은 인터셉터가 자동 추가)
    await axios.post(`/webtoons/${toon.id}/favorite/`);
    if (!toon.is_favorited) {
      webtoonStore.removeFavorite(toon.id)  // 관심 리스트에서 제거
    }
  } catch (error) {
    // 실패 시 롤백
    toon.is_favorited = previousState;
    console.error('즐겨찾기 오류:', error);
    alert('오류가 발생했습니다.');
  }
}

onMounted(async () => {
  // 전체 웹툰 목록
  await webtoonStore.fetchWebtoons()
})

onMounted(() => {
  // 관심 웹툰
   webtoonStore.fetchFavorites()
})
// 관심 웹툰 목록
const favorites = computed(() => webtoonStore.favorites)
</script>

<template>
  <div>
    <!-- Title Section -->
    <div class="flex items-center justify-between mb-6">
      <div>
        <h2 class="text-3xl font-extrabold text-text-main mb-2">오늘의 웹툰</h2>
        <p class="text-text-muted text-sm">다양한 플랫폼의 웹툰을 한눈에 모아보세요.</p>
      </div>

      <div class="w-64">
        <input
          v-model="searchQuery"
          @keyup.enter="goSearch"
          type="text"
          placeholder="제목으로 검색"
          class="w-full border rounded-lg px-3 py-2 text-sm"
        />
      </div>
    </div>

    <!-- 1. Favorite Section -->
    <div v-if="loadingFavorites" class="py-6 text-sm text-text-muted">
      내 관심 웹툰을 불러오는 중입니다...
    </div>

    <!-- 관심 웹툰이 있을 때: 가로 슬라이드 -->
    <WebtoonRow
      v-else-if="favorites.length > 0"
      :title="''"       
      :items="favorites"
      :showMore="false"
      @toggle-favorite="toggleFavorite"
    />

    <!-- 관심 웹툰이 없을 때: 안내 문구 -->
    <div
      v-else
      class="py-10 flex flex-col items-center justify-center rounded-xl bg-gray-50 text-center"
    >
      <span class="material-symbols-outlined text-3xl mb-2 text-gray-400">
        star
      </span>
      <p class="text-sm font-semibold text-gray-700">
        관심 웹툰이 없습니다.
      </p>
      <p class="mt-1 text-xs text-gray-500">
        마음에 드는 작품의 별 아이콘을 눌러 관심 웹툰을 등록해보세요!
      </p>
    </div>
  </div>
</template>
