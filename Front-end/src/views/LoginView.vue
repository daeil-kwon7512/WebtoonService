<script setup>
import { ref } from 'vue';
import { useAuthStore } from '@/stores/auth';
import { useRouter } from 'vue-router';

const authStore = useAuthStore();
const router = useRouter();

const username = ref('');
const password = ref('');
const errorMessage = ref('');

const handleLogin = async () => {
  if (!username.value || !password.value) {
    errorMessage.value = '아이디와 비밀번호를 모두 입력해주세요.';
    return;
  }

  // 1. 로그인 시도
  const success = await authStore.login(username.value, password.value);

  if (success) {
    // 2. 로그인 성공 시, 유저 정보(onboarding_completed) 확인
    // authStore.user는 fetchUser()에 의해 이미 채워져 있음
    if (authStore.user && !authStore.user.onboarding_completed) {
        // 설문 미완료 -> 설문 페이지로
        router.push({ name: 'survey' });
    } else {
        // 설문 완료(또는 정보 없음) -> 홈으로
        router.push({ name: 'home' });
    }
  } else {
    errorMessage.value = authStore.error || '로그인에 실패했습니다.';
  }
};
</script>

<template>
  <div class="flex min-h-[80vh] items-center justify-center">
    <div class="w-full max-w-md p-8 bg-white rounded-2xl shadow-lg border border-gray-100">
      
      <!-- Header -->
      <div class="text-center mb-8">
        <h2 class="text-2xl font-extrabold text-primary mb-2">로그인</h2>
        <p class="text-sm text-text-muted">ToonsToon에 오신 것을 환영합니다.</p>
      </div>

      <!-- Form -->
      <form @submit.prevent="handleLogin" class="space-y-6">
        
        <!-- Username Input -->
        <div>
          <label for="username" class="block text-sm font-semibold text-text-main mb-2">아이디</label>
          <input 
            type="text" 
            id="username" 
            v-model="username"
            class="w-full px-4 py-3 rounded-lg border border-gray-200 focus:border-primary focus:ring-2 focus:ring-primary/20 transition-all outline-none"
            placeholder="아이디를 입력하세요"
          />
        </div>

        <!-- Password Input -->
        <div>
          <label for="password" class="block text-sm font-semibold text-text-main mb-2">비밀번호</label>
          <input 
            type="password" 
            id="password" 
            v-model="password"
            class="w-full px-4 py-3 rounded-lg border border-gray-200 focus:border-primary focus:ring-2 focus:ring-primary/20 transition-all outline-none"
            placeholder="비밀번호를 입력하세요"
          />
        </div>

        <!-- Error Message -->
        <div v-if="errorMessage" class="text-red-500 text-sm font-medium text-center bg-red-50 py-2 rounded-lg">
          {{ errorMessage }}
        </div>

        <!-- Submit Button -->
        <button 
          type="submit" 
          :disabled="authStore.loading"
          class="w-full py-3.5 bg-primary text-white font-bold rounded-xl hover:bg-opacity-90 transition-all shadow-md active:scale-[0.98] disabled:opacity-70 disabled:cursor-not-allowed flex justify-center items-center gap-2"
        >
          <span v-if="authStore.loading" class="size-5 border-2 border-white/30 border-t-white rounded-full animate-spin"></span>
          <span>{{ authStore.loading ? '로그인 중...' : '로그인하기' }}</span>
        </button>
      </form>

      <!-- Footer Links -->
      <div class="mt-8 text-center text-sm text-text-muted">
        계정이 없으신가요? 
        <router-link to="/signup" class="text-primary font-bold hover:underline ml-1">회원가입</router-link>
      </div>

    </div>
  </div>
</template>
