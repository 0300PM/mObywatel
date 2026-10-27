<script setup lang="ts">
import { computed } from 'vue'
import type { KartaDanych } from '@/lib/types'
import { iconSvg } from '@/lib/icons'
import { svg as sylwetkaSvg } from '@/lib/sylwetki'
import { para, t } from '@/lib/i18n'

const props = defineProps<{
  karta: KartaDanych
  dzialanie?: 'czeka' | 'ok' | 'anulowano' | null
  przyciski?: boolean
}>()

const emituj = defineEmits<{ (e: 'potwierdz'): void; (e: 'anuluj'): void }>()

const ton = computed(() => props.karta.tone ?? '')
const rysunek = computed(() => (props.karta.pojazd?.model ? sylwetkaSvg(props.karta.pojazd.model, props.karta.pojazd.kolor ?? '') : ''))
</script>

<template>
  <div class="anim-unos w-full overflow-hidden rounded-[18px] bg-surface shadow-[0_1px_2px_rgba(15,25,60,.06)]">
    <div class="flex items-center gap-3 px-4 pb-2.5 pt-3.5">
      <span
        class="grid h-[34px] w-[34px] flex-none place-items-center rounded-[10px]"
        :class="ton === 'ok' ? 'bg-ok-wash text-ok' : ton === 'warn' ? 'bg-warn-wash text-warn' : 'bg-brand-wash text-brand'"
      >
        <span class="h-[19px] w-[19px]" v-html="iconSvg(karta.icon ?? 'doc')" />
      </span>
      <p class="text-[16px] font-semibold leading-[21px] tracking-[-0.01em]">{{ t(karta.title ?? '') }}</p>
      <span v-if="dzialanie === 'ok'" class="ml-auto text-[12px] font-semibold text-ok">{{ t('Potwierdzone') }}</span>
    </div>

    <div v-if="rysunek" class="mx-4 mb-2 flex items-center gap-2 rounded-xl bg-bg p-2">
      <span class="h-10 flex-1" v-html="rysunek" />
      <span v-if="karta.pojazd?.nr" class="flex flex-none items-center overflow-hidden rounded border border-ink/80 text-[11px] font-bold">
        <i class="bg-blue-700 px-1 py-0.5 not-italic text-white">PL</i>
        <b class="px-1.5 py-0.5">{{ karta.pojazd.nr }}</b>
      </span>
    </div>

    <div v-if="karta.body" class="px-4 pb-3 text-[14.5px] leading-[21px]" v-html="t(karta.body)" />

    <div v-if="karta.rows?.length" class="px-4 pb-1">
      <div v-for="r in karta.rows" :key="r[0] + r[1]" class="flex justify-between gap-4 border-t border-line py-[9px] text-[14px] leading-[19px]">
        <span class="flex-none text-ink-2">{{ para(r[0], r[1]).etykieta }}</span>
        <b class="min-w-0 text-right font-medium [overflow-wrap:anywhere]">{{ para(r[0], r[1]).wartosc }}</b>
      </div>
    </div>

    <div v-if="karta.flag" class="mx-4 mb-3 mt-1 rounded-xl bg-warn-wash px-3 py-2.5 text-[13.5px] leading-[19px] text-warn">{{ t(karta.flag) }}</div>
    <div v-if="karta.note" class="mx-4 mb-3 text-[13px] leading-[18px] text-ink-2">{{ t(karta.note) }}</div>

    <div v-if="przyciski && dzialanie === 'czeka'" class="flex gap-2 px-4 pb-4 pt-1.5">
      <button type="button" class="h-12 flex-none rounded-[14px] bg-bg px-[18px] font-semibold" @click="emituj('anuluj')">{{ t('Anuluj') }}</button>
      <button type="button" class="h-12 flex-1 rounded-[14px] bg-brand font-semibold tracking-[-0.01em] text-white active:bg-brand-dark" @click="emituj('potwierdz')">
        {{ t(karta.label ?? 'Potwierdź') }}
      </button>
    </div>

    <div v-if="karta.source" class="flex items-center gap-1.5 border-t border-line px-4 pb-3 pt-2.5 text-[12px] text-ink-3">
      <span class="h-[13px] w-[13px]" v-html="iconSvg('db')" />
      {{ t(karta.source) }}
    </div>
  </div>
</template>
