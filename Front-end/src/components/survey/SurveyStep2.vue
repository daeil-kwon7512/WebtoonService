<template>
  <div class="animate-fade-in-up">
    <h2 class="text-2xl font-extrabold text-gray-900 mb-2">어떤 장르를 좋아하세요?</h2>
    <p class="text-gray-500 mb-6">좋아하는 장르를 모두 선택해주세요. (최소 1개)</p>

    <div class="flex flex-wrap gap-2 mb-8">
      <button 
        v-for="g in genres" :key="g"
        @click="toggleGenre(g)"
        class="px-4 py-2 rounded-full border text-sm font-bold transition-all duration-200 transform active:scale-95"
        :class="selected.includes(g) 
          ? 'bg-gray-900 text-white border-gray-900 shadow-md' 
          : 'bg-white text-gray-600 border-gray-200 hover:border-gray-400'"
      >
        {{ g }}
      </button>
    </div>

    <button 
      @click="next" 
      :disabled="selected.length === 0"
      class="w-full py-4 rounded-xl font-bold text-white bg-blue-600 shadow-lg shadow-blue-200 transition-all active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed hover:bg-blue-700"
    >
      {{ selected.length === 0 ? '장르를 선택해주세요' : `다음 (${selected.length}개 선택됨)` }}
    </button>
  </div>
</template>

<script setup>
import { ref } from 'vue'
const emit = defineEmits(['next'])

const genres = ['로맨스', '로맨스 판타지', '판타지/이세계', '액션/무협', '스릴러/미스터리', '드라마', '코미디/일상', '스포츠/직업']
const selected = ref([])

const toggleGenre = (g) => {
  if (selected.value.includes(g)) {
    selected.value = selected.value.filter(item => item !== g)
  } else {
    selected.value.push(g)
  }
}

const next = () => emit('next', { genres: selected.value })
</script>
