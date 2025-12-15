<template>
  <div class="animate-fade-in-up relative">
    <h2 class="text-2xl font-extrabold text-gray-900 mb-2">거의 다 왔습니다!</h2>
    <p class="text-gray-500 mb-8">주로 이용하는 웹툰 플랫폼을 알려주세요.</p>

    <div class="space-y-3 mb-8">
      <label 
        v-for="p in platforms" :key="p.value"
        class="flex items-center p-4 rounded-xl border-2 cursor-pointer transition-all hover:bg-gray-50"
        :class="selected === p.value ? 'border-blue-600 bg-blue-50 ring-1 ring-blue-600' : 'border-gray-100'"
      >
        <input type="radio" :value="p.value" v-model="selected" class="w-5 h-5 text-blue-600 focus:ring-blue-600 border-gray-300">
        <span class="ml-3 font-bold text-gray-700">{{ p.label }}</span>
      </label>
    </div>

    <button 
      @click="submit" 
      :disabled="!selected || isSubmitting"
      class="w-full py-4 rounded-xl font-bold text-white bg-blue-600 shadow-lg shadow-blue-200 transition-all active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed"
    >
      결과 보기
    </button>

    <!-- 로딩 오버레이 -->
    <div v-if="isSubmitting" class="absolute inset-0 bg-white/90 backdrop-blur-sm flex flex-col items-center justify-center z-10 rounded-xl">
      <div class="w-12 h-12 border-4 border-gray-200 border-t-blue-600 rounded-full animate-spin mb-4"></div>
      <p class="font-bold text-gray-800 animate-pulse">취향 분석 중입니다...</p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
defineProps(['isSubmitting'])
const emit = defineEmits(['submit'])

// 백엔드에 저장하기 좋은 형태로 값(value) 설정
const platforms = [
  { label: '네이버웹툰', value: 'NAVER' },
  { label: '카카오웹툰', value: 'KAKAO_WEBTOON' },
  { label: '카카오페이지', value: 'KAKAO_PAGE' }
]
const selected = ref('')

const submit = () => emit('submit', { platform: selected.value })
</script>
