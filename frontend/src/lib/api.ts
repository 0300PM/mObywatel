import type { OdpowiedzAgenta, StanUslug } from './types'

async function pobierz<T>(url: string, init?: RequestInit): Promise<T> {
  const r = await fetch(url, init)
  const dane = (await r.json().catch(() => ({}))) as T & { error?: string }
  if (!r.ok) throw new Error(dane.error || `HTTP ${r.status}`)
  return dane
}

export const api = {
  zdrowie: (): Promise<StanUslug> => pobierz<StanUslug>('/api/health', { cache: 'no-store' }),

  agent: (body: unknown): Promise<OdpowiedzAgenta> =>
    pobierz<OdpowiedzAgenta>('/api/agent', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body)
    }),

  znakKto: (token: number, dev: string) =>
    pobierz<{ dev: string | null; kind?: string; kto?: string; cel?: string; zakres?: string[][] }>(
      `/api/znak/kto?t=${token}&dev=${encodeURIComponent(dev)}`
    ),

  znakPrzekaz: (body: { to: string; from?: string; ok: boolean; dane?: unknown }) =>
    pobierz<{ ok: boolean }>('/api/znak/przekaz', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body)
    }),

  znakBeat: (body: { dev: string; token: number; kind: 'telefon' | 'web'; kto?: string; cel?: string; zakres?: string[][] }) =>
    pobierz<{ otrzymane: { ok: boolean; dane?: Record<string, unknown> }[]; skanuje: boolean; zmien: boolean }>('/api/znak/beat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body)
    }),

  i18n: (lang: string) => pobierz<{ lang: string; t: Record<string, string> }>(`/api/i18n?lang=${lang}`),

  brakujaceTlumaczenia: (lang: string, teksty: string[]) =>
    pobierz<{ t: Record<string, string> }>('/api/i18n/brak', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ lang, teksty })
    })
}
