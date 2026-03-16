<template>
  <div class="flex items-center gap-6 mb-8 h-full">
    <div
      class="w-24 h-24 bg-gradient-to-br from-orange-500 to-orange-600 rounded-2xl flex items-center justify-center text-4xl flex-shrink-0 view-transition-devicon"
    >
      {{ emoji }}
    </div>
    <div>
      <div class="text-4xl font-bold view-transition-devname">
        {{ name }}
      </div>
      <div class="text-xl text-orange-500 view-transition-devrole">
        {{ role }}
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
interface Props {
  name: string;
  role: string;
  emoji: string;
}

defineProps<Props>();
</script>
