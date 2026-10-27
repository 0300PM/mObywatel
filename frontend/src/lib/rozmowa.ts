import { computed, nextTick, reactive, ref } from 'vue'
import { api } from './api'
import { jezyk, t } from './i18n'
import { idOsoby, osoba } from './portfel'
import { czytaj, mowi, przerwijCzytanie, rozpoznawanieDostepne, slucham, nasluchuj, zatrzymajNasluch } from './speech'
import type { IkonaId, KartaDanych, Rozmowa, StanUslug, Wiadomosc, ZdarzenieAgenta } from './types'
import { otworzSkaner, otworzPrzyjmowanie, type WynikZnaku } from './znak-flow'

interface Odpowiedz {
  blad?: string
}

let licznikWiadomosci = 0
let licznikRozmow = 0

function nowaWiadomosc(czesc: Omit<Wiadomosc, 'id'>): Wiadomosc {
  return { id: ++licznikWiadomosci, ...czesc }
}

export const rozmowy = ref<Rozmowa[]>([])
export const idAktywnej = ref<number | null>(null)
export const aktywna = computed<Rozmowa | null>(() => rozmowy.value.find((r) => r.id === idAktywnej.value) ?? null)
export const uslugi = ref<StanUslug | null>(null)
export const trwa = ref(0)
export const bladModelu = ref('')
export const potwierdzenieWToku = ref(false)

export const widok = reactive({
  rozmowa: false,
  historia: false,
  menu: false,
  todo: false,
  dokument: null as string | null,
  dokumentKarta: null as KartaDanych | null,
  faceid: false
})

export const glos = reactive({
  tryb: false,
  stan: 'idle' as 'idle' | 'listen' | 'stt' | 'think' | 'speak' | 'wait',
  uslyszane: '',
  komunikat: '',
  scena: [] as Wiadomosc[]
})

export const agentGotowy = computed(() => Boolean(uslugi.value?.agent))
export const modelGotowy = computed(() => Boolean(uslugi.value?.modelGotowy))
export const modelBielik = computed(() => uslugi.value?.bielik !== false)

function utworzRozmowe(): Rozmowa {
  const r: Rozmowa = {
    id: ++licznikRozmow,
    tytul: '',
    ikona: 'doc',
    ostatnia: '',
    czas: Date.now(),
    nieprzeczytana: false,
    wiadomosci: [],
    historia: [],
    stanSwiata: null,
    glos: false
  }
  rozmowy.value.push(r)
  return r
}

export function nowaRozmowa(): Rozmowa {
  const r = rozmowy.value.find((x) => !x.tytul) ?? utworzRozmowe()
  idAktywnej.value = r.id
  r.nieprzeczytana = false
  widok.rozmowa = true
  return r
}

export function otworzRozmowe(id: number): void {
  const r = rozmowy.value.find((x) => x.id === id)
  if (!r) return
  idAktywnej.value = r.id
  r.nieprzeczytana = false
  widok.historia = false
  widok.rozmowa = true
}

export function rozmowyZHistoria(): Rozmowa[] {
  return [...rozmowy.value].filter((r) => r.tytul).sort((a, b) => b.czas - a.czas)
}

function ikonaTematu(tekst: string): IkonaId {
  const n = tekst.toLowerCase()
  if (/portfel|zgubi|ukrad|zastrz/.test(n)) return 'shield'
  if (/stluczk|stłuczk|kolizj|wypadek|auto|samoch|pojazd|\boc\b|ubezpiecz/.test(n)) return 'car'
  if (/urodzi|dzieck|noworod/.test(n)) return 'baby'
  if (/sms|oszust|dziwn|podejrz/.test(n)) return 'alert'
  if (/skrzynk|pismo|doręczen|doreczen|urzędu|urzedu/.test(n)) return 'mail'
  if (/podatek|zaplac|zapłać|oplat|opłat|kdr|dużej rodziny/.test(n)) return 'coin'
  if (/punkt/.test(n)) return 'clock'
  if (/dowod|dowód|pesel/.test(n)) return 'id'
  if (/zalatwienia|załatwienia|przypomn/.test(n)) return 'bell'
  return 'doc'
}

function dotknijRozmowy(kind: 'user' | 'bot', tekst: string): void {
  const r = aktywna.value
  if (!r) return
  r.czas = Date.now()
  if (kind === 'user' && !r.tytul) {
    r.tytul = tekst.replace(/^📷\s*/, 'Zdjęcie: ')
    r.ikona = ikonaTematu(tekst)
  }
  if (kind === 'bot') r.ostatnia = tekst
}

