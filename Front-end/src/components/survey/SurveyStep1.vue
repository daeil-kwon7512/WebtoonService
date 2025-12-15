<template>
  <div class="animate-fade-in-up">
    <h2 class="text-2xl font-extrabold text-gray-900 mb-2">환영합니다! 👋</h2>
    <p class="text-gray-500 mb-8">더 정확한 추천을 위해 기본 정보를 알려주세요.</p>

    <!-- 출생년도 -->
    <div class="mb-6">
      <label class="block text-sm font-bold text-gray-700 mb-2">출생년도</label>
      <input 
        type="number" 
        v-model="localData.birth_year" 
        placeholder="예: 2000"
        class="w-full px-4 py-3 rounded-xl border border-gray-200 focus:border-blue-600 focus:ring-2 focus:ring-blue-100 outline-none transition-all"
      >
    </div>

    <!-- 성별 -->
    <div class="mb-8">
      <label class="block text-sm font-bold text-gray-700 mb-3">성별</label>
      <div class="grid grid-cols-2 gap-4">
        <label 
          class="cursor-pointer border-2 rounded-xl py-3 text-center font-bold transition-all"
          :class="localData.gender === 'M' ? 'border-blue-600 bg-blue-50 text-blue-600' : 'border-gray-100 text-gray-400 hover:border-gray-300'"
        >
          <input type="radio" value="M" v-model="localData.gender" class="hidden">
          남성
        </label>
        <label 
          class="cursor-pointer border-2 rounded-xl py-3 text-center font-bold transition-all"
          :class="localData.gender === 'F' ? 'border-blue-600 bg-blue-50 text-blue-600' : 'border-gray-100 text-gray-400 hover:border-gray-300'"
        >
          <input type="radio" value="F" v-model="localData.gender" class="hidden">
          여성
        </label>
      </div>
    </div>

    <button 
      @click="next" 
      :disabled="!isValid"
      class="w-full py-4 rounded-xl font-bold text-white bg-blue-600 shadow-lg shadow-blue-200 transition-all active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed hover:bg-blue-700"
    >
      다음 단계로
    </button>
  </div>
</template>

<script setup>
import { reactive, computed } from 'vue'
const emit = defineEmits(['next'])

const localData = reactive({ birth_year: null, gender: null })
const isValid = computed(() => localData.birth_year && localData.gender)

const next = () => emit('next', { ...localData })
</script>
