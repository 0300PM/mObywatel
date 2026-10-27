<script setup lang="ts">
import { UKLADY, idOsoby, osoby, uklad, ustawUklad, zmienOsobe, zdjecieOsoby } from '@/lib/portfel'
import { widok } from '@/lib/rozmowa'
import { iconSvg } from '@/lib/icons'
import { t } from '@/lib/i18n'
import type { WariantUkladu } from '@/lib/types'

function wybierzUklad(id: WariantUkladu): void {
  ustawUklad(id)
  widok.menu = false
}

function wybierzOsobe(id: string): void {
  if (id === idOsoby.value) {
    widok.menu = false
    return
  }
  zmienOsobe(id)
}
</script>

<template>
  <div class="absolute inset-0 z-30 flex flex-col justify-end">
    <button type="button" class="absolute inset-0 bg-ink/35" :aria-label="t('Zamknij')" @click="widok.menu = false" />
    <div class="relative max-h-[82%] overflow-y-auto rounded-t-[26px] bg-surface pb-5">
      <div class="mx-auto mb-2 mt-2 h-1 w-10 rounded-full bg-line" />
      <p class="px-5 py-1 text-[12px] font-semibold uppercase tracking-wide text-ink-3">{{ t('Układ dokumentów') }}</p>
      <div class="px-2">
        <button
          v-for="l in UKLADY"
          :key="l.id"
          type="button"
          class="flex w-full items-start gap-3 rounded-2xl px-3 py-2.5 text-left"
          :class="l.id === uklad ? 'bg-bg' : ''"
          @click="wybierzUklad(l.id)"
        >
          <span class="min-w-0 flex-1">
            <b class="block text-[14.5px] font-semibold">{{ t(l.nazwa) }}</b>
            <small class="block text-[12.5px] text-ink-2">{{ t(l.opis) }}</small>
          </span>
          <span v-if="l.id === uklad" class="h-4 w-4 flex-none text-ok" v-html="iconSvg('check')" />
        </button>
      </div>

      <p class="px-5 pb-1 pt-3 text-[12px] font-semibold uppercase tracking-wide text-ink-3">{{ t('Osoba w pokazie') }}</p>
      <div class="flex gap-2 overflow-x-auto px-3 pb-2">
        <button
          v-for="o in osoby"
          :key="o.id"
          type="button"
          class="w-[104px] flex-none rounded-2xl p-2 text-center"
          :class="o.id === idOsoby ? 'bg-bg ring-1 ring-line' : ''"
          :aria-label="`${o.imie} ${o.nazwisko}, ${o.opis}`"
          @click="wybierzOsobe(o.id)"
        >
          <span class="mx-auto block h-12 w-12 rounded-full bg-slate-200 bg-cover bg-[50%_25%]" :style="{ backgroundImage: `url(${zdjecieOsoby(o.id)})` }" />
          <b class="mt-1.5 block text-[13px]">{{ o.imie }}</b>
          <small class="block truncate text-[11.5px] text-ink-3">{{ o.opis.split(',')[0] }}</small>
        </button>
      </div>
    </div>
  </div>
</template>
