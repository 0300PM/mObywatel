import { ref } from 'vue'
import { api } from './api'

const LANGS = ['pl', 'en', 'de', 'fr', 'es', 'it', 'pt', 'nl', 'cs', 'sk', 'sl', 'hu', 'ro', 'el', 'sv', 'uk'] as const

export type Jezyk = (typeof LANGS)[number]

const NUM = /\d+(?:[.,:/]\d+)*/g

function wykryjJezyk(): Jezyk {
  const zAdresu = (location.pathname.match(/^\/([a-z]{2})\//) || [])[1]
  const zParametru = new URLSearchParams(location.search).get('lang')
  const kandydat = [zAdresu, zParametru].find((x) => x && (LANGS as readonly string[]).includes(x))
  return (kandydat as Jezyk) || 'pl'
}

export const jezyk = ref<Jezyk>(wykryjJezyk())
const slownik = ref<Record<string, string>>({})
const zgloszone = new Set<string>()

function szablon(tekst: string): { klucz: string; liczby: string[] } {
  const liczby: string[] = []
  const klucz = tekst.replace(NUM, (m) => {
    liczby.push(m)
    return `{${liczby.length - 1}}`
  })
  return { klucz, liczby }
}

export function t(tekst: string): string {
  if (jezyk.value === 'pl' || !tekst) return tekst
  const { klucz, liczby } = szablon(tekst)
  const przetlumaczone = slownik.value[klucz]
  if (!przetlumaczone) {
    if (!zgloszone.has(klucz)) {
      zgloszone.add(klucz)
      void api.brakujaceTlumaczenia(jezyk.value, [klucz]).catch(() => {})
    }
    return tekst
  }
  return przetlumaczone.replace(/\{(\d+)\}/g, (m, i) => liczby[Number(i)] ?? m)
}

const LITERY = /\p{L}{2,}/u

export function para(etykieta: string, wartosc: string): { etykieta: string; wartosc: string } {
  return { etykieta: t(etykieta), wartosc: LITERY.test(wartosc) ? t(wartosc) : wartosc }
}

export function przetlumaczWartosc(tekst: string): string {
  return LITERY.test(tekst) ? t(tekst) : tekst
}

export async function wczytajJezyk(): Promise<void> {
  document.documentElement.lang = jezyk.value
  if (jezyk.value === 'pl') return
  try {
    slownik.value = (await api.i18n(jezyk.value)).t ?? {}
  } catch {
    slownik.value = {}
  }
}

export const glosDostepny = ref(true)
