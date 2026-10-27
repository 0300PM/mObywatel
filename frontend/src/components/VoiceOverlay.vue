<script setup lang="ts">
import { computed } from 'vue'
import { glos, dotknijMikrofonu, zakonczGlos } from '@/lib/rozmowa'
import { t } from '@/lib/i18n'
import { iconSvg } from '@/lib/icons'
import DataCard from './DataCard.vue'

const emituj = defineEmits<{ (e: 'pisac'): void }>()

const STANY: Record<string, string> = {
  idle: 'Dotknij, aby mówić',
  listen: 'Słucham…',
  stt: 'Rozpoznaję…',
  think: 'Sprawdzam…',
  speak: 'Mówię. Dotknij, aby przerwać',
  wait: 'Potwierdź na karcie'
}

const opis = computed(() => glos.komunikat || t(STANY[glos.stan] ?? STANY.idle))
const karta = computed(() => {
  const ostatnia = [...glos.scena].reverse().find((m) => m.karta)
  return ostatnia?.karta ?? null
})
</script>

<template>
  <div class="absolute inset-0 z-40 flex flex-col bg-bg/95 backdrop-blur-sm" :data-stan="glos.stan">
    <div class="flex-1 overflow-y-auto px-4 pt-4">
      <div v-if="karta" class="mx-auto max-w-[330px]">
        <DataCard :karta="karta" :przyciski="false" />
      </div>
    </div>

    <div class="shrink-0 px-6 pb-6 pt-2 text-center">
      <p v-if="glos.uslyszane" class="mb-1 text-[14px] leading-5 text-ink-2">„{{ glos.uslyszane }}”</p>
      <p class="mb-3 text-[15px] leading-5 text-ink-2">{{ opis }}</p>
      <button
        type="button"
        class="relative mx-auto grid h-[92px] w-[92px] place-items-center rounded-full bg-brand text-white shadow-lg transition-transform active:scale-95"
        :aria-label="t(STANY[glos.stan] ?? STANY.idle)"
        @click="dotknijMikrofonu()"
      >
        <span
          v-if="glos.stan === 'listen'"
          class="anim-tchnienie absolute inset-0 rounded-full ring-4 ring-brand/30"
        />
        <span class="h-9 w-9" v-html="iconSvg('mic', 1.8)" />
      </button>
      <div class="mt-4 flex items-center justify-center gap-4 text-[13px] text-ink-2">
        <button type="button" class="flex items-center gap-1.5 rounded-full px-3 py-1.5" @click="emituj('pisac')">
          <span class="h-4 w-4" v-html="iconSvg('doc')" />
          {{ t('Pisz zamiast mówić') }}
        </button>
        <button type="button" class="rounded-full px-3 py-1.5 font-semibold text-brand" @click="zakonczGlos()">
          {{ t('Zakończ') }}
        </button>
      </div>
    </div>
  </div>
</template>