export function tekstBezHtml(html: string): string {
  const d = document.createElement('div')
  d.innerHTML = html
  return (d.textContent ?? '').replace(/\s+/g, ' ').trim()
}

function dodaj(czesc: Omit<Wiadomosc, 'id'>): Wiadomosc {
  const r = aktywna.value ?? nowaRozmowa()
  const m = nowaWiadomosc(czesc)
  r.wiadomosci.push(m)
  return m
}

function zablokujStare(): void {
  const r = aktywna.value
  if (!r) return
  for (const m of r.wiadomosci) {
    if (m.potwierdzenie && m.stanPotwierdzenia === 'czeka') m.stanPotwierdzenia = 'anulowano'
    if (m.opcje) m.opcje = undefined
    m.pokazDalej = false
  }
}

function tytulRozmowy(): void {
  const r = aktywna.value
  if (r && !r.tytul) {
    r.tytul = t('Nowa rozmowa')
    r.ikona = 'doc'
  }
}

function klodkaPotwierdzenia(): void {
  potwierdzenieWToku.value = true
}

export function faceId(): Promise<void> {
  if (!widok.faceid) {
    widok.faceid = true
    return new Promise((resolve) => {
      setTimeout(() => {
        widok.faceid = false
        resolve()
      }, 1200)
    })
  }
  return Promise.resolve()
}

export async function zapytajAgent(extra: Record<string, unknown> = {}): Promise<Odpowiedz> {
  const r = aktywna.value
  if (!r) return { blad: 'brak rozmowy' }
  const pisze = nowaWiadomosc({ autor: 'bot', pisze: true })
  r.wiadomosci.push(pisze)
  trwa.value++
  if (glos.tryb) glos.stan = 'think'
  try {
    const odpowiedz = await api.agent({
      conv: r.id,
      messages: r.historia,
      stan: r.stanSwiata,
      osoba: idOsoby.value,
      lang: jezyk.value,
      ...extra
    })
    r.historia = odpowiedz.messages
    r.stanSwiata = odpowiedz.stan
    r.wiadomosci = r.wiadomosci.filter((m) => m.id !== pisze.id)
    await pokazZdarzenia(odpowiedz.events ?? [])
    return {}
  } catch (e) {
    r.wiadomosci = r.wiadomosci.filter((m) => m.id !== pisze.id)
    const komunikat = e instanceof Error ? e.message : String(e)
    bladModelu.value = komunikat
    await powiedz(komunikat)
    return { blad: komunikat }
  } finally {
    trwa.value--
    if (trwa.value === 0) potwierdzenieWToku.value = false
    if (glos.tryb && glos.stan === 'think') glos.stan = 'idle'
  }
}

export async function powiedz(tekst: string): Promise<void> {
  zablokujStare()
  dodaj({ autor: 'bot', html: tekst })
  dotknijRozmowy('bot', tekst)
  if (glos.tryb) await wypowiedz(tekst)
}

function czyCzekaNaDzialanie(): boolean {
  const r = aktywna.value
  if (!r) return false
  const ostatnia = r.wiadomosci[r.wiadomosci.length - 1]
  return Boolean(ostatnia?.potwierdzenie && ostatnia.stanPotwierdzenia === 'czeka')
}

async function wypowiedz(tekst: string): Promise<void> {
  if (!glos.tryb || !tekst.trim()) return
  zatrzymajNasluch()
  glos.stan = 'speak'
  await czytaj(tekst, jezyk.value)
  if (!glos.tryb || mowi.value) return
  nastepnyKrokGlosu()
}

function nastepnyKrokGlosu(): void {
  if (!glos.tryb) return
  if (trwa.value || czyCzekaNaDzialanie()) {
    glos.stan = 'wait'
    return
  }
  glos.stan = 'idle'
}

