<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { api } from '@/lib/api'
import { iconSvg } from '@/lib/icons'
import { t, wczytajJezyk } from '@/lib/i18n'
import { svgZnaku } from '@/lib/znak'
import { svg as sylwetkaSvg } from '@/lib/sylwetki'

const DEV = 'web' + Math.random().toString(36).slice(2, 10)
const KTO = 'Autoplus Wypożyczalnia Samochodów'
const ZAKRES: [string, string][] = [
  ['Zdjęcie', 'foto'],
  ['Imię i nazwisko', 'imie_nazwisko'],
  ['Data urodzenia', 'data_urodzenia'],
  ['PESEL', 'pesel'],
  ['Numer dowodu', 'nr_dowodu'],
  ['Prawo jazdy', 'prawo_jazdy']
]

const token = ref(Math.floor(Math.random() * 65536))
const stan = ref<'czekam' | 'telefon' | 'odrzucono' | 'gotowe' | 'blad'>('czekam')
const dane = ref<{ imie: string; foto: string; rows: [string, string][]; godzina: string } | null>(null)
const oplacono = ref(false)
const blokada = ref(false)
let beatTimer: number | null = null
let tokenTimer: number | null = null

const auto = computed(() => sylwetkaSvg('Toyota Yaris', 'biały'))

const komunikat = computed(() => {
  if (stan.value === 'telefon') return t('Znak zeskanowany. Potwierdź przekazanie danych na telefonie.')
  if (stan.value === 'odrzucono') return t('Przekazanie danych zostało odrzucone na telefonie. Możesz spróbować ponownie.')
  if (stan.value === 'blad') return t('Brak połączenia z serwerem. Sprawdzam dalej.')
  return t('Czekam na zeskanowanie znaku telefonem…')
})

function nowyToken(): void {
  token.value = Math.floor(Math.random() * 65536)
}

async function beat(): Promise<void> {
  if (stan.value === 'gotowe' || document.visibilityState !== 'visible') return
  try {
    const j = await api.znakBeat({ dev: DEV, token: token.value, kind: 'web', kto: KTO, cel: 'tozsamosc', zakres: ZAKRES })
    if (j.zmien) nowyToken()
    for (const d of j.otrzymane ?? []) {
      if (d.ok && d.dane) {
        pokaz(d.dane)
        return
      }
      stan.value = 'odrzucono'
      window.setTimeout(() => {
        if (stan.value === 'odrzucono') stan.value = 'czekam'
      }, 6000)
      return
    }
    stan.value = j.skanuje ? 'telefon' : 'czekam'
  } catch {
    stan.value = 'blad'
  }
}

function pokaz(otrzymane: Record<string, unknown>): void {
  const rows = ((otrzymane.rows as [string, string][] | undefined) ?? []).filter((r) => r[1] !== 'foto')
  dane.value = {
    imie: (otrzymane.od as string | undefined) ?? t('Osoba pełnoletnia'),
    foto: /^[a-z]+$/.test(String(otrzymane.foto ?? '')) ? String(otrzymane.foto) : 'marta',
    rows,
    godzina: new Date().toLocaleTimeString('pl-PL', { hour: '2-digit', minute: '2-digit' })
  }
  stan.value = 'gotowe'
  if (beatTimer !== null) clearInterval(beatTimer)
  if (tokenTimer !== null) clearInterval(tokenTimer)
}

function zaplac(): void {
  if (oplacono.value || blokada.value) return
  blokada.value = true
  window.setTimeout(() => {
    oplacono.value = true
    blokada.value = false
  }, 600)
}

function zacznijOdNowa(): void {
  dane.value = null
  oplacono.value = false
  stan.value = 'czekam'
  nowyToken()
  beatTimer = window.setInterval(() => void beat(), 1200)
  tokenTimer = window.setInterval(() => stan.value !== 'gotowe' && nowyToken(), 30000)
  void beat()
}

