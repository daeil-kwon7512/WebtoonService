<!-- src/components/WebtoonCard.vue -->
<template>
  <div class="group flex flex-col gap-3">
    <!-- 포스터 -->
    <div
      class="relative w-[180px] rounded-xl overflow-hidden shadow-md
            group-hover:shadow-lg group-hover:-translate-y-1 transition-all
            duration-300 bg-gray-100"
    >
      <a :href="toon.url" target="_blank" class="block w-full h-full">
        <img
          :src="toon.thumbnail"
          :alt="toon.title"
          class="w-full h-[240px] object-cover transition-transform duration-500 group-hover:scale-105"
          loading="lazy"
        />
      </a>

      <!-- 즐겨찾기 -->
      <button
        @click.stop="$emit('toggle-favorite', toon)"
        :class="[
          'absolute top-2 right-2 p-2 rounded-full backdrop-blur-md shadow-sm transition-all duration-200 z-10',
          toon.is_favorited
            ? 'bg-yellow-400 text-white'
            : 'bg-black/30 text-white/70 hover:bg-black/50',
        ]"
      >
        <span
          class="material-symbols-outlined text-[20px] block"
          style="font-variation-settings: 'FILL' 1;"
        >
          star
        </span>
      </button>
    </div>

    <!-- 제목 + 작가 -->
    <div>
      <h3
        class="text-sm font-bold text-text-main leading-tight truncate group-hover:text-primary transition-colors"
      >
        {{ toon.title }}
      </h3>
      <p
        v-if="toon.authors_display"
        class="mt-1 text-xs text-text-muted truncate"
      >
        {{ toon.authors_display }}
      </p>
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  toon: {
    type: Object,
    required: true,
  },
})
</script>
