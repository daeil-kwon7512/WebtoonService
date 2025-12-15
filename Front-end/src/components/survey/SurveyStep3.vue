<template>
  <div class="animate-fade-in-up w-full max-w-2xl mx-auto">
    <!-- 헤더 (여백 축소) -->
    <div class="text-center mb-4">
      <h2 class="text-xl font-extrabold text-gray-900 mb-1">이 작품 어떠셨나요? 🤔</h2>
      <p class="text-gray-500 text-xs">
        <span class="text-blue-600 font-bold">5개 이상</span> 평가하면 추천 정확도가 올라갑니다!
      </p>
    </div>

    <!-- 진행률 바 (높이 및 여백 축소) -->
    <div class="mb-4">
      <div class="flex justify-between text-[10px] font-bold mb-1">
        <span :class="validCount >= targetCount ? 'text-blue-600' : 'text-gray-400'">
          {{ validCount >= targetCount ? '✅ 목표 달성!' : '데이터 수집 중...' }}
        </span>
        <span class="text-gray-500">{{ validCount }}/{{ targetCount }}</span>
      </div>
      <div class="w-full bg-gray-100 rounded-full h-2 overflow-hidden">
        <div 
          class="h-full transition-all duration-500 ease-out rounded-full"
          :class="validCount >= targetCount ? 'bg-blue-600' : 'bg-blue-300'"
          :style="{ width: Math.min((validCount / targetCount) * 100, 100) + '%' }"
        ></div>
      </div>
    </div>

    <!-- 메인 컨텐츠 영역 -->
    <div v-if="currentWebtoon" class="relative">
      
      <!-- 카드 컨테이너: flex-row로 변경하여 좌우 배치 (PC 기준) -->
      <div class="bg-white border border-gray-100 rounded-xl p-4 shadow-sm flex flex-col md:flex-row gap-4 items-center">
        
        <!-- 왼쪽: 썸네일 (크기 제한) -->
        <div class="w-32 md:w-40 flex-shrink-0">
          <div class="aspect-[2/3] w-full rounded-lg overflow-hidden bg-gray-100 relative shadow-inner">
            <img 
              v-if="currentWebtoon.thumbnail_url" 
              :src="currentWebtoon.thumbnail_url" 
              alt="웹툰 썸네일"
              class="w-full h-full object-cover"
              @error="handleImageError" 
            />
            <div v-else class="absolute inset-0 flex items-center justify-center text-gray-400 text-xs">
              No Image
            </div>
          </div>
        </div>
        
        <!-- 오른쪽: 정보 및 컨트롤 -->
        <div class="flex-1 w-full text-center md:text-left flex flex-col justify-center">
          
          <!-- 타이틀 및 장르 -->
          <div class="mb-4">
            <h3 class="text-lg font-bold text-gray-800 truncate px-1">
              {{ currentWebtoon.title }}
            </h3>
            <p class="text-xs text-gray-400">
               {{ currentWebtoon.genre || '장르 정보 없음' }}
            </p>
          </div>

          <!-- 평가 버튼 그리드 (2x2로 변경하여 공간 절약) -->
          <div class="grid grid-cols-2 gap-2 mb-3">
            <button 
              v-for="opt in ratingOptions" 
              :key="opt.value"
              @click="handleRate(opt.value)"
              class="py-3 px-2 rounded-lg transition-all active:scale-95 shadow-sm text-white font-bold text-xs flex items-center justify-center gap-1"
              :class="opt.colorClass"
            >
              <span>{{ opt.emoji }}</span>
              <span>{{ opt.label }}</span>
            </button>
          </div>

          <!-- 보지 않음 버튼 -->
          <button 
            @click="handleRate('WATCHED')" 
            class="w-full py-2 rounded-lg border border-gray-200 text-gray-400 text-xs font-medium hover:bg-gray-50 hover:text-gray-600 transition-colors"
          >
            아직 안 봤어요 (Skip)
          </button>
        </div>
      </div>

    </div>

    <!-- 로딩 상태 -->
    <div v-else class="flex flex-col items-center justify-center py-12">
      <div class="w-8 h-8 border-4 border-gray-200 border-t-blue-600 rounded-full animate-spin mb-3"></div>
      <p class="text-gray-400 text-sm animate-pulse">불러오는 중...</p>
    </div>

  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import axios from '@/api/axios'

const emit = defineEmits(['next', 'update-data'])

// --- State ---
const webtoonQueue = ref([])      
const currentIndex = ref(0)       
const ratings = ref({})           
const isLoading = ref(false)
const targetCount = 5

// 버튼 옵션 (이모지 추가로 직관성 높임)
const ratingOptions = [
  { label: '최고', value: 'BEST', emoji: '😍', colorClass: 'bg-violet-500 hover:bg-violet-600' },
  { label: '좋음', value: 'GOOD', emoji: '😊', colorClass: 'bg-emerald-400 hover:bg-emerald-500' },
  { label: '별로', value: 'BAD', emoji: '😐', colorClass: 'bg-amber-400 hover:bg-amber-500' },
  { label: '최악', value: 'WORST', emoji: '😫', colorClass: 'bg-rose-400 hover:bg-rose-500' },
]

// --- Computed ---
const currentWebtoon = computed(() => webtoonQueue.value[currentIndex.value] || null)

const validCount = computed(() => {
  return Object.values(ratings.value).filter(val => val !== 'WATCHED').length
})

// --- Methods ---
const fetchWebtoons = async (count = 10) => {
  try {
    isLoading.value = true
    const res = await axios.get('/api/survey/candidates/', { params: { count } })
    
    const newItems = res.data.filter(item => {
      const isRatedById = ratings.value[item.id] !== undefined
      const isInQueue = webtoonQueue.value.some(q => q.id === item.id)
      return !isRatedById && !isInQueue
    })
    
    webtoonQueue.value.push(...newItems)
  } catch (error) {
    console.error("데이터 로드 실패:", error)
  } finally {
    isLoading.value = false
  }
}

const handleImageError = (e) => {
  e.target.style.display = 'none'; 
  e.target.parentElement.classList.add('flex', 'items-center', 'justify-center', 'bg-gray-100');
  e.target.parentElement.innerHTML = '<span class="text-xs text-gray-400">이미지 없음</span>';
}

const handleRate = async (score) => {
  if (!currentWebtoon.value) return

  const webtoonId = currentWebtoon.value.id
  ratings.value[webtoonId] = score
  
  emit('update-data', ratings.value)

  const isLastItem = currentIndex.value >= webtoonQueue.value.length - 1

  if (isLastItem) {
    if (validCount.value >= targetCount) {
      emit('next')
    } else {
      const needed = Math.max(3, targetCount - validCount.value + 3)
      await fetchWebtoons(needed)
      
      if (currentIndex.value >= webtoonQueue.value.length - 1) {
          alert("평가할 웹툰이 더 이상 없습니다.");
          emit('next');
      } else {
          currentIndex.value++
      }
    }
  } else {
    currentIndex.value++
  }
}

onMounted(() => {
  fetchWebtoons(10)
})
</script>
