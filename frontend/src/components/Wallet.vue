<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { dokumenty, osoba, sprawy, uklad } from '@/lib/portfel'
import type { Dokument } from '@/lib/types'
import { iconSvg } from '@/lib/icons'
import { otworzSkaner } from '@/lib/znak-flow'
import { otworzTemat, widok } from '@/lib/rozmowa'
import { t } from '@/lib/i18n'
import DocumentFace from './DocumentFace.vue'

const props = defineProps<{ token: number }>()

const emituj = defineEmits<{ (e: 'pokaz-dokument', id: string): void; (e: 'pokaz-sprawy'): void }>()

const aktywnaKarta = ref(0)
const przewijany = ref<HTMLElement | null>(null)

const karty = computed(() => dokumenty.value)

function klikKarty(id: string): void {
  if (widok.rozmowa) {
    widok.rozmowa = false
    return
  }
  emituj('pokaz-dokument', id)
}

function tlo(d: Dokument): Record<string, string> {
  return { backgroundImage: `url(${d.img})` }
}

function akcje(d: Dokument): { ikona: 'scan' | 'doc' | 'shield' | 'coin' | 'clock' | 'car' | 'dots'; etykieta: string; run: () => void }[] {
  const baza: { ikona: 'scan' | 'doc' | 'shield' | 'coin' | 'clock' | 'car' | 'dots'; etykieta: string; run: () => void }[] = [
    { ikona: 'scan', etykieta: 'Potwierdź dane', run: () => void otworzSkaner({ dokument: d.id }) },
    { ikona: 'doc', etykieta: 'Szczegóły', run: () => emituj('pokaz-dokument', d.id) }
  ]
  const kontekst: Record<string, { ikona: 'shield' | 'coin' | 'clock' | 'car'; etykieta: string; temat: string }> = {
    dowod: { ikona: 'shield', etykieta: 'Zastrzeż PESEL', temat: 'Zastrzeż mój PESEL' },
    kdr: { ikona: 'coin', etykieta: 'Partnerzy KDR', temat: 'Gdzie mogę użyć Karty Dużej Rodziny?' },
    leg: { ikona: 'coin', etykieta: 'Ulgi studenta', temat: osoba.value.ask.leg ?? 'Opowiedz mi o legitymacji' },
    pj: { ikona: 'clock', etykieta: 'Punkty karne', temat: 'Ile mam punktów karnych?' },
    auto: { ikona: 'car', etykieta: 'OC i badanie', temat: osoba.value.ask.auto ?? 'Kiedy kończy się OC?' }
  }
  const dodatkowa = kontekst[d.id]
  if (dodatkowa) baza.push({ ikona: dodatkowa.ikona, etykieta: dodatkowa.etykieta, run: () => otworzTemat(dodatkowa.temat) })
  baza.push({ ikona: 'dots', etykieta: t('Zapytaj'), run: () => otworzTemat(osoba.value.ask[d.id] ?? 'Opowiedz mi o tym dokumencie') })
  return baza
}

const biezaca = computed(() => karty.value[aktywnaKarta.value])

function sledzPrzewijanie(): void {
  const pojemnik = przewijany.value
  if (!pojemnik) return
  const poziomo = uklad.value === 'karuzela'
  const pierwsze = pojemnik.firstElementChild as HTMLElement | null
  if (!pierwsze) return
  const rozmiar = (poziomo ? pierwsze.offsetWidth : pierwsze.offsetHeight) + 12
  const indeks = Math.round((poziomo ? pojemnik.scrollLeft : pojemnik.scrollTop) / rozmiar)
  aktywnaKarta.value = Math.max(0, Math.min(karty.value.length - 1, indeks))
}

watch(uklad, () => {
  aktywnaKarta.value = 0
})
</script>

