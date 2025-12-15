// src/stores/webtoons.js
import { defineStore } from 'pinia'
import axios from '@/api/axios'

export const useWebtoonStore = defineStore('webtoons', {
  state: () => ({
    items: [],        // 전체 웹툰 목록
    favorites: [],    // 관심 웹툰 목록
    loading: false,
    error: null,
  }),

  getters: {
    // 성인 웹툰 제외 필터
    nonAdult(state) {
      return state.items.filter(w => !w.is_adult)
    },
  },

  actions: {
    async fetchWebtoons({ q = '' } = {}) {
      this.loading = true
      this.error = null
      try {
        const res = await axios.get('/api/webtoons/', {
          params: { q },
        })
        this.items = res.data.results
      } catch (err) {
        console.error(err)
        this.error = '웹툰 목록을 불러오지 못했습니다.'
      } finally {
        this.loading = false
      }
    },
    // 관심 웹툰 로드
    async fetchFavorites() {
      try {
        const res = await axios.get('/api/me/favorites/')
        this.favorites = res.data
      } catch (err) {
        console.error(err)
      }
    },

    // 관심 해제 시 리스트에서 제거
    removeFavorite(id) {
      this.favorites = this.favorites.filter(w => w.id !== id)
    },
  },
})
