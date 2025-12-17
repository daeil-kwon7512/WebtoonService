// src/router/index.js
import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import LoginView from '../views/LoginView.vue'   
import SignupView from '../views/SignupView.vue' 
import SurveyView from '../views/SurveyView.vue' // [추가]
import SearchView  from '@/views/SearchView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView
    },
    {
      path: '/login',
      name: 'login',
      component: LoginView
    },
    {
      path: '/signup',
      name: 'signup',
      component: SignupView
    },
    // [추가] 설문조사 페이지 라우트
    {
      path: '/survey',
      name: 'survey',
      component: SurveyView
    },
    {
      path: '/search',
      name: 'Search',
      component: SearchView,
    },
  ]
})

export default router
