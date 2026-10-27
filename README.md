# mObywatel.ai: prototyp z lokalnym modelem Bielik

Prototyp aplikacji, w której zamiast menu i formularzy jest asystent AI: rozmawiasz z nim tekstem albo głosem,
a on sprawdza dane w (fikcyjnych) rejestrach i załatwia sprawy. Każdą czynność potwierdzasz na karcie.

Asystent działa **wyłącznie na modelu uruchomionym lokalnie** (polski Bielik przez Ollama). Projekt nie używa
płatnych API: nie ma tu wysyłania rozmów do OpenAI, Anthropic ani ElevenLabs, nie ma syntezy mowy z chmury
i nie ma automatycznego przełączania na płatnego dostawcę, gdy model lokalny zawiedzie.

**Ważne:** to prototyp z fikcyjnymi danymi (osoby, numery PESEL, dokumenty, pojazdy i płatności są zmyślone).
To nie jest usługa administracji publicznej ani aplikacja mObywatel, nie łączy się z żadnym rejestrem państwowym
i nie wolno w nim wpisywać prawdziwych danych osobowych. Teksty z kart usług gov.pl i biznes.gov.pl w katalogu
`serwer/wiedza/` to kopia publicznych stron z dnia ich pobrania, mogą być nieaktualne.

## Co jest w paczce

- `frontend/`: aplikacja w **Vue 3 + TypeScript + Tailwind CSS** (Vite), dwa wejścia: telefon (`index.html`)
  i strona „komputera” (`komputer.html`). Zbudowane pliki leżą w `frontend/dist`.
- `serwer/`: serwer HTTP w Pythonie (tylko biblioteka standardowa, bez `pip install`), pętla agenta, narzędzia,
  fikcyjne dane, znak mObywatela.
  - `serwer/bielik.py`: jedno miejsce konfiguracji modelu (dostawca, nazwa, okno kontekstu, próbkowanie, blokada innych modeli),
  - `serwer/i18n/`: słowniki interfejsu (15 języków poza polskim),
  - `serwer/wiedza/`: baza wiedzy z kart usług gov.pl (wyszukiwanie lokalne, bez sieci).
- `docs/SPRAWDZENIE.md`: lista miejsc w kodzie do sprawdzenia i kryteria testowania.
- `Dockerfile`, `docker-compose.yml`, `.env.example`.

## Wymagania

- Python 3.9 lub nowszy (Linux, macOS albo Windows), bez dodatkowych bibliotek.
- Node.js 20 lub nowszy, tylko jeśli chcesz przebudować frontend (`npm run build`). Zbudowana wersja jest w paczce.
- [Ollama](https://ollama.com) z modelem Bielik. Rozmowa działa bez internetu, ale pobranie modelu wymaga sieci.
- Przeglądarka. Głos korzysta z wbudowanych funkcji przeglądarki (mikrofon i mowa), więc działa tylko pod adresem
  `localhost`/`127.0.0.1` albo przez HTTPS.

### Sprzęt

| Model | Pobranie | RAM (szacunkowo) | Uwagi |
|---|---|---|---|
| `SpeakLeash/bielik-11b-v3.0-instruct:Q4_K_M` | 6,7 GB | 12 GB | domyślny, dobry kompromis |
| `SpeakLeash/bielik-11b-v3.0-instruct:Q8_0` | 12 GB | 20 GB | lepsza jakość |
| `SpeakLeash/bielik-minitron-7B-v3.0-instruct:Q4_K_M` | 4,4 GB | 8 GB | szybszy, słabszy w narzędziach |
| `SpeakLeash/bielik-4.5b-v3.0-instruct:Q8_0` | 4,8 GB | 6 GB | do testów interfejsu |

Karta graficzna nie jest wymagana, ale na samym procesorze 11B odpowiada kilka razy wolniej.
Przy 16 GB RAM zamknij inne aplikacje: model trzyma się w pamięci przez `MODEL_KEEP_ALIVE`.

## Uruchomienie lokalne

```bash
# 1. model (raz)
ollama pull SpeakLeash/bielik-11b-v3.0-instruct:Q4_K_M
ollama serve                       # jeśli nie działa już jako usługa w tle

# 2. konfiguracja
cp .env.example .env               # domyślnie: PROVIDER=ollama, MODEL=Bielik 11B v3.0 Q4_K_M

# 3. serwer — .env z katalogu głównego wczytuje się sam
python3 serwer/server.py
```

Otwórz http://127.0.0.1:8790/aplikacja (adres `/` też pokazuje aplikację, `/komputer` to strona wypożyczalni,
na której telefon przekazuje dane znakiem). Wersje językowe: `/de/aplikacja`, `/fr/aplikacja` itd.

