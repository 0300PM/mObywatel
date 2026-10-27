<script setup lang="ts">
import { computed } from 'vue'
import type { Wiadomosc } from '@/lib/types'
import { iconSvg } from '@/lib/icons'
import { qrSvg } from '@/lib/qr'
import { t } from '@/lib/i18n'
import DataCard from './DataCard.vue'

const props = defineProps<{ wiadomosc: Wiadomosc }>()

const emituj = defineEmits<{
  (e: 'opcja', wartosc: string): void
  (e: 'przelacz', wartosc: string): void
  (e: 'dalej'): void
  (e: 'potwierdz', id: string): void
  (e: 'anuluj', id: string): void
}>()

const karta = computed(() => props.wiadomosc.karta)
const potwierdzenie = computed(() => props.wiadomosc.potwierdzenie)

function wybrana(opcja: string): boolean {
  return props.wiadomosc.wybrane?.includes(opcja) ?? false
}
</script>

<template>
  <div v-if="wiadomosc.pisze" class="flex gap-1 py-2 pl-0.5" aria-label="Asystent pisze">
    <i class="anim-kropka h-[7px] w-[7px] rounded-full bg-ink-3" />
    <i class="anim-kropka h-[7px] w-[7px] rounded-full bg-ink-3 [animation-delay:.15s]" />
    <i class="anim-kropka h-[7px] w-[7px] rounded-full bg-ink-3 [animation-delay:.3s]" />
  </div>

  <div
    v-else-if="wiadomosc.autor === 'user'"
    class="anim-unos max-w-[84%] self-end rounded-[20px_20px_6px_20px] bg-brand px-3.5 py-2 text-[15.5px] leading-[22px] text-white [overflow-wrap:anywhere]"
  >
    {{ wiadomosc.tekst }}
  </div>

  <div
    v-else-if="wiadomosc.html"
    class="anim-unos max-w-[84%] self-start px-0.5 text-[15.5px] leading-[22px] [overflow-wrap:anywhere] [&_b]:font-semibold"
    v-html="wiadomosc.html"
  />

  <div v-else-if="wiadomosc.qr" class="anim-unos w-full rounded-[18px] bg-surface p-4 shadow-[0_1px_2px_rgba(15,25,60,.06)]">
    <div class="flex items-center gap-3 pb-3">
      <span class="grid h-[34px] w-[34px] place-items-center rounded-[10px] bg-brand-wash text-brand">
        <span class="h-[19px] w-[19px]" v-html="iconSvg('qr')" />
      </span>
      <p class="text-[16px] font-semibold">{{ wiadomosc.qr.title }}</p>
    </div>
    <div class="mx-auto w-[190px] text-ink">
      <span class="block" v-html="qrSvg(11)" />
    </div>
    <p v-if="wiadomosc.qr.code" class="pt-2 text-center font-mono text-[13px] tracking-widest text-ink-2">{{ wiadomosc.qr.code }}</p>
  </div>

  <DataCard
    v-else-if="karta"
    :karta="karta"
    :dzialanie="wiadomosc.stanPotwierdzenia ?? null"
    :przyciski="Boolean(potwierdzenie)"
    @potwierdz="potwierdzenie && emituj('potwierdz', potwierdzenie.id)"
    @anuluj="potwierdzenie && emituj('anuluj', potwierdzenie.id)"
  />

  <div v-if="wiadomosc.opcje?.length" class="anim-unos flex flex-wrap gap-2">
    <button
      v-for="o in wiadomosc.opcje"
      :key="o"
      type="button"
      class="rounded-full border border-line bg-surface px-3.5 py-2 text-[14px] font-medium transition-colors"
      :class="wybrana(o) ? 'border-brand bg-brand-wash text-brand' : 'text-ink'"
      @click="wiadomosc.wielokrotny ? emituj('przelacz', o) : emituj('opcja', o)"
    >
      {{ o }}
    </button>
    <button
      v-if="wiadomosc.pokazDalej"
      type="button"
      class="rounded-full bg-brand px-4 py-2 text-[14px] font-semibold text-white disabled:opacity-40"
      :disabled="!wiadomosc.wybrane?.length"
      @click="emituj('dalej')"
    >
      {{ t('Dalej') }}
    </button>
  </div>
</template>
