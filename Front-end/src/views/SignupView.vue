<script setup>
import { ref } from 'vue';
import { useAuthStore } from '@/stores/auth';
import { useRouter } from 'vue-router';

const authStore = useAuthStore();
const router = useRouter();

// 폼 데이터
const formData = ref({
  username: '',
  email: '',
  password: '',
  passwordConfirm: '',
  gender: 'M', // 기본값
});

const errorMessage = ref('');

const handleSignup = async () => {
  // 1. 유효성 검사 (간단한 예시)
  if (formData.value.password !== formData.value.passwordConfirm) {
    errorMessage.value = '비밀번호가 일치하지 않습니다.';
    return;
  }
  if (formData.value.password.length < 4) {
    errorMessage.value = '비밀번호는 4자리 이상이어야 합니다.';
    return;
  }

  // 2. API 전송 데이터 준비
  const payload = {
    username: formData.value.username,
    email: formData.value.email,
    password: formData.value.password,
    gender: formData.value.gender,
  };

  // 3. 회원가입 요청 // [수정됨] 가입 후 설문조사 페이지로 이동
  const success = await authStore.register(payload);

  if (success) {
    // [수정됨] 회원가입 성공 시 바로 설문조사 페이지로 이동
    // (신규 유저는 무조건 설문 미완료 상태이므로 검사 불필요)
    router.push({ name: 'survey' });
  } else {
    // 에러 처리 (서버에서 받은 객체 형태에 따라 파싱 필요할 수 있음)
    // 예: { username: ["이미 존재하는 아이디입니다."] }
    const errorData = authStore.error;
    if (typeof errorData === 'object') {
       // 첫 번째 에러 메시지만 보여주기
       const firstKey = Object.keys(errorData)[0];
       errorMessage.value = `${firstKey}: ${errorData[firstKey]}`;
    } else {
       errorMessage.value = '회원가입 중 오류가 발생했습니다.';
    }
  }
};
</script>

<template>
  <div class="flex min-h-[80vh] items-center justify-center py-10">
    <div class="w-full max-w-md p-8 bg-white rounded-2xl shadow-lg border border-gray-100">
      
      <div class="text-center mb-8">
        <h2 class="text-2xl font-extrabold text-primary mb-2">회원가입</h2>
        <p class="text-sm text-text-muted">나만의 웹툰 리스트를 만들어보세요.</p>
      </div>

      <form @submit.prevent="handleSignup" class="space-y-5">
        
        <!-- Username -->
        <div>
          <label class="block text-sm font-semibold text-text-main mb-2">아이디</label>
          <input type="text" v-model="formData.username" required
            class="w-full px-4 py-3 rounded-lg border border-gray-200 focus:border-primary focus:ring-2 focus:ring-primary/20 transition-all outline-none" />
        </div>

        <!-- Email -->
        <div>
          <label class="block text-sm font-semibold text-text-main mb-2">이메일</label>
          <input type="email" v-model="formData.email" required
            class="w-full px-4 py-3 rounded-lg border border-gray-200 focus:border-primary focus:ring-2 focus:ring-primary/20 transition-all outline-none" />
        </div>

        <!-- Gender -->
        <div>
           <label class="block text-sm font-semibold text-text-main mb-2">성별</label>
           <div class="flex gap-4">
             <label class="flex items-center gap-2 cursor-pointer">
               <input type="radio" v-model="formData.gender" value="M" class="text-primary focus:ring-primary" />
               <span class="text-sm">남성</span>
             </label>
             <label class="flex items-center gap-2 cursor-pointer">
               <input type="radio" v-model="formData.gender" value="F" class="text-primary focus:ring-primary" />
               <span class="text-sm">여성</span>
             </label>
           </div>
        </div>

        <!-- Password -->
        <div>
          <label class="block text-sm font-semibold text-text-main mb-2">비밀번호</label>
          <input type="password" v-model="formData.password" required
            class="w-full px-4 py-3 rounded-lg border border-gray-200 focus:border-primary focus:ring-2 focus:ring-primary/20 transition-all outline-none" />
        </div>

        <!-- Password Confirm -->
        <div>
          <label class="block text-sm font-semibold text-text-main mb-2">비밀번호 확인</label>
          <input type="password" v-model="formData.passwordConfirm" required
            class="w-full px-4 py-3 rounded-lg border border-gray-200 focus:border-primary focus:ring-2 focus:ring-primary/20 transition-all outline-none" 
            :class="{'border-red-300': formData.password !== formData.passwordConfirm && formData.passwordConfirm}" />
            <p v-if="formData.password !== formData.passwordConfirm && formData.passwordConfirm" class="text-xs text-red-500 mt-1">
              비밀번호가 일치하지 않습니다.
            </p>
        </div>

        <!-- Error Message -->
        <div v-if="errorMessage" class="text-red-500 text-sm font-medium text-center bg-red-50 py-2 rounded-lg">
          {{ errorMessage }}
        </div>

        <!-- Submit Button -->
        <button type="submit" :disabled="authStore.loading"
          class="w-full py-3.5 bg-primary text-white font-bold rounded-xl hover:bg-opacity-90 transition-all shadow-md active:scale-[0.98] mt-4">
          <span v-if="authStore.loading">가입 처리 중...</span>
          <span v-else>가입하기</span>
        </button>

      </form>

      <div class="mt-6 text-center text-sm text-text-muted">
        이미 계정이 있으신가요? 
        <router-link to="/login" class="text-primary font-bold hover:underline ml-1">로그인</router-link>
      </div>

    </div>
  </div>
</template>