Sprawdzenie, czy model odpowiada:

```bash
curl -s http://127.0.0.1:8790/api/health | python3 -m json.tool
```

`agent: true` i `modelGotowy: true` oznaczają gotowy model. Gdy modelu nie ma, `komunikat` mówi, co zrobić.

### Frontend: praca nad kodem

```bash
cd frontend
npm install
npm run dev          # http://127.0.0.1:5173, /api proxowane do serwera na porcie 8790
npm run build        # wynik w frontend/dist, serwowany przez python3 serwer/server.py
npm run typecheck
```

## Uruchomienie w Dockerze

```bash
cp .env.example .env
docker compose up --build
```

W Dockerze serwer modelu działa na Twoim komputerze, więc w `.env` ustaw `OLLAMA_URL=http://host.docker.internal:11434`
(`docker-compose.yml` dodaje wpis `host.docker.internal` także na Linuksie). Bez Compose:
`docker build -t mobywatel-ai . && docker run --rm --env-file .env --add-host=host.docker.internal:host-gateway -p 127.0.0.1:8790:8790 mobywatel-ai`.

## Ustawienia (zmienne środowiskowe)

| Zmienna | Domyślnie | Opis |
|---|---|---|
| `BIELIK_TYLKO` | `1` | `1` = inny model niż Bielik jest odrzucany (komunikat i błąd 503); `0` = dopuszczony z ostrzeżeniem |
| `PROVIDER` | `ollama` | `ollama` (natywne API Ollamy) albo `zgodny` (dowolne API zgodne z OpenAI) |
| `OLLAMA_URL` | `http://127.0.0.1:11434` | adres Ollamy |
| `MODEL` | `SpeakLeash/bielik-11b-v3.0-instruct:Q4_K_M` | model asystenta, pełna nazwa z tagiem |
| `MODEL_NUM_CTX` | `32768` | okno kontekstu; instrukcja + 66 narzędzi to ok. 14,6 tys. tokenów, więc mniejsze wartości uciskają historię |
| `MODEL_MAX_TOKENS` | `1200` | limit długości odpowiedzi |
| `MODEL_TEMPERATURE` | `0.1` | temperatura; niska stabilizuje wywoływanie narzędzi |
| `MODEL_TOP_P`, `MODEL_TOP_K`, `MODEL_MIN_P` | `0.95`, `40`, `0.05` | obcinanie ogona rozkładu przy próbkowaniu |
| `MODEL_REPEAT_PENALTY`, `MODEL_REPEAT_LAST_N` | `1.1`, `256` | kara powtórzeń: mniej zapętleń i obcych słów |
| `MODEL_SEED` | `-1` | `-1` = losowo; stała liczba = powtarzalne odpowiedzi w testach |
| `MODEL_TIMEOUT` | `180` | czas oczekiwania na odpowiedź (s) |
| `MODEL_KEEP_ALIVE` | `30m` | jak długo model zostaje w pamięci |
| `MODEL_WARMUP` | `1` | `1` = wczytaj model przy starcie serwera |
| `OPENAI_BASE_URL` | `OLLAMA_URL` + `/v1` | adres API przy `PROVIDER=zgodny` |
| `MODEL_API_KEY` | puste | klucz tylko wtedy, gdy lokalny serwer go wymaga |
| `HOST`, `PORT` | `127.0.0.1`, `8790` | adres i port serwera (w Dockerze `HOST=0.0.0.0`) |
| `AGENT_LOG` | `serwer/agent.log` | plik dziennika |
| `MOCKUP` | `frontend/dist` | katalog z plikami statycznymi |

