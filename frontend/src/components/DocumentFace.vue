<script setup lang="ts">
import { computed } from 'vue'
import type { Dokument } from '@/lib/types'
import { svgZnaku } from '@/lib/znak'
import { svg as sylwetkaSvg } from '@/lib/sylwetki'
import { daneWidoczne, pokazDane } from '@/lib/ui'
import { osoba } from '@/lib/portfel'
import { otworzPrzyjmowanie } from '@/lib/znak-flow'
import { para, t } from '@/lib/i18n'

const props = defineProps<{ dokument: Dokument; token: number }>()

const czyPojazd = computed(() => Boolean(props.dokument.plate))
const krotkieImie = computed(() => osoba.value.imie)
const pelneImie = computed(() => props.dokument.holder)

const komorka = (p: string[]): { etykieta: string; wartosc: string } => para(p[0], p[1])

const rysunek = computed(() => {
  const d = props.dokument
  if (!d.model) return ''
  return sylwetkaSvg(d.model, d.kolor ?? '')
})

const drugiPojazd = computed(() => {
  const drugi = props.dokument.more?.[0]
  return drugi?.model ? sylwetkaSvg(drugi.model, drugi.kolor ?? '', { shadow: false }) : ''
})
</script>

<template>
  <span class="flex h-full flex-col justify-between p-4 text-left text-white drop-shadow-sm">
    <span class="text-[13px] font-semibold tracking-wide opacity-95">{{ t(dokument.name) }}</span>

    <template v-if="czyPojazd">
      <span class="flex items-end gap-2">
        <span v-if="drugiPojazd" class="h-8 w-16 opacity-90" v-html="drugiPojazd" />
        <span class="h-12 flex-1" v-html="rysunek" />
      </span>
      <span class="flex items-center gap-3">
        <span class="flex items-center overflow-hidden rounded-md border border-white/70 text-[12px] font-bold leading-none">
          <i class="bg-blue-700 px-1 py-1 not-italic">PL</i>
          <b class="px-1.5 py-1">{{ dokument.plate }}</b>
        </span>
        <span class="min-w-0">
          <span class="block truncate text-[12px] font-semibold">{{ dokument.holder }}</span>
          <span class="flex flex-wrap gap-x-3 text-[10.5px] opacity-90">
            <span v-for="p in dokument.f" :key="p[0]">{{ komorka(p).etykieta }}: {{ komorka(p).wartosc }}</span>
          </span>
        </span>
      </span>
    </template>

    <template v-else>
      <span class="flex items-end justify-between gap-3">
        <span class="flex items-end gap-2">
          <button
            v-if="dokument.id === 'dowod'"
            type="button"
            class="grid h-14 w-14 place-items-center rounded-full bg-white p-1 shadow"
            :aria-label="t('Mój znak mObywatela: powiększ, aby przyjąć dane')"
            @click.stop.prevent="otworzPrzyjmowanie({ cel: 'tozsamosc' })"
          >
            <span class="block h-full w-full" v-html="svgZnaku(token)" />
          </button>
          <span
            v-if="dokument.photo"
            class="block h-[70px] w-[54px] rounded-md bg-slate-200 bg-cover bg-[50%_30%] ring-1 ring-white/40"
            role="img"
            :aria-label="`Zdjęcie: ${osoba.imie} ${osoba.nazwisko}`"
            :style="{ backgroundImage: `url(assets/foto-${osoba.id}.jpg)` }"
          />
        </span>
        <span class="min-w-0 text-right">
          <span class="block truncate text-[13px] font-bold uppercase tracking-wide">
            {{ dokument.id === 'dowod' && !daneWidoczne ? krotkieImie : pelneImie }}
          </span>
          <span class="mt-0.5 flex flex-wrap justify-end gap-x-2.5 text-[10.5px] leading-4 opacity-90">
            <span v-for="p in dokument.f" :key="p[0]">{{ komorka(p).etykieta }}: {{ komorka(p).wartosc }}</span>
          </span>
        </span>
      </span>

      <button
        v-if="dokument.id === 'dowod' && !daneWidoczne"
        type="button"
        class="self-end rounded-full bg-white/20 px-2.5 py-1 text-[11px] font-semibold backdrop-blur"
        @click.stop.prevent="pokazDane()"
      >
        {{ t('Pokaż dane') }}
      </button>
    </template>
  </span>
</template>