<template>
  <div class="flex min-h-0 flex-1 flex-col">
    <template v-if="uklad === 'stos'">
      <div class="relative mx-4 flex-1">
        <div
          v-for="(d, i) in karty"
          :key="d.id"
          role="button"
          tabindex="0"
          class="absolute inset-x-0 aspect-[3/2] cursor-pointer overflow-hidden rounded-[18px] bg-[#ccc] bg-cover bg-center text-white shadow-[0_6px_18px_-6px_rgba(15,25,60,.28)] transition-[top,transform] duration-500 active:brightness-95"
          :style="{ ...tlo(d), top: `${i * 56}px`, zIndex: i + 1 }"
          :aria-label="t(d.name)"
          @click="klikKarty(d.id)"
          @keydown.enter.prevent="klikKarty(d.id)"
          @keydown.space.prevent="klikKarty(d.id)"
        >
          <DocumentFace v-if="!widok.rozmowa" :dokument="d" :token="props.token" />
        </div>
      </div>
      <p class="px-6 pb-1 pt-2 text-center text-[12px] text-ink-3">{{ widok.rozmowa ? t('Dotknij stosu, aby wrócić do dokumentów') : t('Dotknij karty, aby ją otworzyć') }}</p>
    </template>

    <template v-else-if="uklad === 'karuzela' || uklad === 'pion'">
      <div
        ref="przewijany"
        class="scrollbar-none flex min-h-0 flex-1 gap-3 px-6"
        :class="uklad === 'pion' ? 'snap-y snap-mandatory flex-col overflow-y-auto px-8' : 'snap-x snap-mandatory overflow-x-auto'"
        @scroll.passive="sledzPrzewijanie()"
      >
        <div
          v-for="d in karty"
          :key="d.id"
          role="button"
          tabindex="0"
          class="relative aspect-[3/2] w-full max-w-[320px] flex-none snap-center cursor-pointer overflow-hidden rounded-[18px] bg-[#ccc] bg-cover bg-center text-white shadow-[0_6px_18px_-6px_rgba(15,25,60,.28)]"
          :style="tlo(d)"
          :aria-label="t(d.name)"
          @click="klikKarty(d.id)"
          @keydown.enter.prevent="klikKarty(d.id)"
          @keydown.space.prevent="klikKarty(d.id)"
        >
          <DocumentFace :dokument="d" :token="props.token" />
        </div>
      </div>
      <div class="flex justify-center gap-1.5 py-2">
        <i v-for="(d, i) in karty" :key="d.id" class="h-1.5 w-1.5 rounded-full" :class="i === aktywnaKarta ? 'bg-ink' : 'bg-ink-3/40'" />
      </div>
      <div v-if="biezaca" class="grid grid-cols-4 gap-1 px-4 pb-2">
        <button
          v-for="a in akcje(biezaca).slice(0, 4)"
          :key="a.etykieta"
          type="button"
          class="flex flex-col items-center gap-1 rounded-xl bg-surface px-1 py-2 text-[10.5px] font-medium leading-tight text-ink-2"
          @click="a.run()"
        >
          <span class="h-[18px] w-[18px] text-brand" v-html="iconSvg(a.ikona)" />
          {{ a.etykieta }}
        </button>
      </div>
    </template>

    <template v-else-if="uklad === 'lista'">
      <div class="flex min-h-0 flex-1 flex-col gap-2 overflow-y-auto px-4">
        <button
          v-for="d in karty"
          :key="d.id"
          type="button"
          class="relative flex flex-none items-center gap-3 overflow-hidden rounded-2xl bg-white/60 bg-[length:cover] bg-center p-3 text-left"
          :style="{ backgroundImage: `url(${d.strip})` }"
          @click="klikKarty(d.id)"
        >
          <span class="h-12 w-12 flex-none overflow-hidden rounded-xl bg-slate-200 bg-cover bg-[50%_30%]" :style="{ backgroundImage: `url(assets/foto-${osoba.id}.jpg)` }" />
          <span class="min-w-0 flex-1">
            <b class="block truncate text-[15px] font-semibold">{{ t(d.name) }}</b>
            <small class="block truncate text-[12.5px] text-ink-2">{{ d.who ?? d.holder }}</small>
          </span>
          <span
            class="flex-none rounded-full px-2 py-0.5 text-[11px] font-semibold"
            :class="d.alert ? 'bg-brand-wash text-brand' : 'text-ink-3'"
          >{{ d.alert ? t(d.alert) : t(d.sub) }}</span>
        </button>
      </div>
    </template>

    <template v-else>
      <div class="grid min-h-0 flex-1 grid-cols-2 content-start gap-3 overflow-y-auto px-4 pb-2">
        <div
          v-for="d in karty"
          :key="d.id"
          role="button"
          tabindex="0"
          class="cursor-pointer text-left"
          @click="klikKarty(d.id)"
          @keydown.enter.prevent="klikKarty(d.id)"
          @keydown.space.prevent="klikKarty(d.id)"
        >
          <span class="relative block aspect-[3/2] overflow-hidden rounded-xl bg-[#ccc] bg-cover bg-center text-white" :style="tlo(d)">
            <DocumentFace :dokument="d" :token="props.token" />
          </span>
          <span class="mt-1 block truncate text-[12px] font-semibold">{{ t(d.name) }}</span>
          <span class="flex items-center gap-1 text-[11px]" :class="d.alert ? 'text-brand' : 'text-ok'">
            <span class="h-3 w-3" v-html="iconSvg(d.alert ? 'alert' : 'check')" />
            {{ d.alert ? t(d.alert) : t('Dokument ważny') }}
          </span>
        </div>
      </div>
    </template>

    <section class="shrink-0 px-4 pb-1" :aria-label="t('Przypomnienia')">
      <button
        type="button"
        class="flex w-full items-center gap-3 rounded-2xl bg-surface px-3 py-2 text-left shadow-[0_1px_2px_rgba(15,25,60,.06)]"
        :aria-label="t(`Do załatwienia: ${sprawy.length} sprawy`)"
        @click="emituj('pokaz-sprawy')"
      >
        <span class="grid h-6 w-6 flex-none place-items-center rounded-full bg-brand text-[12px] font-bold text-white">{{ sprawy.length }}</span>
        <span class="min-w-0 flex-1">
          <b class="block truncate text-[14px] font-semibold">{{ t(sprawy[0]?.h ?? '') }}</b>
          <small class="block truncate text-[12px] text-ink-2"><em class="not-italic text-brand">{{ t(sprawy[0]?.d ?? '') }}</em> {{ t(`· i ${sprawy.length - 1} inne sprawy`) }}</small>
        </span>
        <span class="h-4 w-4 flex-none text-ink-3" v-html="iconSvg('chev')" />
      </button>
    </section>
  </div>
</template>
