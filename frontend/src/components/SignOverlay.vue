<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, ref, watch } from 'vue'
import { api } from '@/lib/api'
import { iconSvg } from '@/lib/icons'
import { t } from '@/lib/i18n'
import { odkodujZnak, svgZnaku } from '@/lib/znak'
import { ZAKRESY, identyfikatorUrzadzenia, mojaNazwa, wypelnijZakres, zakonczZadanie, zadanieZnaku, type WynikZnaku } from '@/lib/znak-flow'
import { daneWidoczne } from '@/lib/ui'

type Ekran = 'skan' | 'zgoda' | 'wyslano' | 'znak' | 'odebrano'

const ekran = ref<Ekran>('skan')
const video = ref<HTMLVideoElement | null>(null)
const komunikat = ref('')
const postep = ref('')
const znakWidoczny = ref(false)

const cel = ref('tozsamosc')
const osobaOdbiorcy = ref<{ dev: string; kind: string; kto: string; zakres: [string, string][] } | null>(null)
const mojToken = ref(0)
const otrzymane = ref<[string, string][]>([])
const otrzymaneImie = ref('')
const pozostalo = ref(180)
const zakresWybrany = ref('tozsamosc')

let strumien: MediaStream | null = null
let petla: number | null = null
let beatTimer: number | null = null
let tokenTimer: number | null = null
let licznikTimer: number | null = null
let zatrzymane = false

const ZAKRESY_WYBORU = ['tozsamosc', 'pelnoletnosc', 'prawo_jazdy']

const tytul = computed(() => (ekran.value === 'skan' ? t('Potwierdź swoje dane') : ekran.value === 'znak' ? t('Przyjmij dane') : t('Przekazanie danych')))

function nowyToken(): void {
  mojToken.value = Math.floor(Math.random() * 65536)
}

function zatrzymajKamere(): void {
  if (petla !== null) {
    clearTimeout(petla)
    petla = null
  }
  if (strumien) {
    strumien.getTracks().forEach((t) => t.stop())
    strumien = null
  }
  if (video.value) video.value.srcObject = null
}

function zatrzymajTimery(): void {
  if (beatTimer !== null) clearInterval(beatTimer)
  if (tokenTimer !== null) clearInterval(tokenTimer)
  if (licznikTimer !== null) clearInterval(licznikTimer)
  beatTimer = tokenTimer = licznikTimer = null
}

function zamknij(wynik: WynikZnaku = { ok: false }): void {
  if (zatrzymane) return
  zatrzymane = true
  zatrzymajKamere()
  zatrzymajTimery()
  zakonczZadanie(wynik)
}

async function startKamery(): Promise<void> {
  ekran.value = 'skan'
  komunikat.value = t('Uruchamiam aparat…')
  postep.value = ''
  try {
    strumien = await navigator.mediaDevices.getUserMedia({
      video: { facingMode: { ideal: 'environment' }, width: { ideal: 1280 }, height: { ideal: 720 } },
      audio: false
    })
  } catch {
    komunikat.value = t('Brak dostępu do aparatu. Zezwól na aparat w ustawieniach przeglądarki.')
    return
  }
  if (zatrzymane) {
    zatrzymajKamere()
    return
  }
  await nextTick()
  const v = video.value
  if (!v) return
  v.srcObject = strumien
  try {
    await v.play()
  } catch {
    /* autoplay może wymagać gestu, obraz pojawi się po dotknięciu */
  }
  komunikat.value = t('Szukam znaku…')
  skanuj()
}

let plansza: HTMLCanvasElement | null = null
let kontekst: CanvasRenderingContext2D | null = null

function skanuj(): void {
  const v = video.value
  if (!plansza) {
    plansza = document.createElement('canvas')
    kontekst = plansza.getContext('2d', { willReadFrequently: true })
  }
  const szukaj = (): void => {
    if (zatrzymane || ekran.value !== 'skan' || !v || !kontekst || !plansza) return
    if (v.readyState >= 2 && v.videoWidth) {
      const w = 480
      const h = Math.round((w * v.videoHeight) / v.videoWidth) || 360
      plansza.width = w
      plansza.height = h
      kontekst.drawImage(v, 0, 0, w, h)
      const odczyt = odkodujZnak(kontekst.getImageData(0, 0, w, h).data, w, h)
      if (odczyt) {
        znakWidoczny.value = true
        if (odczyt.token === mojToken.value) {
          komunikat.value = t('To Twój własny znak. Zeskanuj znak odbiorcy.')
        } else {
          void rozpoznaj(odczyt.token)
          return
        }
      }
    }
    petla = window.setTimeout(szukaj, 110)
  }
  szukaj()
}

