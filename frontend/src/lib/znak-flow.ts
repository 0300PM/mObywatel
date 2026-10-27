import { shallowRef } from 'vue'
import { mojeDane, osoba } from './portfel'

export interface WynikZnaku {
  ok: boolean
  wynik?: Record<string, unknown>
}

export interface ZadanieZnaku {
  mode: 'scan' | 'show'
  cel: string
  dokument: string
  resolve: (wynik: WynikZnaku) => void
}

export interface Zakres {
  nazwa: string
  pola: [string, string][]
}

export const ZAKRESY: Record<string, Zakres> = {
  tozsamosc: {
    nazwa: 'Tożsamość',
    pola: [['Zdjęcie', 'foto'], ['Imię i nazwisko', 'imie_nazwisko'], ['Data urodzenia', 'data_urodzenia'], ['PESEL', 'pesel'], ['Dowód osobisty', 'dowod']]
  },
  pelnoletnosc: {
    nazwa: 'Pełnoletność',
    pola: [['Zdjęcie', 'foto'], ['Pełnoletność', 'pelnoletnosc']]
  },
  prawo_jazdy: {
    nazwa: 'Prawo jazdy',
    pola: [['Zdjęcie', 'foto'], ['Imię i nazwisko', 'imie_nazwisko'], ['Prawo jazdy', 'prawo_jazdy']]
  },
  mstluczka: {
    nazwa: 'Dane do oświadczenia',
    pola: [['Kierowca', 'imie_nazwisko'], ['Pojazd', 'pojazd'], ['OC', 'oc'], ['Prawo jazdy', 'prawo_jazdy']]
  }
}

export const identyfikatorUrzadzenia = (() => {
  try {
    let d = sessionStorage.getItem('mobDev')
    if (!d) {
      d = Math.random().toString(36).slice(2, 10)
      sessionStorage.setItem('mobDev', d)
    }
    return d
  } catch {
    return Math.random().toString(36).slice(2, 10)
  }
})()

export const zadanieZnaku = shallowRef<ZadanieZnaku | null>(null)

function uruchom(opt: { mode: 'scan' | 'show'; cel?: string; dokument?: string }): Promise<WynikZnaku> {
  zakonczZadanie({ ok: false })
  return new Promise((resolve) => {
    zadanieZnaku.value = { mode: opt.mode, cel: opt.cel && ZAKRESY[opt.cel] ? opt.cel : 'tozsamosc', dokument: opt.dokument ?? 'dowod', resolve }
  })
}

export function otworzSkaner(opt: { cel?: string; dokument?: string } = {}): Promise<WynikZnaku> {
  return uruchom({ ...opt, mode: 'scan' })
}

export function otworzPrzyjmowanie(opt: { cel?: string } = {}): Promise<WynikZnaku> {
  return uruchom({ ...opt, mode: 'show' })
}

export function zakonczZadanie(wynik: WynikZnaku): void {
  const zadanie = zadanieZnaku.value
  zadanieZnaku.value = null
  zadanie?.resolve(wynik)
}

export function wypelnijZakres(pola: [string, string][]): [string, string][] {
  const dane: Record<string, string> = { ...mojeDane.value, foto: 'foto' }
  return pola.map(([etykieta, klucz]) => [etykieta, dane[klucz] ?? klucz])
}

export function mojaNazwa(): string {
  return `${osoba.value.imie} ${osoba.value.nazwisko}`
}
