export type Plec = 'K' | 'M'

export type IkonaId =
  | 'doc' | 'shield' | 'car' | 'baby' | 'mail' | 'alert' | 'check' | 'qr' | 'coin' | 'clock'
  | 'id' | 'bell' | 'db' | 'chev' | 'back' | 'dots' | 'scan'

export interface Sylwetka {
  plate?: string
  model?: string
  kolor?: string
  nr?: string
}

export interface Dokument {
  id: string
  name: string
  img: string
  strip: string
  sub: string
  line: string
  holder: string
  f: string[][]
  rows: string[][]
  photo?: number
  alert?: string
  plate?: string
  model?: string
  kolor?: string
  who?: string
  more?: Sylwetka[]
}

export interface Sprawa {
  i: IkonaId
  h: string
  d: string
  k: string
  s?: string
  q?: string
  u?: number
}

export interface Osoba {
  id: string
  plec: Plec
  imie: string
  nazwisko: string
  wolacz: string
  opis: string
  docs: Dokument[]
  tiles: Sprawa[]
  moje: Record<string, string>
  sugg: string[][]
  ask: Record<string, string>
}

export type WariantUkladu = 'stos' | 'karuzela' | 'pion' | 'lista' | 'siatka'

export interface Uklad {
  id: WariantUkladu
  nazwa: string
  opis: string
}

export interface WierszDanych {
  k: string
  v: string
}

export interface KartaDanych {
  t: 'card' | 'confirm'
  icon?: IkonaId
  title?: string
  source?: string
  rows?: string[][]
  body?: string
  flag?: string
  note?: string
  label?: string
  tone?: string
  pojazd?: Sylwetka | null
  tl?: number
  id?: string
  mow?: string
}

export type ZdarzenieAgenta =
  | { t: 'text'; html: string; plain: string; md?: string; tl?: number }
  | (KartaDanych & { t: 'card' })
  | { t: 'qr'; title?: string; code?: string; after?: KartaDanych }
  | { t: 'doc'; id: string }
  | { t: 'chips'; opcje: string[]; mow?: string; tl?: number }
  | { t: 'multi'; opcje: string[]; mow?: string; tl?: number }
  | { t: 'qrflow'; id: string; mode: 'scan' | 'show'; cel?: string; kto?: string; dok?: string }
  | { t: 'koniec' }
  | (KartaDanych & { t: 'confirm' })

export interface OdpowiedzAgenta {
  messages: unknown[]
  stan: unknown
  events: ZdarzenieAgenta[]
  czeka?: string | null
  error?: string
}

export interface StanUslug {
  agent: boolean
  provider: string
  model: string
  modelGotowy: boolean
  bielik?: boolean
  klucz?: boolean
  konto?: boolean
  kontoOk?: boolean
  kluczRodzaj?: 'ok' | 'brak' | 'globalny' | 'krotki'
  ostrzezenia?: string[]
  config?: string
  glos: Record<string, string>
  stt: boolean
  tts: boolean
  komunikat: string
}

export interface Wiadomosc {
  id: number
  autor: 'user' | 'bot'
  tekst?: string
  html?: string
  karta?: KartaDanych
  opcje?: string[]
  wielokrotny?: boolean
  wybrane?: string[]
  pokazDalej?: boolean
  qr?: { title?: string; code?: string }
  potwierdzenie?: { id: string; label: string; tytul?: string }
  stanPotwierdzenia?: 'czeka' | 'ok' | 'anulowano'
  pisze?: boolean
}

export interface Rozmowa {
  id: number
  tytul: string
  ikona: IkonaId
  ostatnia: string
  czas: number
  nieprzeczytana: boolean
  wiadomosci: Wiadomosc[]
  historia: unknown[]
  stanSwiata: unknown
  glos: boolean
}
