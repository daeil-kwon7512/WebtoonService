<!-- src/views/SearchView.vue -->
<template>
  <div class="p-4">
    <h2 class="text-xl font-bold mb-4">
      "{{ query }}" 검색 결과
    </h2>

    <div v-if="loading">검색 중입니다...</div>
    <div v-else-if="error">{{ error }}</div>
    <div v-else-if="!webtoons.length">
      검색 결과가 없습니다.
    </div>
    <ul v-else class="space-y-3">
      <li v-for="w in webtoons" :key="w.id" class="flex gap-3 items-center">
        <img
          v-if="w.thumbnail"
          :src="w.thumbnail"
          :alt="w.title"
          class="w-32 h-40 object-cover rounded"
        />
        <div class="flex-1">
          <div class="flex items-center gap-2">
            <p class="font-semibold">{{ w.title }}</p>
            <button type="button" @click="toggleFavorite(w)">
              <Icon
                :icon="w.is_favorited ? 'material-symbols:star' : 'material-symbols:star-outline'"
                class="text-yellow-400 text-xl"
              />
            </button>
          </div>
          <p class="text-xs text-gray-500">
            {{ w.authors_display }} · {{ w.provider }} · {{ w.update_days }}
          </p>
        </div>
      </li>
    </ul>
  </div>
</template>

<script setup>
import { Icon } from '@iconify/vue'
import { computed, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useWebtoonStore } from '@/stores/webtoons'
import { useAuthStore } from '@/stores/auth'
import axios from '@/api/axios'

const route = useRoute()
const webtoonStore = useWebtoonStore()
const authStore = useAuthStore()

const query = computed(() => route.query.q || '')

const webtoons = computed(() => webtoonStore.items)
const loading = computed(() => webtoonStore.loading)
const error = computed(() => webtoonStore.error)

async function runSearch() {
  await webtoonStore.fetchWebtoons({ q: query.value })
}

async function toggleFavorite(toon) {
  if (!authStore.isAuthenticated) {
    alert('로그인이 필요한 서비스입니다.')
    return
  }

  const prev = toon.is_favorited
  toon.is_favorited = !prev

  try {
    await axios.post(`/webtoons/${toon.id}/favorite/`)
  } catch (e) {
    toon.is_favorited = prev
    console.error(e)
  }
}

onMounted(runSearch)
// 주소창에서 q가 바뀌면 결과 다시 로드
watch(query, () => {
  runSearch()
})
</script>
