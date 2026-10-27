import { BAZA } from './sylwetki-baza'

const KOLORY: Record<string, string> = {
  biały: '#f1f2f4', bialy: '#f1f2f4', czarny: '#1d2026', srebrny: '#b8bdc5', szary: '#878d96', grafitowy: '#4b5159',
  czerwony: '#c6262d', bordowy: '#7a1f2b', niebieski: '#2d62c6', granatowy: '#1e3462', zielony: '#2f7a4d',
  'żółty': '#e6bc2f', zolty: '#e6bc2f', 'pomarańczowy': '#e5762a', pomaranczowy: '#e5762a', 'brązowy': '#6a4932',
  brazowy: '#6a4932', 'beżowy': '#cbb692', bezowy: '#cbb692', fioletowy: '#6b4a9e', 'złoty': '#c7a34a',
  zloty: '#c7a34a', 'błękitny': '#5aa0dc'
}

const ALIAS: [RegExp, string][] = [
  [/\bvw\b/g, 'volkswagen'],
  [/mercedes(?!-benz)/g, 'mercedes-benz'],
  [/\bclass\b/g, 'klasa'],
  [/\bseria\s*(\d)/g, 'seria $1'],
  [/škoda/g, 'skoda'],
  [/citroën/g, 'citroen']
]

const DOMYSLNE_WYMIARY: Record<string, [number, number, number]> = {
  hatch: [4300, 1460, 2640],
  kombi: [4650, 1480, 2700],
  suv: [4550, 1660, 2700],
  sedan: [4700, 1450, 2800],
  van: [4950, 1950, 3050],
  furgon: [5600, 2550, 3500],
  autokar: [12000, 3600, 6000]
}

interface Sylwetka {
  klucz: string | null
  typ: string
  L: number
  H: number
  wb: number
}

interface Profil {
  hb: number
  nose: number
  hood: number
  a: number
  re: number
  dr: number
  tail: [number, number][]
  g: [number, number, number, number]
  rk?: number
  sideStop?: number
  bus?: number
}

interface Krzywe {
  d: string
  g: string
  pil: number[]
  gy: number
  gt: number
  xf: number
  xr: number
  r: number
  big: boolean
  L: number
  H: number
}

const PROMIEN_TYLU: Record<string, number> = { hatch: 0.3, crossover: 0.32, liftback: 0.45, sedan: 0.35, coupe: 0.4, kabriolet: 0.3, mini: 0.55 }