async function rozpoznaj(token: number): Promise<void> {
  zatrzymajKamere()
  komunikat.value = t('Rozpoznano znak, sprawdzam…')
  try {
    const wynik = await api.znakKto(token, identyfikatorUrzadzenia)
    if (!wynik.dev) {
      komunikat.value = t('Ten znak jest nieaktualny. Poproś o odświeżenie ekranu.')
      void startKamery()
      return
    }
    const zakres = (wynik.zakres as [string, string][] | undefined) ?? ZAKRESY.tozsamosc.pola
    osobaOdbiorcy.value = {
      dev: wynik.dev,
      kind: wynik.kind ?? 'telefon',
      kto: wynik.kto ?? t('Odbiorca danych'),
      zakres: wypelnijZakres(zakres)
    }
    cel.value = wynik.cel && ZAKRESY[wynik.cel] ? wynik.cel : 'tozsamosc'
    ekran.value = 'zgoda'
  } catch {
    komunikat.value = t('Brak połączenia. Spróbuj jeszcze raz.')
    void startKamery()
  }
}

async function udostepnij(): Promise<void> {
  const o = osobaOdbiorcy.value
  if (!o) return
  try {
    await api.znakPrzekaz({
      to: o.dev,
      from: identyfikatorUrzadzenia,
      ok: true,
      dane: {
        od: mojaNazwa(),
        foto: '',
        cel: cel.value,
        rows: o.zakres
      }
    })
  } catch {
    komunikat.value = t('Nie udało się przekazać danych. Spróbuj jeszcze raz.')
    return
  }
  ekran.value = 'wyslano'
}

async function odmow(): Promise<void> {
  const o = osobaOdbiorcy.value
  if (o) await api.znakPrzekaz({ to: o.dev, from: identyfikatorUrzadzenia, ok: false }).catch(() => {})
  zamknij({ ok: false })
}

function startZnaku(): void {
  ekran.value = 'znak'
  zatrzymajKamere()
  nowyToken()
  tokenTimer = window.setInterval(nowyToken, 30000)
  void beat()
  beatTimer = window.setInterval(() => void beat(), 1200)
}

async function beat(): Promise<void> {
  if (document.visibilityState !== 'visible') return
  const zakres = ZAKRESY[zakresWybrany.value]
  try {
    const j = await api.znakBeat({
      dev: identyfikatorUrzadzenia,
      token: mojToken.value,
      kind: 'telefon',
      kto: t('Telefon z mObywatelem'),
      cel: zakresWybrany.value,
      zakres: zakres.pola
    })
    if (j.zmien) nowyToken()
    for (const d of j.otrzymane ?? []) {
      if (d.ok && d.dane) {
        pokazOdebrane(d.dane)
        return
      }
      komunikat.value = t('Druga osoba odmówiła. Możesz poprosić jeszcze raz.')
    }
    postep.value = j.skanuje ? t('Druga osoba potwierdza przekazanie…') : t('Czekam na dane…')
  } catch {
    postep.value = t('Brak połączenia z serwerem.')
  }
}

function pokazOdebrane(dane: Record<string, unknown>): void {
  const rows = (dane.rows as [string, string][] | undefined) ?? []
  const imie = (dane.od as string | undefined) ?? rows.find((r) => r[0] === 'Imię i nazwisko')?.[1] ?? ''
  otrzymaneImie.value = imie
  otrzymane.value = rows.filter((r) => r[0] !== 'Zdjęcie')
  ekran.value = 'odebrano'
  zatrzymajTimery()
  pozostalo.value = 180
  licznikTimer = window.setInterval(() => {
    pozostalo.value = Math.max(0, pozostalo.value - 1)
    if (!pozostalo.value) zamknij({ ok: true, wynik: { imie_nazwisko: imie, status: 'przekazane z mObywatela' } })
  }, 1000)
}

function zakonczOdbior(): void {
  zamknij({ ok: true, wynik: { imie_nazwisko: otrzymaneImie.value, status: 'przekazane z mObywatela' } })
}

function minutniki(sek: number): string {
  return `${Math.floor(sek / 60)}:${String(sek % 60).padStart(2, '0')}`
}

