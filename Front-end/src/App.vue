<!-- src/App.vue -->
<script setup>
import { onMounted } from 'vue';
import { useAuthStore } from '@/stores/auth';
import { useRouter } from 'vue-router';

const authStore = useAuthStore();
const router = useRouter();

// onMounted(() => {
//   // 앱 시작 시 토큰 체크하여 로그인 유지
//   authStore.initializeAuth();
// });
onMounted(async () => {
  // 앱 시작 시 토큰 체크하여 로그인 유지
  console.log('App mounted')
  await authStore.initializeAuth()
  console.log('initializeAuth done, isAuthenticated =', authStore.isAuthenticated)
})

const handleLogout = async () => {
  if (!confirm('정말 로그아웃 하시겠습니까?')) return;
  await authStore.logout();
  alert('로그아웃 되었습니다.');
  router.push('/login'); // 로그아웃 후 로그인 페이지로
};
</script>

<template>
  <div class="min-h-screen bg-background-light text-text-main font-sans selection:bg-primary/20 selection:text-primary pb-20">
    
    <!-- Navbar (Sticky) -->
    <header class="sticky top-0 z-50 w-full bg-white/90 backdrop-blur-md border-b border-gray-100 shadow-sm transition-all duration-300">
      <div class="max-w-[1200px] mx-auto px-6 h-16 flex items-center justify-between">
        <!-- Logo -->
        <router-link to="/" class="flex items-center gap-2 group">
          <div class="size-8 bg-primary rounded-lg flex items-center justify-center text-white shadow-sm group-hover:bg-accent transition-colors">
            <span class="material-symbols-outlined">auto_stories</span>
          </div>
          <h1 class="text-xl font-extrabold tracking-tight text-primary group-hover:text-accent transition-colors">ToonsToon</h1>
        </router-link>

        <!-- Nav Links -->
        <nav class="flex items-center gap-4">
          <router-link to="/" class="text-sm font-semibold text-text-muted hover:text-primary transition-colors">홈</router-link>
          
          <!-- 로그인 상태에 따른 분기 -->
          <template v-if="!authStore.isAuthenticated">
            <router-link to="/login" class="text-sm font-semibold text-primary hover:underline">로그인</router-link>
            <router-link to="/signup" class="text-sm font-semibold text-text-muted hover:text-primary">회원가입</router-link>
          </template>
          
          <template v-else>
            <span class="text-sm text-gray-600">{{ authStore.user?.username }}님</span>
            <button @click="handleLogout" class="px-4 py-1.5 text-xs font-bold text-white bg-primary rounded-full hover:bg-opacity-90 shadow-sm transition-transform active:scale-95">
              로그아웃
            </button>
          </template>
        </nav>
      </div>
    </header>

    <!-- Main Content (Routing) -->
    <main class="w-full max-w-[1200px] mx-auto px-6 mt-8">
      <router-view />
    </main>
  </div>
</template>