async function pokazZdarzenia(zdarzenia: ZdarzenieAgenta[]): Promise<void> {
  const doWypowiedzenia: string[] = []
  let czekaNaZnak: Extract<ZdarzenieAgenta, { t: 'qrflow' }> | null = null

  for (const e of zdarzenia) {
    if (e.t === 'text') {
      dodaj({ autor: 'bot', html: e.html })
      doWypowiedzenia.push(e.plain)
      dotknijRozmowy('bot', e.plain)
      await nextTick()
      continue
    }
    if (e.t === 'card') {
      const m = dodaj({ autor: 'bot', karta: e })
      if (glos.tryb) glos.scena.push(m)
      await nextTick()
      continue
    }
    if (e.t === 'qr') {
      const m = dodaj({ autor: 'bot', karta: { ...e, t: 'card' }, qr: { title: e.title, code: e.code } })
      if (glos.tryb) glos.scena.push(m)
      if (e.after) dodaj({ autor: 'bot', karta: e.after })
      await nextTick()
      continue
    }
    if (e.t === 'doc') {
      widok.dokument = e.id
      const m = dodaj({ autor: 'bot', karta: { t: 'card', icon: 'id', title: t('Dokument w aplikacji'), note: t('Dotknij karty dokumentu, żeby zobaczyć szczegóły.') } })
      if (glos.tryb) glos.scena.push(m)
      continue
    }
    if (e.t === 'chips' || e.t === 'multi') {
      const m = dodaj({ autor: 'bot', opcje: e.opcje, wielokrotny: e.t === 'multi', wybrane: [], pokazDalej: e.t === 'multi' })
      if (glos.tryb) glos.scena.push(m)
      if (e.mow) doWypowiedzenia.push(e.mow)
      await nextTick()
      continue
    }
    if (e.t === 'confirm') {
      const m = dodaj({
        autor: 'bot',
        karta: e,
        potwierdzenie: { id: e.id ?? '', label: e.label || t('Potwierdź'), tytul: e.title },
        stanPotwierdzenia: 'czeka'
      })
      if (glos.tryb) glos.scena.push(m)
      klodkaPotwierdzenia()
      doWypowiedzenia.push(e.mow || `${e.title ? e.title + '. ' : ''}${t('Sprawdź dane na karcie i potwierdź.')}`)
      await nextTick()
      continue
    }
    if (e.t === 'koniec') {
      if (glos.tryb) zakonczGlos()
      continue
    }
    if (e.t === 'qrflow') {
      czekaNaZnak = e
      continue
    }
  }

  if (czekaNaZnak) {
    if (glos.tryb && doWypowiedzenia.length) await wypowiedz(doWypowiedzenia.join(' '))
    else if (glos.tryb) glos.stan = 'wait'
    await obsluzZnak(czekaNaZnak)
    return
  }
  if (glos.tryb && doWypowiedzenia.length) await wypowiedz(doWypowiedzenia.join(' '))
  else if (glos.tryb) nastepnyKrokGlosu()
}

async function obsluzZnak(e: Extract<ZdarzenieAgenta, { t: 'qrflow' }>): Promise<void> {
  glos.stan = 'wait'
  const wynik: WynikZnaku = e.mode === 'scan'
    ? await otworzSkaner({ cel: e.cel, dokument: e.dok })
    : await otworzPrzyjmowanie({ cel: e.cel })
  const r = await zapytajAgent({ confirm: { id: e.id, ok: Boolean(wynik.ok), wynik: wynik.wynik ?? null } })
  if (r.blad) await powiedz(wynik.ok ? t('Dane zostały przekazane.') : t('Zamknięto skaner.'))
}

export async function wyslij(tekst: string, opcje: { ukryty?: string; glosowo?: boolean } = {}): Promise<void> {
  const tresc = tekst.trim()
  if (!tresc) return
  widok.rozmowa = true
  const r = aktywna.value ?? nowaRozmowa()
  r.historia.push({ role: 'user', content: (opcje.glosowo ? '[głos] ' : '') + (opcje.ukryty ?? tresc) })
  zablokujStare()
  dodaj({ autor: 'user', tekst: tresc })
  dotknijRozmowy('user', tresc)
  await zapytajAgent()
}

export function wybierzOpcje(opcja: string): void {
  const r = aktywna.value
  if (!r) return
  const m = r.wiadomosci[r.wiadomosci.length - 1]
  if (!m?.opcje) return
  m.opcje = undefined
  void wyslij(opcja)
}

export function przelaczWielokrotny(opcja: string): void {
  const r = aktywna.value
  const m = r?.wiadomosci[r.wiadomosci.length - 1]
  if (!m?.wielokrotny) return
  m.wybrane = m.wybrane ?? []
  m.wybrane = m.wybrane.includes(opcja) ? m.wybrane.filter((x) => x !== opcja) : [...m.wybrane, opcja]
}

export function zatwierdzWielokrotny(): void {
  const r = aktywna.value
  const m = r?.wiadomosci[r.wiadomosci.length - 1]
  if (!m?.wielokrotny || !m.wybrane?.length || !m.opcje) return
  const wybrane = m.opcje.filter((o) => m.wybrane?.includes(o))
  m.opcje = undefined
  m.pokazDalej = false
  void wyslij(wybrane.join(', '))
}

