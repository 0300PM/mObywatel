<script setup lang="ts">
import { computed, ref } from 'vue'
import { dokumenty, osoba, rodzaj } from '@/lib/portfel'
import { widok, otworzTemat } from '@/lib/rozmowa'
import { otworzSkaner } from '@/lib/znak-flow'
import { godzinaSekundy } from '@/lib/ui'
import { iconSvg } from '@/lib/icons'
import { para, t } from '@/lib/i18n'
import DocumentFace from './DocumentFace.vue'

defineProps<{ token: number }>()

const szczegoly = ref(false)

const dokument = computed(() => dokumenty.value.find((d) => d.id === widok.dokument) ?? null)

const szybkie = computed(() => {
  const d = dokument.value
  if (!d) return []
  if (d.id === 'dowod') {
    return [
      { ikona: 'scan' as const, etykieta: t('Potwierdź swoje dane'), run: () => void otworzSkaner({ dokument: 'dowod' }) },
      { ikona: 'id' as const, etykieta: t('Dane dowodu'), run: () => (szczegoly.value = !szczegoly.value) },
      { ikona: 'shield' as const, etykieta: t('Zastrzeż PESEL'), run: () => otworzTemat('Zastrzeż mój PESEL') },
      { ikona: 'dots' as const, etykieta: t('Zapytaj asystenta'), run: () => otworzTemat(osoba.value.ask.dowod ?? 'Opowiedz mi o tym dokumencie') }
    ]
  }
  return [
    { ikona: 'scan' as const, etykieta: t('Potwierdź dane'), run: () => void otworzSkaner({ dokument: d.id }) },
    { ikona: 'doc' as const, etykieta: t('Szczegóły'), run: () => (szczegoly.value = !szczegoly.value) },
    { ikona: 'shield' as const, etykieta: t('Zgubiony portfel'), run: () => otworzTemat(rodzaj('Zgubiłam portfel', 'Zgubiłem portfel')) },
    { ikona: 'dots' as const, etykieta: t('Zapytaj asystenta'), run: () => otworzTemat(osoba.value.ask[d.id] ?? 'Opowiedz mi o tym dokumencie') }
  ]
})

function zamknij(): void {
  widok.dokument = null
  szczegoly.value = false
}
</script>

<template>
  <div v-if="dokument" class="absolute inset-0 z-30 flex flex-col bg-bg">
    <div class="flex h-[52px] shrink-0 items-center gap-2 px-4">
      <button type="button" class="flex items-center gap-1 text-[15px] font-semibold text-brand" @click="zamknij">
        <span class="h-4 w-4" v-html="iconSvg('back', 2)" />
        {{ t('Wróć') }}
      </button>
      <b class="mx-auto text-[15px]">{{ t(dokument.name) }}</b>
      <span class="w-12" />
    </div>

    <div class="scrollbar-none flex-1 overflow-y-auto px-4 pb-6">
      <p class="pb-2 text-center text-[12px] text-ink-3">{{ t('Czas') }}: {{ godzinaSekundy }}</p>

      <div class="relative aspect-[3/2] overflow-hidden rounded-2xl bg-[#ccc] bg-cover bg-center text-white shadow-lg" :style="{ backgroundImage: `url(${dokument.img})` }">
        <DocumentFace :dokument="dokument" :token="token" />
      </div>
      <div class="mt-2 flex items-center gap-1.5 text-[13px] font-semibold" :class="dokument.alert ? 'text-brand' : 'text-ok'">
        <span class="h-4 w-4" v-html="iconSvg(dokument.alert ? 'alert' : 'check')" />
        {{ dokument.alert ? t(dokument.alert) : t('Dokument ważny') }}
      </div>
      <div class="mt-2 rounded-2xl bg-surface px-4">
        <div v-for="r in dokument.rows" :key="r[0]" class="flex justify-between gap-4 border-t border-line py-2.5 text-[14px] first:border-t-0">
          <span class="text-ink-2">{{ para(r[0], r[1]).etykieta }}</span>
          <b class="text-right font-medium">{{ para(r[0], r[1]).wartosc }}</b>
        </div>
      </div>

      <div class="mt-4 grid grid-cols-4 gap-2">
        <button
          v-for="q in szybkie"
          :key="q.etykieta"
          type="button"
          class="flex flex-col items-center gap-1.5 rounded-2xl bg-surface px-1 py-3 text-[11px] font-medium leading-tight text-ink-2"
          @click="q.run()"
        >
          <span class="h-5 w-5 text-brand" v-html="iconSvg(q.ikona)" />
          <span class="text-center">{{ q.etykieta }}</span>
        </button>
      </div>

      <div v-if="szczegoly" class="mt-3 rounded-2xl bg-surface px-4">
        <div v-for="r in dokument.rows" :key="r[0]" class="flex justify-between gap-4 border-t border-line py-2.5 text-[14px] first:border-t-0">
          <span class="text-ink-2">{{ para(r[0], r[1]).etykieta }}</span>
          <b class="text-right font-medium">{{ para(r[0], r[1]).wartosc }}</b>
        </div>
      </div>
    </div>
  </div>
</template>
