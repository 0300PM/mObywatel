<script setup lang="ts">
import { computed, nextTick, ref, watch } from 'vue'
import { dokumenty } from '@/lib/portfel'
import { aktywna, bladModelu, modelGotowy, powitanie, sugerowane, uslugi, widok, wyslij } from '@/lib/rozmowa'
import { t } from '@/lib/i18n'
import { iconSvg } from '@/lib/icons'
import ChatMessage from './ChatMessage.vue'

const emituj = defineEmits<{
  (e: 'potwierdz', id: string): void
  (e: 'anuluj', id: string): void
  (e: 'opcja', wartosc: string): void
  (e: 'przelacz', wartosc: string): void
  (e: 'dalej'): void
  (e: 'wroc'): void
}>()

const lista = ref<HTMLElement | null>(null)

const wiadomosci = computed(() => aktywna.value?.wiadomosci ?? [])
const pokazPusty = computed(() => wiadomosci.value.length === 0)

const komunikatModelu = computed(() => {
  if (bladModelu.value) return t('Model w Cloudflare nie odpowiedział. Sprawdź token i połączenie, potem spróbuj ponownie.')
  if (uslugi.value && !uslugi.value.agent) return uslugi.value.komunikat
  if (uslugi.value && !modelGotowy.value) return uslugi.value.komunikat
  return ''
})

const ostrzezeniaModelu = computed(() => uslugi.value?.ostrzezenia ?? [])

function przewinNaDol(plynnie = true): void {
  const el = lista.value
  if (!el) return
  if (typeof el.scrollTo === 'function') el.scrollTo({ top: el.scrollHeight, behavior: plynnie ? 'smooth' : 'auto' })
  else el.scrollTop = el.scrollHeight
}

watch(
  () => wiadomosci.value.length,
  async () => {
    await nextTick()
    przewinNaDol()
  }
)

watch(
  () => widok.rozmowa,
  async (otwarta) => {
    if (!otwarta) return
    await nextTick()
    przewinNaDol(false)
  }
)
</script>

<template>
  <div class="flex min-h-0 flex-1 flex-col">
    <div class="mx-4 mb-1.5 flex gap-1.5">
      <button
        v-for="d in dokumenty"
        :key="d.id"
        type="button"
        class="h-9 flex-1 rounded-lg bg-[#ccc] bg-cover bg-center shadow-sm transition-transform active:scale-95"
        :style="{ backgroundImage: `url(${d.img})` }"
        :aria-label="`Wróć do dokumentów: ${d.name}`"
        @click="emituj('wroc')"
      />
    </div>

    <div ref="lista" class="scrollbar-none flex min-h-0 flex-1 flex-col gap-2.5 overflow-y-auto px-4 pb-3 pt-2">
      <div v-if="pokazPusty" class="mt-auto">
        <h2 class="mb-1 text-[22px] font-bold leading-7 tracking-[-0.02em]">{{ powitanie() }}</h2>
        <p class="mb-3.5 text-[15px] leading-[21px] text-ink-2">
          {{ t('Załatwię sprawę urzędową, sprawdzę dane w rejestrach i pokażę dokument. Zanim cokolwiek wyślę, poproszę o potwierdzenie.') }}
        </p>
        <div v-if="komunikatModelu" class="mb-3 rounded-xl bg-warn-wash px-3 py-2.5 text-[13px] leading-[18px] text-warn">
          {{ komunikatModelu }}
        </div>
        <ul v-else-if="ostrzezeniaModelu.length" class="mb-3 space-y-1 rounded-xl bg-warn-wash px-3 py-2.5 text-[13px] leading-[18px] text-warn">
          <li v-for="tekst in ostrzezeniaModelu" :key="tekst">{{ tekst }}</li>
        </ul>
        <div class="overflow-hidden rounded-2xl bg-surface">
          <button
            v-for="s in sugerowane"
            :key="s[0]"
            type="button"
            class="flex w-full items-center gap-3 border-t border-line px-3.5 py-3 text-left text-[15px] first:border-t-0"
            @click="void wyslij(s[0])"
          >
            <span class="flex-1">
              {{ s[0] }}
              <small class="mt-px block text-[13px] text-ink-3">{{ s[1] }}</small>
            </span>
            <span class="h-4 w-4 flex-none text-ink-3" v-html="iconSvg('chev')" />
          </button>
        </div>
      </div>

      <template v-else>
        <p class="text-center text-[12px] leading-4 text-ink-3">{{ t('Odpowiada model z Cloudflare. Ważne informacje sprawdź na karcie sprawy.') }}</p>
        <ChatMessage
          v-for="m in wiadomosci"
          :key="m.id"
          :wiadomosc="m"
          @potwierdz="(id: string) => emituj('potwierdz', id)"
          @anuluj="(id: string) => emituj('anuluj', id)"
          @opcja="(w: string) => emituj('opcja', w)"
          @przelacz="(w: string) => emituj('przelacz', w)"
          @dalej="emituj('dalej')"
        />
      </template>
    </div>

  </div>
</template>
