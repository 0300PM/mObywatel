<script setup lang="ts">
import { ref } from 'vue'
import { t } from '@/lib/i18n'
import { iconSvg } from '@/lib/icons'
import { rozpoznawanieDostepne, slucham } from '@/lib/speech'

const emituj = defineEmits<{
  (e: 'wyslij', tekst: string): void
  (e: 'mikrofon'): void
  (e: 'zdjecie'): void
}>()

const wpis = ref('')

function wyslij(): void {
  const tresc = wpis.value.trim()
  if (!tresc) return
  wpis.value = ''
  emituj('wyslij', tresc)
}
</script>

<template>
  <form class="flex shrink-0 items-center gap-2 px-4 pb-2 pt-1" @submit.prevent="wyslij">
    <button type="button" class="grid h-10 w-10 flex-none place-items-center rounded-full text-ink-2" :aria-label="t('Zrób zdjęcie dokumentu')" @click="emituj('zdjecie')">
      <span class="h-6 w-6" v-html="iconSvg('camera')" />
    </button>
    <input
      v-model="wpis"
      :placeholder="t('Co chcesz załatwić?')"
      enterkeyhint="send"
      :aria-label="t('Wiadomość')"
      class="h-11 min-w-0 flex-1 rounded-full bg-surface px-4 text-[15px] shadow-sm outline-none"
    />
    <button
      type="button"
      class="grid h-10 w-10 flex-none place-items-center rounded-full text-ink-2"
      :class="rozpoznawanieDostepne ? '' : 'opacity-60'"
      :aria-label="slucham ? t('Zatrzymaj słuchanie') : t('Powiedz')"
      :title="rozpoznawanieDostepne ? t('Powiedz') : t('Ta przeglądarka nie obsługuje rozpoznawania mowy')"
      @click="emituj('mikrofon')"
    >
      <span class="h-6 w-6" v-html="iconSvg('mic')" />
    </button>
    <button type="submit" class="grid h-10 w-10 flex-none place-items-center rounded-full bg-brand text-white" :aria-label="t('Wyślij')">
      <span class="h-5 w-5" v-html="iconSvg('send')" />
    </button>
  </form>
</template>