const KONTUR: Record<string, Profil> = {
  hatch: { hb: 0.62, nose: 0.44, hood: 0.25, a: 0.43, re: 0.76, dr: 0.05, tail: [[0.905, 0.74], [0.978, 0.6], [1, 0.42]], g: [0.27, 0.45, 0.75, 0.885] },
  mini: { hb: 0.6, nose: 0.46, hood: 0.2, a: 0.39, re: 0.86, dr: 0.03, tail: [[0.965, 0.72], [0.995, 0.56], [1, 0.4]], g: [0.22, 0.41, 0.85, 0.95] },
  kombi: { hb: 0.63, nose: 0.43, hood: 0.25, a: 0.43, re: 0.91, dr: 0.035, tail: [[0.975, 0.7], [0.995, 0.56], [1, 0.4]], g: [0.27, 0.45, 0.9, 0.965] },
  liftback: { hb: 0.63, nose: 0.42, hood: 0.25, a: 0.44, re: 0.7, dr: 0.03, tail: [[0.93, 0.73], [0.985, 0.68], [1, 0.44]], g: [0.27, 0.46, 0.69, 0.91] },
  sedan: { hb: 0.63, nose: 0.42, hood: 0.26, a: 0.45, re: 0.67, dr: 0.025, tail: [[0.83, 0.72], [0.975, 0.7], [1, 0.46]], g: [0.28, 0.47, 0.66, 0.82] },
  coupe: { hb: 0.62, nose: 0.4, hood: 0.32, a: 0.52, re: 0.68, dr: 0.05, tail: [[0.9, 0.7], [0.98, 0.66], [1, 0.44]], g: [0.34, 0.54, 0.67, 0.88] },
  kabriolet: { hb: 0.7, nose: 0.42, hood: 0.34, a: 0.5, re: 0.6, dr: 0.08, tail: [[0.8, 0.74], [0.97, 0.72], [1, 0.48]], g: [0.36, 0.51, 0.59, 0.7] },
  crossover: { hb: 0.62, nose: 0.47, hood: 0.25, a: 0.45, re: 0.77, dr: 0.06, tail: [[0.925, 0.74], [0.985, 0.6], [1, 0.43]], g: [0.27, 0.47, 0.76, 0.9] },
  suv: { hb: 0.61, nose: 0.5, hood: 0.25, a: 0.43, re: 0.89, dr: 0.025, tail: [[0.975, 0.72], [0.995, 0.6], [1, 0.44]], g: [0.27, 0.45, 0.88, 0.965] },
  mpv: { hb: 0.58, nose: 0.43, hood: 0.17, a: 0.37, re: 0.92, dr: 0.03, tail: [[0.985, 0.7], [1, 0.55], [1, 0.42]], g: [0.19, 0.39, 0.91, 0.975] },
  kombivan: { hb: 0.55, nose: 0.42, hood: 0.16, a: 0.33, re: 0.95, dr: 0.01, tail: [[0.995, 0.75], [1, 0.55], [1, 0.4]], g: [0.18, 0.35, 0.94, 0.985] },
  van: { hb: 0.53, nose: 0.36, hood: 0.1, a: 0.27, re: 0.985, dr: 0, tail: [[1, 0.86], [1, 0.6], [1, 0.35]], g: [0.12, 0.29, 0.97, 0.99], sideStop: 0.55 },
  furgon: { hb: 0.5, nose: 0.32, hood: 0.1, a: 0.23, re: 0.99, dr: 0, tail: [[1, 0.92], [1, 0.6], [1, 0.3]], g: [0.115, 0.25, 0.3, 0.32], sideStop: 0.32 },
  pickup: { hb: 0.6, nose: 0.52, hood: 0.24, a: 0.4, re: 0.62, dr: 0.02, tail: [[0.64, 0.62], [1, 0.62], [1, 0.42]], g: [0.26, 0.42, 0.61, 0.64] },
  autokar: { hb: 0.62, nose: 0.3, hood: 0.005, a: 0.035, re: 0.995, dr: 0, tail: [[1, 0.94], [1, 0.6], [1, 0.25]], g: [0.012, 0.04, 0.97, 0.99], bus: 1 }
}

const norm = (s: string): string => String(s ?? '').toLowerCase().replace(/\s+/g, ' ').trim()

export function znajdz(model: string): Sylwetka {
  let n = norm(model)
  for (const [wzorzec, zamiana] of ALIAS) n = n.replace(wzorzec, zamiana)
  let najlepszy: string | null = null
  for (const klucz of Object.keys(BAZA)) {
    if (n.includes(klucz) && (!najlepszy || klucz.length > najlepszy.length)) najlepszy = klucz
  }
  if (najlepszy) {
    const [typ, L, H, wb] = BAZA[najlepszy]
    return { klucz: najlepszy, typ, L, H, wb }
  }
  const typ = /kombi|combi|variant|touring|avant|estate|\bsw\b|tourer/.test(n) ? 'kombi'
    : /suv|4x4|x-trail|cross/.test(n) ? 'suv'
      : /bus|autokar|autobus/.test(n) ? 'autokar'
        : /furgon|dostawcz/.test(n) ? 'furgon'
          : /\bvan\b/.test(n) ? 'van'
            : /sedan|limuzyn/.test(n) ? 'sedan'
              : 'hatch'
  const [L, H, wb] = DOMYSLNE_WYMIARY[typ] ?? DOMYSLNE_WYMIARY.hatch
  return { klucz: null, typ, L, H, wb }
}

export function kolor(k: string): string {
  const n = norm(k)
  for (const nazwa of Object.keys(KOLORY)) if (n.startsWith(nazwa.slice(0, 5))) return KOLORY[nazwa]
  return /^#[0-9a-f]{6}$/i.test(k || '') ? k : '#9aa1ab'
}

const rgb = (hex: string): number[] => [1, 3, 5].map((i) => parseInt(hex.slice(i, i + 2), 16))

const mix = (h: string, t: string, a: number): string =>
  '#' + rgb(h).map((v, i) => Math.round(v + (rgb(t)[i] - v) * a).toString(16).padStart(2, '0')).join('')