onMounted(() => {
  void wczytajJezyk()
  beatTimer = window.setInterval(() => void beat(), 1200)
  tokenTimer = window.setInterval(() => stan.value !== 'gotowe' && nowyToken(), 30000)
  void beat()
})

onBeforeUnmount(() => {
  if (beatTimer !== null) clearInterval(beatTimer)
  if (tokenTimer !== null) clearInterval(tokenTimer)
})
</script>

<template>
  <div class="min-h-screen bg-bg text-ink">
    <nav class="border-b border-line bg-white">
      <div class="mx-auto flex max-w-[1180px] items-center gap-6 px-4 py-3 sm:px-7">
        <span class="text-[22px] font-extrabold tracking-[-0.02em]">auto<span class="text-blue-700">plus</span></span>
        <div class="ml-auto flex gap-2 text-[13px] text-ink-2 sm:gap-5 sm:text-[14px]">
          <span class="flex items-center gap-1.5"><i class="grid h-[22px] w-[22px] place-items-center rounded-full bg-emerald-600 text-[12px] font-bold text-white not-italic">✓</i><em class="hidden not-italic sm:inline">{{ t('Wybór auta') }}</em></span>
          <span class="flex items-center gap-1.5 font-semibold text-ink"><i class="grid h-[22px] w-[22px] place-items-center rounded-full bg-blue-700 text-[12px] font-bold text-white not-italic">2</i>{{ t('Kierowca') }}</span>
          <span class="flex items-center gap-1.5"><i class="grid h-[22px] w-[22px] place-items-center rounded-full bg-slate-200 text-[12px] font-bold not-italic">3</i><em class="hidden not-italic sm:inline">{{ t('Płatność') }}</em></span>
        </div>
      </div>
    </nav>

    <div class="mx-auto grid max-w-[1180px] gap-3 px-3 py-4 sm:grid-cols-[1fr_1.1fr] sm:gap-7 sm:px-7 sm:py-9">
      <section class="rounded-[18px] bg-white p-4 shadow-sm sm:rounded-[20px] sm:p-7">
        <h1 class="text-[20px] font-bold tracking-[-0.02em] sm:text-[28px]">{{ t('Twoja rezerwacja') }}</h1>
        <p class="mt-1 text-[14px] leading-5 text-ink-2 sm:text-[15px]">{{ t('Odbiór') }}: Warszawa, Lotnisko Chopina · 24.10, 10:00 → 27.10, 10:00</p>
        <div class="my-4 flex items-center gap-4 rounded-2xl border border-line p-3">
          <span class="h-14 w-24 flex-none rounded-xl bg-gradient-to-b from-slate-100 to-slate-200 p-1" v-html="auto" />
          <div>
            <b class="block text-[16px]">Toyota Yaris Hybrid {{ t('lub podobny') }}</b>
            <small class="text-[13px] text-ink-2">{{ t('automat · 5 miejsc · klimatyzacja') }}</small>
          </div>
        </div>
        <div class="flex justify-between border-t border-line py-2.5 text-[14.5px]"><span class="text-ink-2">{{ t('Wynajem (3 doby)') }}</span><b>486,00 zł</b></div>
        <div class="flex justify-between border-t border-line py-2.5 text-[14.5px]"><span class="text-ink-2">{{ t('Ubezpieczenie pełne') }}</span><b>117,00 zł</b></div>
        <div class="flex justify-between border-t border-line py-2.5 text-[14.5px]"><span class="text-ink-2">{{ t('Do zapłaty') }}</span><b class="text-[18px]">603,00 zł</b></div>
      </section>

      <section v-if="!dane" class="rounded-[18px] bg-white p-4 shadow-sm sm:rounded-[20px] sm:p-7">
        <h2 class="text-[19px] font-bold tracking-[-0.02em] sm:text-[24px]">{{ t('Potwierdź tożsamość kierowcy') }}</h2>
        <p class="mt-1 text-[14px] leading-5 text-ink-2 sm:text-[15px]">
          {{ t('Bez przepisywania danych i skanów dokumentów. Wystarczy telefon z aplikacją mObywatel.') }}
        </p>
        <div class="my-4 flex flex-col items-center gap-4 sm:flex-row sm:gap-7">
          <div class="aspect-square w-[70vw] max-w-[260px] sm:w-[230px]" v-html="svgZnaku(token)" />
          <ol class="flex-1 list-decimal rounded-2xl bg-slate-50 px-4 py-3 pl-8 text-[15px] leading-6">
            <li>{{ t('Otwórz aplikację') }} <b>mObywatel</b>.</li>
            <li v-html="t('Dotknij ikony <b>Potwierdź swoje dane</b>.')" />
            <li>{{ t('Nakieruj aparat na znak') }} <span class="hidden sm:inline">{{ t('obok') }}</span><span class="sm:hidden">{{ t('powyżej') }}</span>.</li>
            <li>{{ t('Potwierdź na telefonie.') }}</li>
          </ol>
        </div>
        <div
          class="mt-4 flex items-center gap-2.5 rounded-xl px-3.5 py-3 text-[14px]"
          :class="stan === 'telefon' ? 'bg-amber-50 text-amber-800' : stan === 'odrzucono' ? 'bg-brand-wash text-brand' : 'bg-slate-100 text-ink-2'"
        >
          <i class="h-2.5 w-2.5 flex-none rounded-full bg-current" :class="stan === 'telefon' ? 'anim-tchnienie' : ''" />
          <span class="flex-1">{{ komunikat }}</span>
        </div>
      </section>

      <section v-else class="rounded-[18px] bg-white p-4 shadow-sm sm:rounded-[20px] sm:p-7">
        <div class="mb-4 flex flex-wrap items-center gap-2 rounded-xl bg-ok-wash px-3.5 py-3 font-semibold text-ok">
          <span class="h-4 w-4" v-html="iconSvg('check')" />
          {{ t('Tożsamość potwierdzona przez mObywatel') }}
          <small class="w-full text-[13px] font-normal opacity-85 sm:ml-auto sm:w-auto">godz. {{ dane.godzina }}</small>
        </div>
        <div class="flex items-start gap-4">
          <span class="h-24 w-[76px] flex-none rounded-xl bg-slate-200 bg-cover bg-[50%_30%] shadow-sm" :style="{ backgroundImage: `url(assets/foto-${dane.foto}.jpg)` }" />
          <div class="flex-1">
            <div v-for="r in dane.rows" :key="r[0]" class="border-t border-line py-2 first:border-t-0 sm:flex sm:justify-between">
              <span class="text-[12.5px] text-ink-2 sm:text-[14px]">{{ r[0] }}</span>
              <b class="block text-[15px] font-medium sm:text-right">{{ r[1] }}</b>
            </div>
          </div>
        </div>
        <div
          v-if="oplacono"
          class="mt-4 flex items-center gap-2 rounded-xl bg-emerald-50 px-4 py-3 text-[14px] font-semibold text-emerald-800"
        >
          <span class="h-4 w-4" v-html="iconSvg('check')" />
          {{ t('Płatność przyjęta. Rezerwacja potwierdzona, kluczyki czekają w wypożyczalni.') }}
        </div>
        <button
          v-else
          type="button"
          class="mt-4 w-full rounded-xl bg-blue-700 px-5 py-3.5 font-semibold text-white transition-opacity disabled:opacity-60 sm:w-auto"
          :disabled="blokada"
          @click="zaplac()"
        >
          {{ blokada ? t('Przetwarzam płatność…') : t('Przejdź do płatności') }}
        </button>
        <button type="button" class="mt-3 block w-full text-[14px] text-ink-2 underline sm:w-auto" @click="zacznijOdNowa()">
          {{ t('Zacznij od nowa') }}
        </button>
      </section>
    </div>
  </div>
</template>
