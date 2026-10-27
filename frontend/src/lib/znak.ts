const N = 32
const SYNC = [1, 1, 1, 1, 1, 0]
const RING = 37 / 34
const SQ = 0.93

export interface OdczytanyZnak {
  token: number
  x: number
  y: number
  size: number
}

function crc10(v: number): number {
  let c = 0
  for (let i = 15; i >= 0; i--) {
    const b = ((v >> i) & 1) ^ ((c >> 9) & 1)
    c = (c << 1) & 0x3ff
    if (b) c ^= 0x233
  }
  return c
}

export function bity(token: number): number[] {
  const b = [...SYNC]
  for (let i = 15; i >= 0; i--) b.push((token >> i) & 1)
  const c = crc10(token)
  for (let i = 9; i >= 0; i--) b.push((c >> i) & 1)
  return b
}

export function sprawdz(b: number[]): number | null {
  for (let i = 0; i < 6; i++) if (b[i] !== SYNC[i]) return null
  let t = 0
  for (let i = 6; i < 22; i++) t = (t << 1) | b[i]
  let c = 0
  for (let i = 22; i < 32; i++) c = (c << 1) | b[i]
  return crc10(t) === c ? t : null
}

export function svgZnaku(token: number, opcje: { color?: string; img?: string } = {}): string {
  const b = bity(token)
  const red = opcje.color || '#dc143c'
  const img = opcje.img || 'assets/icon-mobywatel.svg'
  let d = ''
  for (let i = 0; i < N; i++) {
    if (!b[i]) continue
    const a = -Math.PI / 2 + (i / N) * Math.PI * 2
    d += `<circle cx="${(Math.cos(a) * 37).toFixed(2)}" cy="${(Math.sin(a) * 37).toFixed(2)}" r="2.9" fill="${red}"/>`
  }
  return `<svg class="znak" viewBox="-50 -50 100 100" role="img" aria-label="Znak mObywatela"><circle r="49" fill="#fff"/>${d}<image href="${img}" x="-17" y="-17" width="34" height="34"/></svg>`
}

