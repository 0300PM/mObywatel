<script setup lang="ts">
import { iconSvg } from '@/lib/icons'
</script>

<template>
  <div class="absolute inset-0 z-50 grid place-items-center bg-ink/70 backdrop-blur-sm">
    <div class="flex flex-col items-center gap-2 rounded-3xl bg-surface px-8 py-7 text-center">
      <span class="grid h-14 w-14 place-items-center rounded-2xl bg-bg text-brand">
        <span class="h-8 w-8" v-html="iconSvg('id', 1.9)" />
      </span>
      <span class="text-[15px] font-semibold">Face ID</span>
    </div>
  </div>
</template>