const lum = (h: string): number => {
  const [r, g, b] = rgb(h).map((v) => v / 255)
  return 0.2126 * r + 0.7152 * g + 0.0722 * b
}

function profil(s: Sylwetka): Krzywe {
  const { typ, L, H, wb } = s
  const big = typ === 'autokar' || typ === 'furgon'
  const r = typ === 'autokar' ? 520
    : typ === 'furgon' ? 360
      : typ === 'suv' || typ === 'pickup' ? 360
        : typ === 'van' || typ === 'kombivan' || typ === 'mpv' ? 335
          : typ === 'mini' ? 290
            : typ === 'coupe' || typ === 'kabriolet' ? 330
              : 315
  const c = typ === 'suv' || typ === 'pickup' ? 250
    : typ === 'crossover' ? 215
      : big || typ === 'van' ? 230
        : typ === 'kombivan' || typ === 'mpv' ? 190
          : 165
  const ohf = typ === 'autokar' ? L * 0.21
    : typ === 'furgon' || typ === 'van' ? (L - wb) * 0.47
      : (L - wb) * 0.52
  const xf = ohf
  const xr = ohf + wb
  const t = KONTUR[typ]
  const hb = H * t.hb
  const ny = H * t.nose
  const top = H
  const rd = H * t.dr
  const X = (f: number): number => f * L
  const yb = c + (big ? 60 : 70)

  const d: string[] = []
  d.push(`M${X(0.012)} ${-yb}`)
  d.push(`C${X(-0.004)} ${-yb - 60} ${X(-0.006)} ${-ny + 40} ${X(0.006)} ${-ny}`)
  d.push(`Q${X(0.03)} ${-ny - H * 0.07} ${X(0.09)} ${-ny - H * 0.09}`)
  d.push(`L${X(t.hood)} ${-hb}`)
  d.push(`Q${X(t.hood + (t.a - t.hood) * 0.55)} ${-(hb + (top - hb) * 0.82)} ${X(t.a)} ${-top}`)
  d.push(`Q${X((t.a + t.re) / 2)} ${-top - H * 0.012} ${X(t.re)} ${-(top - rd)}`)
  const tail = t.tail
  const rk = t.rk ?? PROMIEN_TYLU[typ] ?? 0.85
  const yRe = top - rd
  const y0 = H * tail[0][1]
  d.push(`Q${X(t.re + (tail[0][0] - t.re) * rk)} ${-(yRe - (yRe - y0) * (rk < 0.6 ? 0.12 : 0.02))} ${X(tail[0][0])} ${-y0}`)
  d.push(`Q${X(tail[1][0])} ${-H * (tail[0][1] - 0.02)} ${X(tail[1][0])} ${-H * tail[1][1]}`)
  d.push(`L${X(tail[2][0])} ${-H * tail[2][1]}`)
  d.push(`Q${X(1.004)} ${-yb - 40} ${X(0.985)} ${-yb}`)
  const R = r + (big ? 60 : 45)
  const dx = Math.sqrt(Math.max(1, R * R - (r - c) * (r - c)))
  d.push(`L${xr + dx + 20} ${-c}`)
  d.push(`L${xr + dx} ${-c}`)
  d.push(`A${R} ${R} 0 1 0 ${xr - dx} ${-c}`)
  d.push(`L${xf + dx} ${-c}`)
  d.push(`A${R} ${R} 0 1 0 ${xf - dx} ${-c}`)
  d.push(`L${X(0.03)} ${-c}`)
  d.push(`Q${X(0.012)} ${-c} ${X(0.012)} ${-yb}Z`)

  const [g0, g1, g2, g3] = t.g
  const gy = hb + H * 0.035
  const gt = top - H * 0.075
  let g: string
  if (t.bus) {
    g = `M${X(g0)} ${-H * 0.3}L${X(g0 + 0.006)} ${-gt}L${X(g3)} ${-gt}L${X(g3)} ${-gy}L${X(0.06)} ${-gy}Q${X(0.03)} ${-gy} ${X(0.025)} ${-H * 0.3}Z`
  } else if (t.sideStop) {
    g = `M${X(g0 + 0.01)} ${-gy}L${X(g1 - 0.01)} ${-gt}L${X(g1 + 0.06)} ${-gt}L${X(t.sideStop - 0.02)} ${-gt}L${X(t.sideStop - 0.02)} ${-gy}Z`
  } else {
    g = `M${X(g0 + 0.02)} ${-gy}Q${X(g0 + (g1 - g0) * 0.6)} ${-(gy + (gt - gy) * 0.85)} ${X(g1 + 0.015)} ${-gt}`
      + `Q${X((g1 + g2) / 2)} ${-gt - H * 0.01} ${X(g2 - 0.01)} ${-(gt - rd * 0.6)}`
      + `Q${X(g3 - 0.005)} ${-(gt - rd * 0.6)} ${X(g3 - 0.015)} ${-gy}Z`
  }

  const pil: number[] = []
  if (!t.bus && !t.sideStop && typ !== 'coupe' && typ !== 'kabriolet') {
    const pb = g1 + (g2 - g1) * (typ === 'mini' || (typ === 'hatch' && L < 3900) ? 0.55 : 0.47)
    pil.push(pb)
    if ((typ === 'kombi' || typ === 'suv' || typ === 'mpv' || typ === 'kombivan') && g3 - g2 < 0.12) pil.push(g2 - 0.005)
  }
  if (t.bus) for (let i = 1; i < 9; i++) pil.push(0.06 + i * (0.96 - 0.06) / 9)

  return { d: d.join(''), g, pil: pil.map(X), gy, gt, xf, xr, r, big, L, H }
}

