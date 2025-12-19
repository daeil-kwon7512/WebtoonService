<!-- src/App.vue -->
<script setup>
import { ref, onMounted } from 'vue'; // [추가] ref
import { useAuthStore } from '@/stores/auth';
import { useRouter } from 'vue-router';

const authStore = useAuthStore();
const router = useRouter();
const searchQuery = ref(''); // [추가] 검색어 상태

// [추가] 검색 함수
const goSearch = () => {
  if (!searchQuery.value.trim()) return;
  router.push({
    name: 'Search',
    query: { q: searchQuery.value.trim() },
  });
  // 검색 후 입력창 비우고 싶다면: searchQuery.value = '';
};

onMounted(async () => {
  console.log('App mounted');
  await authStore.initializeAuth();
  console.log('initializeAuth done, isAuthenticated =', authStore.isAuthenticated);
});

const handleLogout = async () => {
  if (!confirm('정말 로그아웃 하시겠습니까?')) return;
  await authStore.logout();
  alert('로그아웃 되었습니다.');
  router.push('/login');
};
</script>

<template>
  <div class="min-h-screen bg-background-light text-text-main font-sans selection:bg-primary/20 selection:text-primary pb-20">
    
    <!-- Navbar (Sticky) -->
    <header class="sticky top-0 z-50 w-full bg-white/90 backdrop-blur-md border-b border-gray-100 shadow-sm transition-all duration-300">
      <div class="max-w-[1200px] mx-auto px-6 h-16 flex items-center justify-between gap-4"> <!-- gap-4 추가 -->
        
        <!-- 1. Logo 영역 (왼쪽) -->
        <router-link to="/" class="flex items-center gap-2 group shrink-0">
          <div class="size-8 bg-primary rounded-lg flex items-center justify-center text-white shadow-sm group-hover:bg-accent transition-colors">
            <span class="material-symbols-outlined">auto_stories</span>
          </div>
          <h1 class="text-xl font-extrabold tracking-tight text-primary group-hover:text-accent transition-colors hidden sm:block"> <!-- 모바일 공간확보 위해 hidden sm:block -->
            ToonsToon
          </h1>
        </router-link>

        <!-- 2. [수정] 검색창 영역 -->
        <div class="flex-1 max-w-md mx-4"> 
          <div class="relative group">
            <!-- [변경 1] div -> button 태그로 변경 -->
            <!-- [변경 2] pointer-events-none 제거 (클릭 가능하게) -->
            <!-- [변경 3] @click="goSearch" 이벤트 추가 -->
            <button 
              @click="goSearch"
              class="absolute inset-y-0 left-0 pl-3 flex items-center cursor-pointer"
              type="button"
              aria-label="검색하기"
            >
              <span class="material-symbols-outlined text-gray-400 group-focus-within:text-primary transition-colors hover:text-primary">
                search
              </span>
            </button>
            
            <input
              v-model="searchQuery"
              @keyup.enter="goSearch"
              type="text"
              placeholder="제목, 작가 검색"
              class="w-full bg-gray-50 border border-gray-200 text-sm rounded-full pl-10 pr-4 py-2 focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all shadow-sm"
            />
          </div>
        </div>


        <!-- 3. Nav Links (오른쪽) -->
        <nav class="flex items-center gap-3 shrink-0">
          <!-- 홈 버튼은 로고가 있으니 선택적으로 제거 가능하나 유지 -->
          <router-link to="/" class="text-sm font-semibold text-text-muted hover:text-primary transition-colors hidden md:block">홈</router-link>
          
          <template v-if="!authStore.isAuthenticated">
            <router-link to="/login" class="text-sm font-semibold text-primary hover:underline whitespace-nowrap">로그인</router-link>
            <router-link to="/signup" class="px-4 py-2 text-sm font-bold text-white bg-primary rounded-full hover:bg-opacity-90 shadow-sm transition-transform active:scale-95 hidden sm:block">회원가입</router-link>
          </template>
          
          <template v-else>
            <span class="text-sm text-gray-600 hidden md:inline-block">{{ authStore.user?.username }}님</span>
            <button @click="handleLogout" class="px-4 py-1.5 text-xs font-bold text-white bg-primary rounded-full hover:bg-opacity-90 shadow-sm transition-transform active:scale-95 whitespace-nowrap">
              로그아웃
            </button>
          </template>
        </nav>
      </div>
    </header>

    <!-- Main Content -->
    <main class="w-full max-w-[1200px] mx-auto px-6 mt-8">
      <router-view />
    </main>
  </div>
</template>
