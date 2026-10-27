<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref } from 'vue'
import { iconSvg } from '@/lib/icons'
import { t, wczytajJezyk } from '@/lib/i18n'
import { idOsoby, uklad } from '@/lib/portfel'
import {
  aktywna,
  dotknijMikrofonu,
  glos,
  nowaRozmowa,
  pobierzStanUslug,
  potwierdz,
  przygotujPowitanie,
  przelaczWielokrotny,
  uruchomGlos,
  uslugi,
  widok,
  wyslij,
  wyslijZdjecie,
  zakonczGlos,
  zatwierdzWielokrotny
} from '@/lib/rozmowa'
import { otworzSkaner } from '@/lib/znak-flow'
import { godzina } from '@/lib/ui'
import { rozpoznawanieDostepne, zatrzymajNasluch } from '@/lib/speech'
import Wallet from './components/Wallet.vue'
import ChatPanel from './components/ChatPanel.vue'
import VoiceOverlay from './components/VoiceOverlay.vue'
import Composer from './components/Composer.vue'
import DocumentSheet from './components/DocumentSheet.vue'
import TodoSheet from './components/TodoSheet.vue'
import HistorySheet from './components/HistorySheet.vue'
import MenuSheet from './components/MenuSheet.vue'
import FaceIdOverlay from './components/FaceIdOverlay.vue'
import SignOverlay from './components/SignOverlay.vue'

const token = ref(Math.floor(Math.random() * 65536))
const podpowiedzGlosu = ref(false)
let zegarTokenu: number | null = null
let zegarPodpowiedzi: number | null = null

function przejdzDoDokumentow(): void {
  if (glos.tryb) zakonczGlos()
  widok.rozmowa = false
  widok.historia = false
}

function otworzRozmowe(): void {
  przygotujPowitanie()
  widok.rozmowa = true
}

function wyslijTekst(tekst: string): void {
  otworzRozmowe()
  void wyslij(tekst)
}

function pokazPodpowiedzGlosu(): void {
  podpowiedzGlosu.value = true
  if (zegarPodpowiedzi !== null) window.clearTimeout(zegarPodpowiedzi)
  zegarPodpowiedzi = window.setTimeout(() => {
    podpowiedzGlosu.value = false
  }, 5000)
}

function klikMikrofonu(): void {
  if (glos.tryb) {
    dotknijMikrofonu()
    return
  }
  if (!rozpoznawanieDostepne.value) {
    pokazPodpowiedzGlosu()
    return
  }
  otworzRozmowe()
  uruchomGlos()
}

function zdjecie(): void {
  otworzRozmowe()
  void wyslijZdjecie()
}

function wybierzOpcje(opcja: string): void {
  const ostatnia = aktywna.value?.wiadomosci[aktywna.value.wiadomosci.length - 1]
  if (ostatnia?.wielokrotny) przelaczWielokrotny(opcja)
  else void wyslij(opcja)
}

function nacisnietoKlawisz(e: KeyboardEvent): void {
  if (e.key !== 'Escape') return
  if (widok.menu) widok.menu = false
  else if (widok.todo) widok.todo = false
  else if (widok.historia) widok.historia = false
  else if (widok.dokument) widok.dokument = null
}

onMounted(() => {
  void wczytajJezyk()
  void pobierzStanUslug()
  przygotujPowitanie()
  zegarTokenu = window.setInterval(() => {
    token.value = Math.floor(Math.random() * 65536)
  }, 30000)
  document.addEventListener('keydown', nacisnietoKlawisz)
})

onBeforeUnmount(() => {
  if (zegarTokenu !== null) clearInterval(zegarTokenu)
  if (zegarPodpowiedzi !== null) clearTimeout(zegarPodpowiedzi)
  document.removeEventListener('keydown', nacisnietoKlawisz)
  zatrzymajNasluch()
})
</script>

