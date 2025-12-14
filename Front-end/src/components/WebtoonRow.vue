<!-- src/components/WebtoonRow.vue -->
<template>
  <section class="mb-10">
    <!-- 섹션 타이틀 -->
    <div class="flex items-center justify-between mb-4">
      <h2 class="text-lg font-bold text-text-main">
        {{ title }}
      </h2>
      <button
        v-if="showMore"
        class="text-xs text-text-muted hover:text-primary"
      >
        모두보기
      </button>
    </div>

    <!-- 1) 6개 이하: 가운데 정렬 고정 레이아웃 -->
    <div
      v-if="items.length <= 6"
      class="flex justify-center gap-6"
    >
      <WebtoonCard
        v-for="toon in items"
        :key="toon.id"
        :toon="toon"
        @toggle-favorite="$emit('toggle-favorite', $event)"
      />
    </div>

    <!-- 2) 7개 이상: 가로 스크롤 + (데스크탑) 좌우 화살표 -->
    <div v-else class="relative">
      <!-- 왼쪽 화살표 -->
      <button
        @click="scrollLeft"
        class="hidden md:flex absolute left-0 top-1/2 -translate-y-1/2 z-10
               w-8 h-8 items-center justify-center rounded-full bg-white/80 shadow
               text-gray-700 hover:bg-white"
      >
        ‹
      </button>

      <!-- 가로 슬라이드 영역 -->
      <div
        ref="scrollContainer"
        class="flex gap-4 overflow-x-auto pb-2 scroll-smooth"
      >
        <WebtoonCard
          v-for="toon in items"
          :key="toon.id"
          :toon="toon"
          @toggle-favorite="$emit('toggle-favorite', $event)"
        />
      </div>

      <!-- 오른쪽 화살표 -->
      <button
        @click="scrollRight"
        class="hidden md:flex absolute right-0 top-1/2 -translate-y-1/2 z-10
               w-8 h-8 items-center justify-center rounded-full bg-white/80 shadow
               text-gray-700 hover:bg-white"
      >
        ›
      </button>
    </div>
  </section>
</template>

<script setup>
import { ref } from 'vue'
import WebtoonCard from '@/components/WebtoonCard.vue'

const props = defineProps({
  title: { type: String, required: true },
  items: { type: Array, required: true },
  showMore: { type: Boolean, default: false },
})

const scrollContainer = ref(null)

// 카드 폭 + 여백 감안해서 한 번에 3장 정도 이동
const SCROLL_STEP = 180 * 3

const scrollLeft = () => {
  if (!scrollContainer.value) return
  scrollContainer.value.scrollBy({ left: -SCROLL_STEP, behavior: 'smooth' })
}

const scrollRight = () => {
  if (!scrollContainer.value) return
  scrollContainer.value.scrollBy({ left: SCROLL_STEP, behavior: 'smooth' })
}
</script>
