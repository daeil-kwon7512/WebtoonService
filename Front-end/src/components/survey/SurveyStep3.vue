<template>
  <div class="animate-fade-in-up">
    <!-- 헤더 -->
    <div class="text-center mb-6">
      <h2 class="text-2xl font-extrabold text-gray-900 mb-2">이 작품 어떠셨나요? 🤔</h2>
      <p class="text-gray-500 text-sm">
        본 적 있는 웹툰만 평가해주세요.<br>
        <span class="text-blue-600 font-bold">5개 이상</span> 평가하면 추천 정확도가 올라갑니다!
      </p>
    </div>

    <!-- 진행률 바 (Progress Bar) -->
    <div class="mb-8">
      <div class="flex justify-between text-xs font-bold mb-2">
        <span :class="validCount >= targetCount ? 'text-blue-600' : 'text-gray-400'">
          {{ validCount >= targetCount ? '✅ 목표 달성!' : '데이터 수집 중...' }}
        </span>
        <span class="text-gray-500">{{ validCount }}/{{ targetCount }}</span>
      </div>
      <div class="w-full bg-gray-100 rounded-full h-3 overflow-hidden">
        <div 
          class="h-full transition-all duration-500 ease-out rounded-full"
          :class="validCount >= targetCount ? 'bg-blue-600' : 'bg-blue-300'"
          :style="{ width: Math.min((validCount / targetCount) * 100, 100) + '%' }"
        ></div>
      </div>
    </div>

    <!-- 메인 컨텐츠 영역 -->
    <div v-if="currentWebtoon" class="relative">
      
      <!-- 웹툰 카드 -->
      <div class="bg-white border border-gray-100 rounded-2xl p-4 shadow-sm mb-6">
        <!-- 썸네일 이미지 -->
        <div class="aspect-[2/3] w-full rounded-xl overflow-hidden bg-gray-100 mb-4 relative shadow-inner">
          <img 
            v-if="currentWebtoon.thumbnail_url" 
            :src="currentWebtoon.thumbnail_url" 
            alt="웹툰 썸네일"
            class="w-full h-full object-cover transition-transform duration-700 hover:scale-105"
            @error="handleImageError" 
          />
          <div v-else class="absolute inset-0 flex items-center justify-center text-gray-400 font-bold text-sm">
            이미지 준비중
          </div>
        </div>
        
        <!-- 타이틀 -->
        <h3 class="text-xl font-bold text-gray-800 text-center truncate px-2 mb-1">
          {{ currentWebtoon.title }}
        </h3>
        <p class="text-xs text-gray-400 text-center mb-4">
           {{ currentWebtoon.genre || '장르 정보 없음' }}
        </p>

        <!-- 평가 버튼 그리드 -->
        <div class="grid grid-cols-4 gap-2 mb-3">
          <button 
            v-for="opt in ratingOptions" 
            :key="opt.value"
            @click="handleRate(opt.value)"
            class="flex flex-col items-center justify-center py-3 rounded-xl transition-all duration-200 active:scale-95 shadow-sm text-white font-bold text-sm"
            :class="opt.colorClass"
          >
            <span>{{ opt.label }}</span>
          </button>
        </div>

        <!-- 보지 않음 버튼 -->
        <button 
          @click="handleRate('WATCHED')" 
          class="w-full py-3 rounded-xl border-2 border-gray-100 text-gray-500 font-bold hover:bg-gray-50 hover:border-gray-200 transition-colors"
        >
          아직 안 봤어요 (Skip)
        </button>
      </div>

    </div>

    <!-- 로딩 상태 (데이터 없을 때) -->
    <div v-else class="flex flex-col items-center justify-center py-20">
      <div class="w-10 h-10 border-4 border-gray-200 border-t-blue-600 rounded-full animate-spin mb-4"></div>
      <p class="text-gray-400 font-medium animate-pulse">다음 작품을 불러오고 있어요...</p>
    </div>

  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import axios from '@/api/axios' // main 프로젝트의 axios 인스턴스 사용

const emit = defineEmits(['next', 'update-data'])

// --- State ---
const webtoonQueue = ref([])      
const currentIndex = ref(0)       
const ratings = ref({})           
const isLoading = ref(false)
const targetCount = 5             // 목표 유효 응답 수

// 버튼 옵션 (백엔드 Model과 매핑된 값 사용: WORST, BAD, GOOD, BEST)
const ratingOptions = [
  { label: '별로', value: 'WORST', colorClass: 'bg-rose-400 hover:bg-rose-500' },
  { label: '글쎄', value: 'BAD', colorClass: 'bg-amber-400 hover:bg-amber-500' },
  { label: '볼만해', value: 'GOOD', colorClass: 'bg-emerald-400 hover:bg-emerald-500' },
  { label: '최고야', value: 'BEST', colorClass: 'bg-violet-500 hover:bg-violet-600' },
]

// --- Computed ---
const currentWebtoon = computed(() => webtoonQueue.value[currentIndex.value] || null)

const validCount = computed(() => {
  // WATCHED(보지 않음)은 유효 개수에서 제외
  return Object.values(ratings.value).filter(val => val !== 'WATCHED').length
})

// --- Methods ---
const fetchWebtoons = async (count = 10) => {
  try {
    isLoading.value = true
    
    // [수정] 백엔드 API 주소 일치시킴
    const res = await axios.get('/api/survey/candidates/', { params: { count } })
    
    // 중복 및 이미 평가한 항목 제외
    const newItems = res.data.filter(item => {
      // 1. 이미 평가한 ID인지 확인
      const isRatedById = ratings.value[item.id] !== undefined
      // 2. 현재 큐에 들어있는지 확인
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
  e.target.parentElement.classList.add('flex', 'items-center', 'justify-center', 'text-xs', 'text-gray-400');
  e.target.parentElement.innerText = '이미지 없음';
}

const handleRate = async (score) => {
  if (!currentWebtoon.value) return

  // 1. 데이터 기록
  const webtoonId = currentWebtoon.value.id
  ratings.value[webtoonId] = score
  
  emit('update-data', ratings.value)

  // 2. 다음 로직 판단
  const isLastItem = currentIndex.value >= webtoonQueue.value.length - 1

  if (isLastItem) {
    // 큐의 끝
    if (validCount.value >= targetCount) {
      emit('next') // 완료 -> 다음 단계로
    } else {
      // 부족함 -> 추가 로드 (sub 코드의 핵심 로직)
      console.log(`현재 ${validCount.value}개. 부족하여 추가 로딩...`)
      
      // 필요한 만큼 넉넉히 요청 (예: 남은 개수 + 여유분)
      const needed = Math.max(3, targetCount - validCount.value + 3)
      await fetchWebtoons(needed)
      
      // 로딩 후에도 큐가 늘어나지 않았다면 (서버 데이터 고갈 등) 강제 종료 처리 가능
      if (currentIndex.value >= webtoonQueue.value.length - 1) {
          alert("평가할 웹툰이 더 이상 없습니다.");
          emit('next');
      } else {
          currentIndex.value++ // 다음 카드로 이동
      }
    }
  } else {
    // 큐 남음 -> 다음 카드
    currentIndex.value++
  }
}

onMounted(() => {
  // 처음에 10개 로딩
  fetchWebtoons(10)
})
</script>