Nazwy modeli i tagi zmieniają się u wydawcy: jeśli domyślny model nie jest dostępny, ustaw własny `MODEL`.
Lista pobranych modeli: `ollama list`.

Wszystkie ustawienia modelu czyta `serwer/bielik.py` — jedno miejsce na dostawcę, nazwę modelu, okno kontekstu,
próbkowanie i warianty. Podgląd i pobranie:

```bash
python3 serwer/bielik.py             # co jest ustawione, czy model jest pobrany
python3 serwer/bielik.py --pobierz   # ollama pull dla MODEL
```

### Tylko Bielik

Projekt obsługuje wyłącznie rodzinę Bielik (SpeakLeash): domyślnie `BIELIK_TYLKO=1`, więc inna nazwa w `MODEL`
kończy się czytelnym komunikatem w `/api/health` (`bielik: false`), ostrzeżeniem w interfejsie i błędem 503
na `/api/agent` — zamiast po cichu odpowiadać innym modelem. Dopuszczalne są wszystkie warianty Bielika
(11B Q4_K_M, Q8_0, minitron 7B, 4.5B); różnią się jakością wywoływania narzędzi.
`BIELIK_TYLKO=0` zdejmuje blokadę, zostawiając ostrzeżenie — przydaje się do porównań.

## Jak działa asystent

1. `frontend/src/lib/rozmowa.ts` wysyła historię rozmowy do `/api/agent`.
2. `serwer/agent.py` dokłada instrukcję systemową, kilkadziesiąt narzędzi i woła model
   (Ollama: `POST /api/chat` z `tools`, `num_ctx`, `keep_alive`).
3. Model wybiera narzędzie, serwer czyta dane z fikcyjnych rejestrów (`serwer/dane.py`) albo przygotowuje
   kartę potwierdzenia (`serwer/akcje.py`). Czynność wykonuje się dopiero po potwierdzeniu na karcie.
4. Karta trafia do przeglądarki jako zdarzenie (`card`, `confirm`, `chips`, `qrflow`), a frontend rysuje ją
   komponentem `DataCard.vue`.

Narzędzia wymagają modelu z obsługą wywoływania funkcji. Bielik 11B v3.0 ją ma; mniejsze warianty
(minitron, 4.5B) mogą wybierać narzędzia niestarannie. Opisy narzędzi zajmują kilkanaście tysięcy tokenów,
dlatego `MODEL_NUM_CTX` musi być odpowiednio duży: przy 16384 całe okno zjada instrukcja z narzędziami
i w historii zostaje jedno zdanie. Serwer liczy dostępne miejsce i przycina najstarsze tury (`przytnij()`
w `serwer/agent.py`), zamiast pozwolić Ollamie po cichu uciąć początek promptu. Całą konfiguracją modelu rządzi `serwer/bielik.py`
(parametry Ollamy: `temperature`, `top_p`, `top_k`, `min_p`, `repeat_penalty`, `num_ctx`, `num_predict`, `seed`).

## Bez kluczy API i bez płatnych usług: co się zmieniło

- **Modele**: usunięto OpenAI, Anthropic i Claude. Zostały dwa dostawcy lokalni: `ollama` (domyślnie) i `zgodny`
  (vLLM, llama.cpp, LM Studio — dowolne API w formacie OpenAI). Jedyne modele to warianty Bielika:
  `BIELIK_TYLKO=1` odrzuca każdy inny (503), a konfiguracja próbkowania jest dobrana pod Bielika 11B v3.0.
