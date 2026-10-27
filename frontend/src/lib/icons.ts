import type { IkonaId } from './types'

type Ikona = IkonaId | 'x' | 'pc' | 'ph' | 'inbox' | 'mic' | 'send' | 'camera' | 'plus' | 'history' | 'home'

export const ICONS: Record<Ikona, string> = {
  doc: '<path d="M7 3.5h7l4 4V20.5H7z"/><path d="M14 3.5v4h4M10 12h5M10 16h5"/>',
  shield: '<path d="M12 3.5 5.5 6v5c0 4.3 2.8 7.8 6.5 9.5 3.7-1.7 6.5-5.2 6.5-9.5V6z"/><path d="m9.2 12 2 2 3.6-3.8"/>',
  car: '<path d="M5 16.5v-4l2-5h10l2 5v4"/><path d="M4 16.5h16v2.5H4z"/><circle cx="8" cy="13.6" r=".9"/><circle cx="16" cy="13.6" r=".9"/>',
  baby: '<circle cx="12" cy="9" r="4.6"/><path d="M10.4 8.6h.01M13.6 8.6h.01M10.6 10.8s.6.6 1.4.6 1.4-.6 1.4-.6M6.8 20c1-2.8 3-4.3 5.2-4.3s4.2 1.5 5.2 4.3"/>',
  mail: '<rect x="3.5" y="5.5" width="17" height="13" rx="2.5"/><path d="m4.5 7.5 7.5 5.5 7.5-5.5"/>',
  alert: '<path d="M12 4.5 3 19.5h18z"/><path d="M12 10v4M12 17h.01"/>',
  check: '<circle cx="12" cy="12" r="8.5"/><path d="m8.3 12.3 2.6 2.6 4.8-5"/>',
  qr: '<path d="M4.5 4.5h5.5v5.5H4.5zM14 4.5h5.5v5.5H14zM4.5 14h5.5v5.5H4.5zM14 14h2v2h-2zM17.5 17.5h2v2h-2zM14 17.5h2M17.5 14h2"/>',
  coin: '<circle cx="12" cy="12" r="8.5"/><path d="M12 7.5v9M14.6 9.8c0-1-1.1-1.6-2.6-1.6s-2.6.6-2.6 1.6 1.1 1.5 2.6 1.9 2.6.9 2.6 1.9-1.1 1.7-2.6 1.7-2.6-.6-2.6-1.7"/>',
  clock: '<circle cx="12" cy="12" r="8.5"/><path d="M12 7.5V12l3 2"/>',
  id: '<rect x="3.5" y="5.5" width="17" height="13" rx="2.5"/><circle cx="9" cy="11" r="2"/><path d="M6 15.5c.6-1.3 1.7-2 3-2s2.4.7 3 2M14.5 10h3M14.5 13h3"/>',
  bell: '<path d="M6.5 16.5V11a5.5 5.5 0 0 1 11 0v5.5l1.5 1.5H5zM10 20.5a2 2 0 0 0 4 0"/>',
  db: '<ellipse cx="12" cy="6" rx="7" ry="2.5"/><path d="M5 6v12c0 1.4 3.1 2.5 7 2.5s7-1.1 7-2.5V6M5 12c0 1.4 3.1 2.5 7 2.5s7-1.1 7-2.5"/>',
  chev: '<path d="m9.5 6 6 6-6 6"/>',
  back: '<path d="m14.5 5-7 7 7 7"/>',
  dots: '<circle cx="6" cy="12" r="1.3"/><circle cx="12" cy="12" r="1.3"/><circle cx="18" cy="12" r="1.3"/>',
  scan: '<path d="M4 8V6a2 2 0 0 1 2-2h2M16 4h2a2 2 0 0 1 2 2v2M20 16v2a2 2 0 0 1-2 2h-2M8 20H6a2 2 0 0 1-2-2v-2"/><path d="m8.5 12 2.4 2.4 4.6-4.8"/>',
  x: '<path d="M6.5 6.5l11 11M17.5 6.5l-11 11"/>',
  pc: '<rect x="3" y="4.5" width="18" height="12" rx="2"/><path d="M8.5 20h7M12 16.5V20"/>',
  ph: '<rect x="7" y="2.5" width="10" height="19" rx="2.5"/><path d="M11 18.5h2"/>',
  inbox: '<path d="M4 13.5h4.5l1.5 2.5h4l1.5-2.5H20"/><path d="M5.5 6.5h13L20 13.5V18a1.5 1.5 0 0 1-1.5 1.5h-13A1.5 1.5 0 0 1 4 18v-4.5z"/><path d="M12 3v7M9.5 7.5 12 10l2.5-2.5"/>',
  mic: '<rect x="9" y="3.5" width="6" height="11" rx="3"/><path d="M5.5 11.5a6.5 6.5 0 0 0 13 0M12 18v2.5"/>',
  send: '<path d="M12 18.5v-13M6.5 11 12 5.5l5.5 5.5"/>',
  camera: '<path d="M4 8.5h3l1.8-2.5h6.4L17 8.5h3V19H4z"/><circle cx="12" cy="13.5" r="3.4"/>',
  plus: '<path d="M11.5 4.5h-5a2 2 0 0 0-2 2v11a2 2 0 0 0 2 2h11a2 2 0 0 0 2-2v-5"/><path d="M17.7 3.8a1.9 1.9 0 0 1 2.7 2.7l-7.6 7.6-3.4.7.7-3.4z"/>',
  history: '<path d="M4.2 12a7.8 7.8 0 1 0 2.3-5.5"/><path d="M4 4.6v3.6h3.6"/><path d="M12 8.2V12l2.7 1.7"/>',
  home: '<path d="M4 11.5 12 4l8 7.5"/><path d="M6.5 10.5V20h11v-9.5"/>'
}

export function iconSvg(nazwa: Ikona, grubosc = 1.7): string {
  return `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="${grubosc}" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${ICONS[nazwa] ?? ICONS.doc}</svg>`
}
