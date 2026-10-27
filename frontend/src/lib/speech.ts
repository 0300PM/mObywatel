import { ref } from 'vue'

interface ZdarzenieRozpoznawania {
  results: { length: number; [i: number]: { 0: { transcript: string } } }
}

interface Rozpoznawacz {
  lang: string
  interimResults: boolean
  continuous: boolean
  maxAlternatives: number
  start: () => void
  stop: () => void
  abort: () => void
  onresult: ((e: ZdarzenieRozpoznawania) => void) | null
  onerror: ((e: { error: string }) => void) | null
  onend: (() => void) | null
}

type KonstruktorRozpoznawania = new () => Rozpoznawacz

const okno = window as unknown as {
  SpeechRecognition?: KonstruktorRozpoznawania
  webkitSpeechRecognition?: KonstruktorRozpoznawania
  webkitAudioContext?: typeof AudioContext
}

const Konstruktor = okno.SpeechRecognition ?? okno.webkitSpeechRecognition

export const rozpoznawanieDostepne = ref(Boolean(Konstruktor))
export const syntezaDostepna = ref(typeof window !== 'undefined' && 'speechSynthesis' in window)
export const mowi = ref(false)
export const slucham = ref(false)

let rozpoznawacz: Rozpoznawacz | null = null

export interface WynikNasluchu {
  tekst: string
  blad?: 'brak-mikrofonu' | 'brak-mowy' | 'przerwano'
}

export function nasluchuj(lang: string, czasMs = 12000): Promise<WynikNasluchu> {
  if (!Konstruktor) return Promise.resolve({ tekst: '', blad: 'brak-mikrofonu' })
  zatrzymajNasluch()
  const r = new Konstruktor()
  rozpoznawacz = r
  r.lang = lang === 'pl' ? 'pl-PL' : lang
  r.interimResults = false
  r.continuous = false
  r.maxAlternatives = 1

  return new Promise((resolve) => {
    let zakonczone = false
    let tekst = ''
    const timer = setTimeout(() => r.stop(), czasMs)
    const koniec = (wynik: WynikNasluchu): void => {
      if (zakonczone) return
      zakonczone = true
      clearTimeout(timer)
      slucham.value = false
      rozpoznawacz = null
      resolve(wynik)
    }
    r.onresult = (e) => {
      tekst = (e.results[0]?.[0]?.transcript ?? '').trim()
    }
    r.onerror = (e) => koniec({ tekst: '', blad: e.error === 'not-allowed' || e.error === 'service-not-allowed' ? 'brak-mikrofonu' : 'brak-mowy' })
    r.onend = () => koniec(tekst ? { tekst } : { tekst: '', blad: 'brak-mowy' })
    try {
      r.start()
      slucham.value = true
    } catch {
      koniec({ tekst: '', blad: 'brak-mikrofonu' })
    }
  })
}

export function zatrzymajNasluch(): void {
  if (!rozpoznawacz) return
  try {
    rozpoznawacz.abort()
  } catch {
    /* przeglądarka mogła już zakończyć sesję */
  }
  rozpoznawacz = null
  slucham.value = false
}

let glosDlaJezyka: SpeechSynthesisVoice | null = null

function wybierzGlos(lang: string): SpeechSynthesisVoice | null {
  if (!syntezaDostepna.value) return null
  const kod = (lang === 'pl' ? 'pl-PL' : lang).toLowerCase()
  const glosy = speechSynthesis.getVoices()
  if (glosDlaJezyka && glosDlaJezyka.lang.toLowerCase().startsWith(lang)) return glosDlaJezyka
  glosDlaJezyka = glosy.find((v) => v.lang.toLowerCase() === kod) ?? glosy.find((v) => v.lang.toLowerCase().startsWith(lang)) ?? null
  return glosDlaJezyka
}

if (syntezaDostepna.value) {
  speechSynthesis.addEventListener('voiceschanged', () => {
    glosDlaJezyka = null
    wybierzGlos(document.documentElement.lang || 'pl')
  })
}

export function czytaj(tekst: string, lang: string): Promise<void> {
  const tresc = tekst.trim()
  if (!tresc || !syntezaDostepna.value) return Promise.resolve()
  return new Promise((resolve) => {
    const wypowiedz = new SpeechSynthesisUtterance(tresc)
    wypowiedz.lang = lang === 'pl' ? 'pl-PL' : lang
    const glos = wybierzGlos(lang)
    if (glos) wypowiedz.voice = glos
    wypowiedz.rate = 1
    const koniec = (): void => {
      mowi.value = false
      resolve()
    }
    wypowiedz.onend = koniec
    wypowiedz.onerror = koniec
    mowi.value = true
    speechSynthesis.speak(wypowiedz)
  })
}

export function przerwijCzytanie(): void {
  if (!syntezaDostepna.value) return
  speechSynthesis.cancel()
  mowi.value = false
}

export function inicjujAudio(): void {
  const C = window.AudioContext ?? okno.webkitAudioContext
  if (!C) return
  const ctx = new C()
  if (ctx.state !== 'running') void ctx.resume().catch(() => {})
}