- **Głos**: nie ma `/api/stt` ani `/api/tts`, nie ma ElevenLabs. Rozpoznawanie mowy to Web Speech API
  (`SpeechRecognition`), a czytanie odpowiedzi to `speechSynthesis` — oba w przeglądarce, bez kluczy.
  Gdy przeglądarka nie ma rozpoznawania mowy, mikrofon jest nieaktywny, a rozmowa działa tekstem.
- **Tłumaczenie rozmowy**: nie ma tłumaczenia maszynowego. Asystent rozmawia po polsku, interfejs korzysta
  ze słowników w `serwer/i18n/`. Teksty, których w słowniku nie ma, zostają po polsku i trafiają do rejestru
  `serwer/i18n/_zrodla.json` (tworzony przy pierwszym braku). Etykiety kart, podpisy pól i nazwy dokumentów
  też przechodzą przez `t()`, więc `/de/aplikacja` pokazuje niemiecki interfejs; polskie zostają tylko dane
  z rejestrów i zdania wygenerowane przez model.
- **Tryb skryptowy**: usunięty. Wcześniej brak klucza oznaczał gotowe scenariusze; teraz aplikacja ma jedną
  ścieżkę (agent na lokalnym modelu), a przy niedostępnym modelu pokazuje komunikat i nie udaje odpowiedzi.
- **Błędy**: brak sieci, brak modelu, przekroczony czas, zły model — każde z nich kończy się komunikatem
  po polsku i kodem 503. Serwer nigdy nie przełącza się na inną (płatną) usługę.
- **Prywatność**: rozmowa nie opuszcza Twojego komputera. Diagnostyka nagrań (`/api/glos`) została usunięta.

## Co sprawdzić w kodzie i jak testować

Pełna lista miejsc do przeglądu i kryteria testów: [`docs/SPRAWDZENIE.md`](docs/SPRAWDZENIE.md).

## Bezpieczeństwo i prywatność

- Serwer nie ma logowania ani limitów. Każdy, kto dostanie się do jego adresu, korzysta z Twojego modelu.
  Domyślnie słucha tylko na `127.0.0.1`, a `docker-compose.yml` wystawia port tylko lokalnie.
  Nie wystawiaj go do internetu bez własnej ochrony.
- Serwer zapisuje dziennik (`serwer/agent.log`): wiadomości wpisane do asystenta, użyte narzędzia i czasy odpowiedzi.
- Rozpoznawanie mowy w przeglądarce może korzystać z usługi dostawcy przeglądarki (tak działa Chrome).
  Jeśli to nieakceptowalne, korzystaj z tekstu albo z przeglądarki z lokalnym rozpoznawaniem mowy.

## Licencja

Kod prototypu (pliki `.py`, `.ts`, `.vue`, `.html`, `.css`, słowniki interfejsu i pliki konfiguracyjne) jest
udostępniony na licencji MIT. Pełny tekst jest w pliku `LICENSE`. Możesz go używać, zmieniać i rozpowszechniać,
także komercyjnie, pod warunkiem zachowania informacji o autorze i treści licencji.

Licencja MIT nie obejmuje:
- godła Rzeczypospolitej Polskiej, nazwy, logo i oznaczeń mObywatela ani wyglądu dokumentów
  (m.in. `frontend/public/assets/icon-mobywatel.svg`, `logo-mobywatel*`, `card-*`, `strip-*`, `mdowod-ekran.png`).
  Są w prototypie wyłącznie w celach pokazowych, a ich użycie podlega odrębnym przepisom i prawom ich właścicieli;
- zdjęć osób z pokazu (`frontend/public/assets/foto-*.jpg`);
- opisów usług w `serwer/wiedza/`, które pochodzą z serwisu gov.pl. Przy ich ponownym wykorzystaniu sprawdź
  warunki podane na gov.pl;
- wag modelu Bielik, które pobierasz z Ollamy na warunkach wydawcy (SpeakLeash, licencja Apache 2.0).

Osoby i dane w prototypie są fikcyjne. Projekt nie jest usługą administracji publicznej ani oficjalną aplikacją mObywatel.