export function odkodujZnak(dane: Uint8ClampedArray, w: number, h: number): OdczytanyZnak | null {
  const n = w * h
  const score = new Int16Array(n)
  const hist = new Uint32Array(256)
  for (let i = 0, p = 0; i < n; i++, p += 4) {
    const r = dane[p]
    const g = dane[p + 1]
    const bl = dane[p + 2]
    let s = r - (g > bl ? g : bl)
    if (r < 70) s = 0
    s = s < 0 ? 0 : s
    score[i] = s
    hist[s > 255 ? 255 : s]++
  }
  let acc = 0
  let p995 = 255
  for (let v = 255; v >= 0; v--) {
    acc += hist[v]
    if (acc > n * 0.006) {
      p995 = v
      break
    }
  }
  const prog = Math.max(30, p995 * 0.45)

  const lab = new Int32Array(n).fill(-1)
  const par: number[] = []
  const find = (x: number): number => {
    while (par[x] !== x) {
      par[x] = par[par[x]]
      x = par[x]
    }
    return x
  }
  for (let y = 0; y < h; y++) {
    for (let x = 0; x < w; x++) {
      const i = y * w + x
      if (score[i] < prog) continue
      const L = x > 0 ? lab[i - 1] : -1
      const U = y > 0 ? lab[i - w] : -1
      if (L < 0 && U < 0) {
        lab[i] = par.length
        par.push(par.length)
      } else if (L >= 0 && U >= 0) {
        const a = find(L)
        const c = find(U)
        lab[i] = a
        if (a !== c) par[c] = a
      } else lab[i] = L >= 0 ? L : U
    }
  }

  interface Skupisko {
    a: number
    x0: number
    x1: number
    y0: number
    y1: number
    sx: number
    sy: number
    sxx: number
    syy: number
    sxy: number
  }
  const comp = new Map<number, Skupisko>()
  for (let i = 0; i < n; i++) {
    if (lab[i] < 0) continue
    const r = find(lab[i])
    const x = i % w
    const y = (i / w) | 0
    let c = comp.get(r)
    if (!c) {
      c = { a: 0, x0: x, x1: x, y0: y, y1: y, sx: 0, sy: 0, sxx: 0, syy: 0, sxy: 0 }
      comp.set(r, c)
    }
    c.a++
    if (x < c.x0) c.x0 = x
    if (x > c.x1) c.x1 = x
    if (y < c.y0) c.y0 = y
    if (y > c.y1) c.y1 = y
    c.sx += x
    c.sy += y
    c.sxx += x * x
    c.syy += y * y
    c.sxy += x * y
  }

  const kandydaci = [...comp.values()]
    .filter((c) => {
      const bw = c.x1 - c.x0 + 1
      const bh = c.y1 - c.y0 + 1
      return c.a >= 30 && bw / bh > 0.5 && bw / bh < 2 && c.a / (bw * bh) > 0.35 && bw < w * 0.6
    })
    .sort((a, b) => b.a - a.a)
    .slice(0, 6)

  const smp = (x: number, y: number): number => {
    const xi = Math.round(x)
    const yi = Math.round(y)
    if (xi < 1 || yi < 1 || xi >= w - 1 || yi >= h - 1) return 0
    const i = yi * w + xi
    return (score[i] * 2 + score[i - 1] + score[i + 1] + score[i - w] + score[i + w]) / 6
  }

  for (const c of kandydaci) {
    const cx = c.sx / c.a
    const cy = c.sy / c.a
    const vxx = c.sxx / c.a - cx * cx
    const vyy = c.syy / c.a - cy * cy
    const vxy = c.sxy / c.a - cx * cy
    const tr = vxx + vyy
    const de = Math.sqrt(Math.max(0, ((vxx - vyy) * (vxx - vyy)) / 4 + vxy * vxy))
    const l1 = tr / 2 + de
    const l2 = Math.max(1e-3, tr / 2 - de)
    const th = 0.5 * Math.atan2(2 * vxy, vxx - vyy)
    const s1 = Math.sqrt(12 * l1) * SQ
    const s2 = Math.sqrt(12 * l2) * SQ
    const ux = Math.cos(th)
    const uy = Math.sin(th)

    for (const f of [1, 0.95, 1.05, 0.9, 1.1, 0.85, 1.15]) {
      const r1 = s1 * RING * f
      const r2 = s2 * RING * f
      const P = new Float32Array(256)
      const pt = (a: number, m: number): [number, number] => {
        const ca = Math.cos(a) * m
        const sa = Math.sin(a) * m
        const e1 = ca * ux + sa * uy
        const e2 = -ca * uy + sa * ux
        return [cx + e1 * r1 * ux - e2 * r2 * uy, cy + e1 * r1 * uy + e2 * r2 * ux]
      }
      for (let k = 0; k < 256; k++) {
        const a = -Math.PI / 2 + (k / 256) * Math.PI * 2
        let m = 0
        for (const q of [0.96, 1, 1.04]) {
          const [x, y] = pt(a, q)
          const v = smp(x, y)
          if (v > m) m = v
        }
        P[k] = m
      }
      let best: { con: number; v: number[]; thr: number } | null = null
      for (let ph = 0; ph < 8; ph++) {
        const v: number[] = []
        for (let s = 0; s < N; s++) {
          let m = 0
          for (let j = -1; j <= 1; j++) m += P[(ph + s * 8 + j + 256) % 256]
          v.push(m / 3)
        }
        const mx = Math.max(...v)
        const mn = Math.min(...v)
        if (mx - mn < 15) continue
        const thr = (mx + mn) / 2
        let con = 0
        for (const x of v) con += Math.abs(x - thr)
        con /= mx - mn
        if (!best || con > best.con) best = { con, v, thr }
      }
      if (!best) continue
      const progi = best.v.map((x) => (x > best.thr ? 1 : 0))
      for (const dir of [1, -1]) {
        for (let s = 0; s < N; s++) {
          const r: number[] = []
          for (let i = 0; i < N; i++) r.push(progi[(((s + dir * i) % N) + N) % N])
          const t = sprawdz(r)
          if (t !== null) return { token: t, x: cx / w, y: cy / h, size: s1 / w }
        }
      }
    }
  }
  return null
}
