<template>
  <div class="space-y-4 h-full flex flex-col justify-center">
    <div
      v-for="(item, index) in items"
      :key="index"
      class="flex items-start gap-4"
    >
      <span class="text-orange-500 text-2xl">{{ item.icon }}</span>
      <span>{{ item.text }}</span>
    </div>
  </div>
</template>

<script setup lang="ts">
interface DetailItem {
  icon: string;
  text: string;
}

interface Props {
  items: DetailItem[];
}

defineProps<Props>();
</script>
