<!-- src/views/SurveyView.vue -->
<template>
  <div class="min-h-screen bg-gray-50 flex items-center justify-center p-6">
    <div class="w-full max-w-lg bg-white rounded-3xl shadow-xl overflow-hidden">
      
      <!-- 상단 진행바 -->
      <div class="h-1.5 w-full bg-gray-100">
        <div 
          class="h-full bg-blue-600 transition-all duration-500 ease-out" 
          :style="{ width: (currentStep / 4) * 100 + '%' }"
        ></div>
      </div>

      <!-- 컨텐츠 영역 -->
      <div class="p-8 md:p-10">
        <SurveyStep1 
          v-if="currentStep === 1" 
          @next="handleNext" 
        />
        <SurveyStep2 
          v-if="currentStep === 2" 
          @next="handleNext" 
        />
        <SurveyStep3 
          v-if="currentStep === 3" 
          @next="handleNext" 
          @update-data="updateWebtoonRatings"
        />
        <!-- Step 4는 플랫폼 선택이지만, 백엔드에는 저장하지 않더라도 완료 버튼 역할로 유지 -->
        <SurveyStep4 
          v-if="currentStep === 4" 
          @submit="handleSubmit" 
          :is-submitting="isSubmitting"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import axios from '@/api/axios' // main 프로젝트의 axios 설정 파일 import

// 컴포넌트 경로 (src/components/survey 폴더 생성 필요)
import SurveyStep1 from '@/components/survey/SurveyStep1.vue'
import SurveyStep2 from '@/components/survey/SurveyStep2.vue'
import SurveyStep3 from '@/components/survey/SurveyStep3.vue'
import SurveyStep4 from '@/components/survey/SurveyStep4.vue'

const router = useRouter()
const authStore = useAuthStore()

const currentStep = ref(1)
const isSubmitting = ref(false)

// Vue 내부 관리용 데이터
const surveyData = reactive({
  birth_year: null,
  gender: null,
  genres: [], // Step 2 결과
  ratings: {}, // Step 3 결과 (Object 형태 { id: rating })
  platform: '' // Step 4 결과 (백엔드 전송 X, UI용)
})

const handleNext = (stepData) => {
  if (stepData) Object.assign(surveyData, stepData)
  currentStep.value++
}

const updateWebtoonRatings = (ratings) => {
  // Step 3에서 실시간으로 넘어오는 평가 데이터를 저장
  surveyData.ratings = ratings
}

const handleSubmit = async (step4Data) => {
  // Step 4에서 넘어온 데이터(platform) 저장
  if (step4Data && step4Data.platform) {
    surveyData.platform = step4Data.platform
  }

  isSubmitting.value = true
  
  // 백엔드로 보낼 최종 데이터 구성
  const payload = {
    gender: surveyData.gender,
    birth_year: surveyData.birth_year,
    preferred_genres: surveyData.genres,
    main_platform: surveyData.platform, // [추가됨] 플랫폼 정보 전송
    
    // 평가 데이터 변환
    webtoon_ratings: Object.entries(surveyData.ratings).map(([id, rating]) => ({
      id: id,
      rating: rating
    }))
  }

  try {
    // API 호출
    await axios.post('/api/accounts/survey/submit/', payload)
    
    // 스토어 상태 업데이트
    if (authStore.completeSurvey) await authStore.completeSurvey()
    
    // [요구사항 반영] 로딩 메시지("사용자에 맞는 추천을 찾고 있습니다")를 보여주기 위해 
    // Step4 컴포넌트의 UI 상태를 유지하다가, 1.5초 뒤 이동
    setTimeout(() => {
        router.push({ name: 'home' }) 
    }, 1500)

  } catch (error) {
    console.error('설문 전송 실패:', error)
    alert("오류가 발생했습니다. 잠시 후 다시 시도해주세요.")
  } finally {
    // 성공 시에는 로딩 상태를 끄지 않고 페이지 이동을 기다림 (자연스러운 UX)
    // 실패 시에만 끔
    // isSubmitting.value = false 
  }
}
</script>
