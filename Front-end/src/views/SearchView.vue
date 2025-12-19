<!-- src/views/SearchView.vue -->
<template>
  <div class="max-w-[1200px] mx-auto px-6 py-8">
    <!-- 헤더 영역 -->
    <div class="mb-8">
      <h2 class="text-2xl font-extrabold text-text-main mb-2">
        "{{ query }}" 검색 결과
      </h2>
      <p class="text-sm text-text-muted" v-if="!loading && webtoons.length > 0">
        총 {{ webtoons.length }}개의 작품을 찾았습니다.
      </p>
    </div>

    <!-- 로딩 상태 -->
    <div v-if="loading" class="py-20 flex justify-center items-center text-text-muted">
       <span class="material-symbols-outlined animate-spin mr-2">progress_activity</span>
       검색 중입니다...
    </div>

    <!-- 에러 상태 -->
    <div v-else-if="error" class="py-20 text-center text-red-500 font-medium">
      {{ error }}
    </div>

    <!-- 검색 결과 없음 -->
    <div v-else-if="!webtoons.length" class="py-32 flex flex-col items-center justify-center bg-gray-50 rounded-2xl border border-dashed border-gray-200">
      <span class="material-symbols-outlined text-5xl text-gray-300 mb-4">search_off</span>
      <p class="text-lg font-bold text-gray-600 mb-1">검색 결과가 없습니다.</p>
      <p class="text-sm text-gray-400">다른 키워드로 검색해 보세요.</p>
    </div>

    <!-- 검색 결과 리스트 (Grid Layout) -->
    <!-- 반응형: 모바일 2열 -> 태블릿 4열 -> 데스크탑 5~6열 -->
    <div v-else class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-x-6 gap-y-10">
      <WebtoonCard
        v-for="toon in webtoons"
        :key="toon.id"
        :toon="toon"
        @toggle-favorite="toggleFavorite"
      />
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useWebtoonStore } from '@/stores/webtoons'
import { useAuthStore } from '@/stores/auth'
import axios from '@/api/axios'
// [중요] WebtoonCard 컴포넌트 불러오기
import WebtoonCard from '@/components/WebtoonCard.vue'

const route = useRoute()
const webtoonStore = useWebtoonStore()
const authStore = useAuthStore()

const query = computed(() => route.query.q || '')
const webtoons = computed(() => webtoonStore.items)
const loading = computed(() => webtoonStore.loading)
const error = computed(() => webtoonStore.error)

async function runSearch() {
  if (query.value) {
    await webtoonStore.fetchWebtoons({ q: query.value })
  }
}

// WebtoonCard에서 발생하는 즐겨찾기 이벤트 처리
async function toggleFavorite(toon) {
  if (!authStore.isAuthenticated) {
    alert('로그인이 필요한 서비스입니다.')
    return
  }

  // 낙관적 업데이트 (UI 먼저 변경)
  const prev = toon.is_favorited
  toon.is_favorited = !prev

  try {
    await axios.post(`/api/webtoons/${toon.id}/favorite/`)
  } catch (e) {
    // 실패 시 롤백
    toon.is_favorited = prev
    console.error(e)
    if (e.response && e.response.status === 401) {
       alert('로그인이 만료되었습니다.')
    }
  }
}

onMounted(runSearch)
watch(query, runSearch)
</script>
