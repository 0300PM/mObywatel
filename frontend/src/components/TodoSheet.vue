<script setup lang="ts">
import { sprawy } from '@/lib/portfel'
import { otworzTemat, widok } from '@/lib/rozmowa'
import { iconSvg } from '@/lib/icons'
import { t } from '@/lib/i18n'
</script>

<template>
  <div class="absolute inset-0 z-30 flex flex-col justify-end">
    <button type="button" class="absolute inset-0 bg-ink/35" :aria-label="t('Zamknij')" @click="widok.todo = false" />
    <div class="relative max-h-[78%] overflow-y-auto rounded-t-[26px] bg-bg pb-5">
      <div class="mx-auto mb-2 mt-2 h-1 w-10 rounded-full bg-line" />
      <div class="flex items-center gap-3 px-5 pb-2">
        <h2 class="flex-1 text-[19px] font-bold tracking-[-0.02em]">{{ t('Do załatwienia') }}</h2>
        <button type="button" class="grid h-8 w-8 place-items-center rounded-full text-ink-2" :aria-label="t('Zamknij')" @click="widok.todo = false">
          <span class="h-4 w-4" v-html="iconSvg('x', 2)" />
        </button>
      </div>
      <div class="px-4">
        <button
          v-for="x in sprawy"
          :key="x.h"
          type="button"
          class="mb-2 flex w-full items-start gap-3 rounded-2xl bg-surface px-3.5 py-3 text-left"
          @click="otworzTemat(x.q ?? x.h)"
        >
          <span class="grid h-[26px] w-[26px] flex-none place-items-center rounded-lg bg-brand-wash text-brand">
            <span class="h-4 w-4" v-html="iconSvg(x.i)" />
          </span>
          <span class="min-w-0 flex-1">
            <b class="block text-[14.5px] font-semibold leading-[18px]">{{ t(x.h) }}</b>
            <small class="mt-0.5 block text-[12.5px]" :class="x.u ? 'font-semibold text-brand' : 'text-ink-2'">{{ t(x.d) }}</small>
            <em v-if="x.s" class="mt-1 block text-[12px] not-italic leading-4 text-ink-3">{{ t(x.s) }}</em>
          </span>
          <span class="mt-1 h-4 w-4 flex-none text-ink-3" v-html="iconSvg('chev')" />
        </button>
        <button
          type="button"
          class="w-full rounded-2xl bg-surface px-4 py-3 text-left text-[15px] font-semibold text-brand"
          @click="otworzTemat('Co mam do załatwienia?')"
        >
          {{ t('Zapytaj asystenta o wszystkie sprawy') }}
        </button>
      </div>
    </div>
  </div>
</template>