watch(
  zadanieZnaku,
  (zadanie) => {
    if (!zadanie) return
    zatrzymane = false
    osobaOdbiorcy.value = null
    otrzymane.value = []
    postep.value = ''
    komunikat.value = ''
    znakWidoczny.value = false
    cel.value = zadanie.cel
    zakresWybrany.value = zadanie.cel
    daneWidoczne.value = false
    if (zadanie.mode === 'scan') void startKamery()
    else startZnaku()
  },
  { immediate: true }
)

onBeforeUnmount(() => {
  zatrzymajKamere()
  zatrzymajTimery()
})
</script>

<template>
  <div v-if="zadanieZnaku" class="absolute inset-0 z-50 flex flex-col" :class="ekran === 'skan' ? 'bg-[#0d0f14] text-white' : 'bg-bg text-ink'">
    <div class="flex h-[52px] shrink-0 items-center gap-2 px-4">
      <button type="button" class="grid h-9 w-9 place-items-center rounded-full bg-white/10" :aria-label="t('Zamknij')" @click="zamknij()">
        <span class="h-4 w-4" v-html="iconSvg('x', 2)" />
      </button>
      <b class="mx-auto text-[15px]">{{ tytul }}</b>
      <span class="w-9" />
    </div>

    <div v-if="ekran === 'skan'" class="relative flex min-h-0 flex-1 flex-col items-center justify-center">
      <video ref="video" playsinline muted autoplay class="absolute inset-0 h-full w-full object-cover opacity-90" />
      <div class="relative grid aspect-square w-[66%] place-items-center rounded-full" :class="znakWidoczny ? 'ring-4 ring-emerald-400' : 'ring-2 ring-dashed ring-white/70'">
        <span class="h-1/2 w-1/2 opacity-20" v-html="svgZnaku(0)" />
      </div>
      <p class="absolute bottom-[110px] mx-auto max-w-[86%] rounded-2xl bg-black/60 px-3.5 py-2 text-center text-[14px] font-semibold leading-[19px]">
        {{ komunikat }}
      </p>
      <div class="absolute inset-x-4 bottom-4">
        <p class="mb-2 text-[13.5px] leading-[19px] text-white/80">
          {{ t('Nakieruj aparat na znak mObywatela: na ekranie telefonu obok, na stronie internetowej albo w okienku urzędu. Przekażesz dane temu, czyj znak zeskanujesz.') }}
        </p>
        <button type="button" class="flex w-full items-center justify-center gap-2 rounded-2xl bg-white/15 px-4 py-3 text-[14px] font-semibold" @click="startZnaku()">
          <span class="h-4 w-4" v-html="iconSvg('inbox', 1.7)" />
          {{ t('Chcę przyjąć dane: pokaż mój znak') }}
        </button>
      </div>
    </div>

    <div v-else-if="ekran === 'zgoda' && osobaOdbiorcy" class="flex min-h-0 flex-1 flex-col px-4 pb-4">
      <div class="flex items-center gap-3 rounded-2xl bg-surface px-4 py-3">
        <span class="grid h-10 w-10 place-items-center rounded-full bg-brand-wash text-brand">
          <span class="h-5 w-5" v-html="iconSvg(osobaOdbiorcy.kind === 'web' ? 'pc' : 'ph')" />
        </span>
        <div class="min-w-0">
          <small class="block text-[12px] text-ink-3">{{ osobaOdbiorcy.kind === 'web' ? t('Strona internetowa prosi o dane') : t('Telefon obok prosi o dane') }}</small>
          <b class="block truncate text-[15px]">{{ osobaOdbiorcy.kto }}</b>
          <em class="flex items-center gap-1 text-[12px] not-italic text-ok">
            <span class="h-3.5 w-3.5" v-html="iconSvg('check')" />
            {{ t('Znak mObywatela aktualny') }} · {{ ZAKRESY[cel]?.nazwa }}
          </em>
        </div>
      </div>
      <h3 class="px-1 pb-1 pt-4 text-[15px] font-semibold">{{ t('Zobaczy te dane') }}</h3>
      <div class="min-h-0 flex-1 overflow-y-auto rounded-2xl bg-surface px-4">
        <div v-for="r in osobaOdbiorcy.zakres" :key="r[0]" class="flex justify-between gap-4 border-t border-line py-2.5 text-[14px] first:border-t-0">
          <span class="text-ink-2">{{ r[0] }}</span>
          <b class="text-right font-medium">{{ r[1] === 'foto' ? t('zdjęcie') : r[1] }}</b>
        </div>
      </div>
      <p class="px-1 py-3 text-[12.5px] leading-[17px] text-ink-2">
        {{ t('Dane zostaną przekazane jednorazowo. Odbiorca nie dostanie dostępu do niczego więcej.') }}
      </p>
      <div class="flex gap-2">
        <button type="button" class="h-12 flex-none rounded-[14px] bg-surface px-[18px] font-semibold" @click="odmow()">{{ t('Odmów') }}</button>
        <button type="button" class="h-12 flex-1 rounded-[14px] bg-brand font-semibold text-white" @click="udostepnij()">
          {{ t('Udostępnij dane') }}
        </button>
      </div>
    </div>

    <div v-else-if="ekran === 'wyslano'" class="flex flex-1 flex-col items-center justify-center gap-3 px-8 text-center">
      <span class="grid h-16 w-16 place-items-center rounded-full bg-ok-wash text-ok">
        <span class="h-9 w-9" v-html="iconSvg('check')" />
      </span>
      <h2 class="text-[20px] font-bold">{{ t('Dane przekazane') }}</h2>
      <p class="text-[14px] text-ink-2">{{ osobaOdbiorcy?.kto }}</p>
      <button type="button" class="mt-2 h-12 w-full rounded-[14px] bg-brand font-semibold text-white" @click="zakonczOdbior()">{{ t('Gotowe') }}</button>
    </div>

    <div v-else-if="ekran === 'znak'" class="flex flex-1 flex-col items-center px-6 pb-5">
      <div class="mx-auto aspect-square w-[76%] max-w-[280px]">
        <span class="block h-full w-full" v-html="svgZnaku(mojToken)" />
      </div>
      <p class="px-2 py-3 text-center text-[14px] leading-[19px] text-ink-2">
        {{ t('Poproś drugą osobę, by w swoim mObywatelu dotknęła Potwierdź swoje dane i zeskanowała ten znak.') }}
      </p>
      <div class="flex gap-1 rounded-2xl bg-brand-wash p-1">
        <button
          v-for="z in ZAKRESY_WYBORU"
          :key="z"
          type="button"
          class="rounded-xl px-3 py-2 text-[13px] font-semibold"
          :class="zakresWybrany === z ? 'bg-white text-ink shadow-sm' : 'text-ink-2'"
          @click="zakresWybrany = z"
        >
          {{ ZAKRESY[z].nazwa }}
        </button>
      </div>
      <p v-if="komunikat" class="pt-3 text-center text-[13px] text-brand">{{ komunikat }}</p>
      <p class="mt-auto pt-3 text-center text-[13.5px] text-ink-3">{{ postep }}</p>
    </div>

    <div v-else class="flex flex-1 flex-col px-4 pb-4">
      <div class="flex items-center gap-2 rounded-2xl bg-ok-wash px-4 py-3 text-ok">
        <span class="h-4 w-4" v-html="iconSvg('check')" />
        <b class="text-[14px]">{{ t('Dane z mObywatela') }}</b>
      </div>
      <div class="mt-2 flex items-center gap-3 rounded-2xl bg-surface px-4 py-3">
        <span class="h-12 w-9 rounded-lg bg-slate-200 bg-cover bg-[50%_30%]" :style="{ backgroundImage: 'url(assets/foto-marta.jpg)' }" />
        <div>
          <b class="block text-[15px]">{{ otrzymaneImie || t('Osoba pełnoletnia') }}</b>
          <small class="text-[12.5px] text-ink-2">{{ t('Dane z rejestrów państwowych') }}</small>
        </div>
      </div>
      <div class="mt-2 min-h-0 flex-1 overflow-y-auto rounded-2xl bg-surface px-4">
        <div v-for="r in otrzymane" :key="r[0]" class="flex justify-between gap-4 border-t border-line py-2.5 text-[14px] first:border-t-0">
          <span class="text-ink-2">{{ r[0] }}</span>
          <b class="text-right font-medium">{{ r[1] }}</b>
        </div>
      </div>
      <p class="py-2 text-center text-[12.5px] text-ink-3">
        {{ t('Dane znikną z ekranu za') }} <b>{{ minutniki(pozostalo) }}</b>
      </p>
      <button type="button" class="h-12 w-full rounded-[14px] bg-brand font-semibold text-white" @click="zakonczOdbior()">{{ t('Zakończ') }}</button>
    </div>
  </div>
</template>