<template>
  <div class="ekran-aplikacji">
    <div class="ramka-telefonu" :data-osoba="idOsoby" :data-uklad="uklad">
      <div class="relative flex min-h-0 flex-1 flex-col pt-[env(safe-area-inset-top)]">
        <div class="hidden h-[42px] shrink-0 items-center justify-between px-8 pt-3 text-[16px] font-semibold md:flex">
          <span>{{ godzina }}</span>
          <span class="h-3 w-6 rounded-[4px] border-[1.4px] border-current">
            <i class="block h-full w-3/4 bg-current" />
          </span>
        </div>

        <header class="flex h-[52px] shrink-0 items-center gap-1 px-4">
          <button type="button" class="-ml-1 rounded-lg p-1" :aria-label="t('Ekran główny')" @click="przejdzDoDokumentow()">
            <img src="/assets/icon-mobywatel.svg" alt="" class="h-[30px] w-[30px] rounded-lg" />
          </button>
          <span class="flex-1" />
          <template v-if="widok.rozmowa">
            <button type="button" class="relative grid h-10 w-10 place-items-center" :aria-label="t('Historia rozmów')" @click="widok.historia = true">
              <span class="h-6 w-6" v-html="iconSvg('history', 1.6)" />
            </button>
            <button type="button" class="grid h-10 w-10 place-items-center" :aria-label="t('Nowa rozmowa')" @click="nowaRozmowa()">
              <span class="h-6 w-6" v-html="iconSvg('plus', 1.6)" />
            </button>
          </template>
          <button
            type="button"
            class="grid h-10 w-10 place-items-center"
            :aria-label="t('Potwierdź swoje dane: zeskanuj znak mObywatela odbiorcy')"
            @click="void otworzSkaner({})"
          >
            <span class="h-6 w-6" v-html="iconSvg('scan', 1.6)" />
          </button>
          <button
            type="button"
            class="grid h-10 w-10 place-items-center"
            :aria-label="t('Skrzynka')"
            @click="wyslijTekst(t('Sprawdź moją skrzynkę'))"
          >
            <span class="h-6 w-6" v-html="iconSvg('mail', 1.6)" />
          </button>
          <button type="button" class="grid h-10 w-10 place-items-center" :aria-label="t('Powiadomienia')" @click="widok.todo = true">
            <span class="h-6 w-6" v-html="iconSvg('bell', 1.6)" />
          </button>
        </header>

        <button
          v-if="!widok.rozmowa"
          type="button"
          class="shrink-0 px-5 pb-1 text-left text-[32px] font-bold leading-10 tracking-[-0.02em]"
          aria-haspopup="true"
          :aria-expanded="widok.menu"
          @click="widok.menu = true"
        >
          {{ t('Dokumenty') }}
          <span class="inline-block h-4 w-4 align-middle text-ink-3" v-html="iconSvg('chev', 2.4)" />
        </button>

        <div
          v-if="uslugi && (!uslugi.agent || uslugi.bielik === false)"
          class="mx-4 mb-2 shrink-0 rounded-xl bg-warn-wash px-3 py-2 text-[12.5px] leading-4 text-warn"
        >
          {{ uslugi.komunikat }}
        </div>

        <main class="relative flex min-h-0 flex-1 flex-col">
          <ChatPanel
            v-if="widok.rozmowa"
            class="absolute inset-0 z-20 bg-bg pt-2"
            @wroc="przejdzDoDokumentow()"
            @potwierdz="(id: string) => void potwierdz(id, true)"
            @anuluj="(id: string) => void potwierdz(id, false)"
            @opcja="wybierzOpcje"
            @przelacz="przelaczWielokrotny"
            @dalej="zatwierdzWielokrotny()"
          />
          <Wallet v-else :token="token" @pokaz-dokument="(id: string) => (widok.dokument = id)" @pokaz-sprawy="widok.todo = true" />
          <VoiceOverlay v-if="glos.tryb" @pisac="zakonczGlos(); otworzRozmowe()" />
        </main>

        <p
          v-if="podpowiedzGlosu"
          class="mx-4 mb-1 shrink-0 rounded-xl bg-warn-wash px-3 py-2 text-[12.5px] leading-4 text-warn"
        >
          {{ t('Ta przeglądarka nie obsługuje rozpoznawania mowy. Napisz wiadomość tekstem.') }}
        </p>

        <Composer @wyslij="wyslijTekst" @mikrofon="klikMikrofonu" @zdjecie="zdjecie" />

        <div class="hidden h-2 shrink-0 justify-center md:flex">
          <span class="h-[5px] w-[134px] rounded-full bg-ink" />
        </div>

        <TodoSheet v-if="widok.todo" />
        <HistorySheet v-if="widok.historia" />
        <MenuSheet v-if="widok.menu" />
        <DocumentSheet v-if="widok.dokument" :token="token" />
        <FaceIdOverlay v-if="widok.faceid" />
        <SignOverlay />
      </div>
    </div>
  </div>
</template>