export interface OpcjeSylwetki {
  label?: string
  shadow?: boolean
  glass?: string
}

let uid = 0

export function svg(model: string, kolorNazwa: string, opcje: OpcjeSylwetki = {}): string {
  const s = znajdz(model)
  const p = profil(s)
  const col = kolor(kolorNazwa)
  const id = 'sy' + (++uid)
  const dark = lum(col) < 0.25
  const light = lum(col) > 0.8
  const pad = 120
  const w = p.L + 2 * pad
  const h = p.H + pad * 1.2
  const glass = opcje.glass || '#2a3442'
  const stroke = light ? 'rgba(20,25,35,.28)' : 'rgba(0,0,0,.18)'
  const wheel = (x: number): string =>
    `<g transform="translate(${x} ${-p.r})"><circle r="${p.r}" fill="#1b1d22"/><circle r="${p.r * 0.64}" fill="#9aa0a8"/><circle r="${p.r * 0.5}" fill="#c9cdd3"/><circle r="${p.r * 0.16}" fill="#80868f"/></g>`
  const pillars = p.pil.map((x) => `<rect x="${x - 26}" y="${-p.gt - 20}" width="52" height="${p.gt - p.gy + 40}" fill="${col}"/>`).join('')
  const shadow = opcje.shadow === false ? ''
    : `<ellipse cx="${p.L / 2}" cy="6" rx="${p.L * 0.48}" ry="${p.big ? 60 : 42}" fill="rgba(0,0,0,.22)"/>`
  const label = (opcje.label || model || 'Pojazd').replace(/"/g, '')
  return `<svg class="sylwetka" viewBox="${-pad} ${-p.H - pad * 0.6} ${w} ${h}" role="img" aria-label="${label}" preserveAspectRatio="xMidYMax meet">
<defs><linearGradient id="${id}b" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="${mix(col, '#ffffff', dark ? 0.18 : 0.22)}"/><stop offset=".55" stop-color="${col}"/><stop offset="1" stop-color="${mix(col, '#000000', dark ? 0.25 : 0.32)}"/></linearGradient>
<linearGradient id="${id}g" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="${mix(glass, '#ffffff', 0.28)}"/><stop offset=".6" stop-color="${glass}"/><stop offset="1" stop-color="${mix(glass, '#000000', 0.2)}"/></linearGradient>
<clipPath id="${id}c"><path d="${p.g}"/></clipPath></defs>
${shadow}<path d="${p.d}" fill="url(#${id}b)" stroke="${stroke}" stroke-width="${p.big ? 14 : 9}" stroke-linejoin="round"/>
<path d="${p.g}" fill="url(#${id}g)"/><g clip-path="url(#${id}c)">${pillars}</g>
${wheel(p.xf)}${wheel(p.xr)}</svg>`
}
