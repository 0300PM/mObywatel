export function qrSvg(ziarno = 7): string {
  let s = ziarno
  const los = (): number => (s = (s * 9301 + 49297) % 233280) / 233280
  const n = 25
  let p = ''
  const naroznik = (x: number, y: number): string =>
    `<rect x="${x}" y="${y}" width="6" height="6" fill="none" stroke="currentColor" stroke-width="1"/><rect x="${x + 1.5}" y="${y + 1.5}" width="3" height="3"/>`
  for (let y = 0; y < n; y++) {
    for (let x = 0; x < n; x++) {
      if ((x < 8 && y < 8) || (x > 16 && y < 8) || (x < 8 && y > 16)) continue
      if (los() > 0.52) p += `<rect x="${x}" y="${y}" width="1" height="1"/>`
    }
  }
  return `<svg viewBox="-1 -1 27 27" fill="currentColor" shape-rendering="crispEdges" aria-hidden="true">${p}${naroznik(0.5, 0.5)}${naroznik(18.5, 0.5)}${naroznik(0.5, 18.5)}</svg>`
}