export async function potwierdz(id: string, ok: boolean): Promise<void> {
  const r = aktywna.value
  if (!r) return
  const m = r.wiadomosci.find((x) => x.potwierdzenie?.id === id)
  if (!ok) {
    if (m) m.stanPotwierdzenia = 'anulowano'
    await zapytajAgent({ confirm: { id, ok: false } })
    return
  }
  await faceId()
  if (m) m.stanPotwierdzenia = 'ok'
  await zapytajAgent({ confirm: { id, ok: true } })
}

export async function wyslijZdjecie(): Promise<void> {
  widok.rozmowa = true
  const r = aktywna.value ?? nowaRozmowa()
  r.historia.push({
    role: 'user',
    content: '[zdjęcie] Zdjęcie dowodu rejestracyjnego pojazdu. Odczyt: numer rejestracyjny WE 4K221, VIN WVWZZZAUZKW118204, data pierwszej rejestracji 14.03.2019, Volkswagen Golf. Właściciel: Marek Zieliński.'
  })
  zablokujStare()
  dodaj({ autor: 'user', tekst: '📷 zdjęcie dowodu rejestracyjnego' })
  dotknijRozmowy('user', 'Zdjęcie dowodu rejestracyjnego')
  await zapytajAgent()
}

export function otworzTemat(tekst: string): void {
  const r = aktywna.value
  if (r?.tytul) nowaRozmowa()
  widok.rozmowa = true
  widok.todo = false
  void wyslij(tekst)
}

export function uruchomGlos(): void {
  if (!rozpoznawanieDostepne.value) return
  widok.rozmowa = true
  widok.historia = false
  glos.tryb = true
  glos.stan = 'idle'
  glos.uslyszane = ''
  glos.komunikat = ''
  if (!aktywna.value) nowaRozmowa()
  void petlaGlosowa()
}

async function petlaGlosowa(): Promise<void> {
  while (glos.tryb) {
    if (trwa.value || czyCzekaNaDzialanie()) {
      glos.stan = 'wait'
      return
    }
    glos.stan = 'listen'
    const wynik = await nasluchuj(jezyk.value)
    if (!glos.tryb) return
    if (!wynik.tekst) {
      if (wynik.blad === 'brak-mikrofonu') {
        glos.komunikat = t('Brak dostępu do mikrofonu. Zezwól na mikrofon w ustawieniach przeglądarki.')
        glos.stan = 'idle'
        return
      }
      glos.komunikat = t('Nic nie usłyszałem. Dotknij mikrofonu i powiedz, w czym pomóc.')
      glos.stan = 'idle'
      return
    }
    glos.komunikat = ''
    glos.uslyszane = wynik.tekst
    glos.stan = 'stt'
    await wyslij(wynik.tekst, { glosowo: true })
    if (!glos.tryb) return
    if (trwa.value || czyCzekaNaDzialanie() || mowi.value) {
      glos.stan = mowi.value ? 'speak' : 'wait'
      return
    }
  }
}

export function wznowGlos(): void {
  if (!glos.tryb) return
  if (trwa.value || mowi.value) return
  void petlaGlosowa()
}

export function dotknijMikrofonu(): void {
  if (!glos.tryb) return
  if (slucham.value) {
    zatrzymajNasluch()
    glos.stan = 'idle'
    return
  }
  if (mowi.value) {
    przerwijCzytanie()
    void petlaGlosowa()
    return
  }
  if (glos.stan === 'wait') return
  void petlaGlosowa()
}

export function zakonczGlos(): void {
  glos.tryb = false
  glos.stan = 'idle'
  glos.komunikat = ''
  glos.uslyszane = ''
  glos.scena = []
  zatrzymajNasluch()
  przerwijCzytanie()
}

export function zamknijRozmowe(): void {
  if (glos.tryb) zakonczGlos()
  widok.historia = false
  widok.rozmowa = false
}

export function przygotujPowitanie(): void {
  if (!rozmowy.value.length) {
    utworzRozmowe()
    idAktywnej.value = rozmowy.value[0].id
    return
  }
  if (idAktywnej.value === null) idAktywnej.value = rozmowy.value[0].id
}

export const sugerowane = computed(() => osoba.value.sugg)

export async function pobierzStanUslug(): Promise<void> {
  try {
    uslugi.value = await api.zdrowie()
  } catch {
    uslugi.value = null
  }
}

export function pustyStan(): boolean {
  return !aktywna.value || aktywna.value.wiadomosci.length === 0
}

export function wolacz(): string {
  return osoba.value.wolacz
}

export function powitanie(): string {
  return `${t('W czym mogę pomóc')}, ${osoba.value.wolacz}?`
}

export { tytulRozmowy }
