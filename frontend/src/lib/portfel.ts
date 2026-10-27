import { computed, ref } from 'vue'
import { OSOBY } from './people.data'
import type { Osoba, Uklad, WariantUkladu } from './types'

const KLUCZ_OSOBY = 'mobOsoba'
const KLUCZ_UKLADU = 'mobUklad'
const DOMYSLNA_OSOBA = 'marta'

export const UKLADY: Uklad[] = [
  { id: 'stos', nazwa: 'Stos', opis: 'Jak dziś w mObywatelu i Apple Wallet' },
  { id: 'karuzela', nazwa: 'Karuzela', opis: 'Duża karta przewijana w bok, akcje pod spodem' },
  { id: 'pion', nazwa: 'Pionowa karuzela', opis: 'Karta na środku, przewijanie w górę i w dół' },
  { id: 'lista', nazwa: 'Lista ze statusem', opis: 'Zdjęcie, dane i alerty w jednym wierszu' },
  { id: 'siatka', nazwa: 'Siatka 2×2', opis: 'Wszystkie dokumenty naraz' }
]

function zPamieci(klucz: string): string | null {
  try {
    return localStorage.getItem(klucz)
  } catch {
    return null
  }
}

function doPamieci(klucz: string, wartosc: string): void {
  try {
    localStorage.setItem(klucz, wartosc)
  } catch {
    /* tryb prywatny może blokować zapis */
  }
}

function wybierzOsobe(): string {
  const zAdresu = new URLSearchParams(location.search).get('osoba')
  if (zAdresu && OSOBY[zAdresu]) {
    doPamieci(KLUCZ_OSOBY, zAdresu)
    return zAdresu
  }
  const zapamietana = zPamieci(KLUCZ_OSOBY)
  return zapamietana && OSOBY[zapamietana] ? zapamietana : DOMYSLNA_OSOBA
}

function wybierzUklad(): WariantUkladu {
  const zAdresu = new URLSearchParams(location.search).get('uklad')
  const zapamietany = zPamieci(KLUCZ_UKLADU)
  const kandydat = [zAdresu, zapamietany].find((x) => UKLADY.some((u) => u.id === x))
  return (kandydat as WariantUkladu) || 'stos'
}

export const idOsoby = ref(wybierzOsobe())
export const uklad = ref<WariantUkladu>(wybierzUklad())

export const osoby = OSOBY
export const osoba = computed<Osoba>(() => OSOBY[idOsoby.value] ?? OSOBY[DOMYSLNA_OSOBA])
export const dokumenty = computed(() => osoba.value.docs)
export const sprawy = computed(() => osoba.value.tiles)
export const mojeDane = computed<Record<string, string>>(() => osoba.value.moje)

export function zmienOsobe(id: string): void {
  if (!OSOBY[id] || id === idOsoby.value) return
  doPamieci(KLUCZ_OSOBY, id)
  const adres = new URL(location.href)
  adres.searchParams.set('osoba', id)
  location.replace(adres.toString())
}

export function ustawUklad(nowy: WariantUkladu): void {
  uklad.value = nowy
  doPamieci(KLUCZ_UKLADU, nowy)
  const adres = new URL(location.href)
  adres.searchParams.set('uklad', nowy)
  history.replaceState(null, '', adres.toString())
}

export function rodzaj(zenski: string, meski: string): string {
  return osoba.value.plec === 'K' ? zenski : meski
}

export function zdjecieOsoby(id: string): string {
  return `assets/foto-${id}.jpg`
}
