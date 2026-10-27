<script setup lang="ts">
import { nowaRozmowa, otworzRozmowe, rozmowyZHistoria, widok } from '@/lib/rozmowa'
import { iconSvg } from '@/lib/icons'
import { t } from '@/lib/i18n'

const godzina = (ts: number): string => new Date(ts).toLocaleTimeString('pl-PL', { hour: '2-digit', minute: '2-digit' })

function wybierz(id: number): void {
  otworzRozmowe(id)
}
</script>

<template>
  <div class="absolute inset-0 z-30 flex flex-col justify-end">
    <button type="button" class="absolute inset-0 bg-ink/35" :aria-label="t('Zamknij')" @click="widok.historia = false" />
    <div class="relative max-h-[72%] overflow-y-auto rounded-t-[26px] bg-bg pb-4">
      <div class="mx-auto mb-2 mt-2 h-1 w-10 rounded-full bg-line" />
      <div class="flex items-center gap-3 px-5 pb-2">
        <h2 class="flex-1 text-[19px] font-bold tracking-[-0.02em]">{{ t('Rozmowy') }}</h2>
        <button type="button" class="rounded-full bg-surface px-3 py-1.5 text-[13px] font-semibold text-brand" @click="nowaRozmowa(); widok.historia = false">
          + {{ t('Nowa rozmowa') }}
        </button>
      </div>
      <div class="px-3">
        <p v-if="!rozmowyZHistoria().length" class="px-2 py-6 text-center text-[14px] text-ink-3">
          {{ t('Tu pojawią się Twoje rozmowy.') }}
        </p>
        <button
          v-for="r in rozmowyZHistoria()"
          :key="r.id"
          type="button"
          class="mb-1 flex w-full items-start gap-3 rounded-2xl px-2.5 py-2.5 text-left"
          :class="r.nieprzeczytana ? 'bg-surface' : ''"
          @click="wybierz(r.id)"
        >
          <span class="grid h-8 w-8 flex-none place-items-center rounded-full bg-brand-wash text-brand">
            <span class="h-4 w-4" v-html="iconSvg(r.ikona)" />
          </span>
          <span class="min-w-0 flex-1">
            <b class="block truncate text-[14.5px] font-semibold">{{ r.tytul }}</b>
            <small class="block truncate text-[12.5px] text-ink-2">{{ r.ostatnia }}</small>
          </span>
          <span class="flex flex-none flex-col items-end gap-1">
            <time class="text-[11.5px] text-ink-3">{{ godzina(r.czas) }}</time>
            <i v-if="r.nieprzeczytana" class="h-2 w-2 rounded-full bg-brand" />
          </span>
        </button>
      </div>
    </div>
  </div>
</template>
