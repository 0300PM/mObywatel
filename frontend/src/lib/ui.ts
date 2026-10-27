import { ref } from 'vue'

export const daneWidoczne = ref(false)
export const godzina = ref('')
export const godzinaSekundy = ref('')

function odswiez(): void {
  const teraz = new Date()
  godzina.value = teraz.toLocaleTimeString('pl-PL', { hour: '2-digit', minute: '2-digit' })
  godzinaSekundy.value = teraz.toLocaleTimeString('pl-PL', { hour: '2-digit', minute: '2-digit', second: '2-digit' })
}

odswiez()
setInterval(odswiez, 1000)

document.addEventListener('visibilitychange', () => {
  if (document.visibilityState === 'hidden') daneWidoczne.value = false
})

export function pokazDane(): void {
  daneWidoczne.value = true
}
