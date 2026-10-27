# mObywatel.ai: prototyp z darmowymi modelami Cloudflare Workers AI

Prototyp aplikacji, w której zamiast menu i formularzy jest asystent AI: rozmawiasz z nim tekstem albo głosem,
a on sprawdza dane w (fikcyjnych) rejestrach i załatwia sprawy. Każdą czynność potwierdzasz na karcie.

Asystent rozmawia z modelem **przez Cloudflare Workers AI i token z pliku `.env`** — model nie działa na Twoim
komputerze. Dozwolone są **wyłącznie darmowe modele otwarte z katalogu Workers AI** (lista w `serwer/katalog.py`),
mieszczące się w dziennym limicie planu Free (10 000 neuronów). Nie ma tu OpenAI, Anthropic, ElevenLabs,
syntezy mowy z chmury ani cichego przełączania na płatnego dostawcę. Wnioskowanie idzie z serwera na Twój token,
a nie z przeglądarki, i token nigdy nie trafia do klienta.

**Ważne:** to prototyp z fikcyjnymi danymi (osoby, numery PESEL, dokumenty, pojazdy i płatności są zmyślone).
To nie jest usługa administracji publicznej ani aplikacja mObywatel, nie łączy się z żadnym rejestrem państwowym
i nie wolno w nim wpisywać prawdziwych danych osobowych. Teksty z kart usług gov.pl i biznes.gov.pl w katalogu
`serwer/wiedza/` to kopia publicznych stron z dnia ich pobrania, mogą być nieaktualne.

## Co jest w paczce

- `frontend/`: aplikacja w **Vue 3 + TypeScript + Tailwind CSS** (Vite), dwa wejścia: telefon (`index.html`)
  i strona „komputera” (`komputer.html`). Zbudowane pliki leżą w `frontend/dist`.
- `serwer/`: serwer HTTP w Pythonie (tylko biblioteka standardowa, bez `pip install`), pętla agenta, narzędzia,
  fikcyjne dane, znak mObywatela.
  - `serwer/katalog.py`: zamknięty katalog darmowych modeli Workers AI (z prędkością i oknem kontekstu),
  - `serwer/model.py`: jedno miejsce konfiguracji modelu (konto, token, adres API, nazwa, okno, próbkowanie),
  - `serwer/ustawienia.py`: wczytywanie `.env` (obsługuje `export`, BOM, CRLF, komentarze i cudzysłowy),
  - `serwer/i18n/`: słowniki interfejsu (15 języków poza polskim),
  - `serwer/wiedza/`: baza wiedzy z kart usług gov.pl (wyszukiwanie lokalne, bez sieci).
- `testy/`: testy katalogu, konfiguracji Cloudflare, parsera `.env` i całego serwera na atrapie
  (`python3 -m unittest discover testy -v`, 40 testów, bez sieci).
- `docs/SPRAWDZENIE.md`: lista miejsc w kodzie do sprawdzenia i kryteria testowania.
- `Dockerfile`, `docker-compose.yml`, `.env.example`.

## Wymagania

- Konto Cloudflare (darmowe) i **Account ID** — `dash.cloudflare.com` → *Workers & Pages* → *Account ID*.
- **API token** z uprawnieniem Workers AI: `dash.cloudflare.com` → *My Profile* → *API Tokens* →
  *Create Token* → template **Workers AI**. Bez tokenu lub konta serwer odpowiada 503 z instrukcją, czego brakuje.
- Python 3.9 lub nowszy (Linux, macOS albo Windows), bez dodatkowych bibliotek.
- Node.js 20 lub nowszy, tylko jeśli chcesz przebudować frontend (`npm run build`). Zbudowana wersja jest w paczce.
- Przeglądarka. Głos korzysta z wbudowanych funkcji przeglądarki (mikrofon i mowa), więc działa tylko pod adresem
  `localhost`/`127.0.0.1` albo przez HTTPS.

### Modele

Katalog jest zamknięty i leży w `serwer/katalog.py` — model spoza niego jest odrzucany, zanim żądanie poleci
do Cloudflare. Wszystkie wpisy to darmowe modele otwarte z wywoływaniem narzędzi.

| Model | Prędkość | Okno | Uwagi |
|---|---|---|---|
| `@cf/ibm-granite/granite-4.0-h-micro` | 420 tok/s | 131k | najmniejszy, najtańszy w neuronach |
| `@cf/swiss-ai/apertus-v1.5-8b` | 380 tok/s | 262k | szybki model otwarty |
| `@cf/utter-project/eurollm-9b-it` | 340 tok/s | 32k | europejski, wielojęzyczny (polski) |
| `@cf/openai/gpt-oss-20b` | 300 tok/s | 131k | mocny w narzędziach, rozsądny koszt |
| `@cf/qwen/qwen3-30b-a3b-fp8` | 260 tok/s | 33k | MoE, dobra polszczyzna |
| `@cf/meta/llama-4-scout-17b-16e-instruct` | 240 tok/s | 131k | MoE, duże okno |
| `@cf/zai-org/glm-4.7-flash` | 210 tok/s | 131k | szybki model rozmowny |
| `@cf/mistralai/mistral-small-3.1-24b-instruct` | 190 tok/s | 131k | szybki model ogólny |
| `@cf/google/gemma-4-26b-a4b-it` | 180 tok/s | 262k | MoE, dobre instrukcje |
| `@cf/openai/gpt-oss-120b` | 150 tok/s | 131k | najlepsze narzędzia, szybciej zużywa limit |
| `@cf/nvidia/nemotron-3-120b-a12b` | 120 tok/s | 262k | wyższa jakość |
| `@cf/moonshotai/kimi-k2.6` | 100 tok/s | 262k | najwyższa jakość, najdroższy w neuronach |

Pełna lista z opisami: `python3 serwer/katalog.py`. Podgląd konfiguracji: `python3 serwer/model.py`,
a podgląd tego, co wybrał serwer i co widzi na koncie: `curl -s http://127.0.0.1:8790/api/modele`.

`MODEL=auto` (domyślnie) bierze **najszybszy** model z katalogu, który Cloudflare widzi na Twoim koncie
i który uniesie instrukcję systemową i 66 narzędzi. `MODEL_PREFERUJ=jakosc` preferuje modele mocne
(gpt-oss-120b, nemotron, kimi), a `szybkosc` działa jak `auto`.

### Dzienny limit i koszt

Darmowy plan Cloudflare to **10 000 neuronów dziennie**, liczone od północy UTC i wspólne dla wszystkich modeli.
Neurony rosną z rozmiarem modelu i długością promptu, a nasz prompt jest duży: instrukcja systemowa i opisy
66 narzędzi to około 14,6 tys. tokenów. Dlatego:

- zaczynaj od najmniejszych modeli z góry tabeli (`granite-4.0-h-micro`, `apertus-8b`, `eurollm-9b`),
- `MODEL_MAX_TOKENS=1200` ogranicza koszt jednej odpowiedzi; nie zwiększaj go bez potrzeby,
- przy wyczerpaniu limitu `/api/agent` zwraca 503 z komunikatem o neuronach (Cloudflare odpowiada wtedy 429),
- modele płatne (spoza katalogu) nie są używane nawet wtedy, gdy limit się skończy.

### Dlaczego nie ma Bielika

W katalogu Workers AI (73 aktywne modele, sprawdzone 27 października 2026) **nie ma modeli SpeakLeash**.
Cloudflare wycofał wcześniejszą wersję Bielika, a jedyna droga do niego prowadzi przez AI Gateway do zewnętrznego
dostawcy, czyli poza darmowy plan. Projekt ma więc jeden warunek: zero płatnych modeli. Gdy Cloudflare doda Bielika,
wystarczy dopisać jedną linię w `serwer/katalog.py`:

```python
Model('@cf/speakleash/bielik-11b-v3.0-instruct', 45, 32768,
      'Bielik 11B v3.0, polski model SpeakLeash', bielik=True),
```

Flaga `bielik` jest już obsługiwana w katalogu, w `/api/modele` i w `/api/health`, więc nic więcej nie trzeba zmieniać.

## Uruchomienie lokalne

```bash
# 1. konfiguracja
cp .env.example .env               # domyślnie: MODEL=auto, resztę zostaw
$EDITOR .env                       # wpisz CLOUDFLARE_ACCOUNT_ID i CLOUDFLARE_API_TOKEN

# 2. serwer — .env z katalogu głównego wczytuje się sam
python3 serwer/server.py
```

Otwórz http://127.0.0.1:8790/aplikacja (adres `/` też pokazuje aplikację, `/komputer` to strona wypożyczalni,
na której telefon przekazuje dane znakiem). Wersje językowe: `/de/aplikacja`, `/fr/aplikacja` itd.

Sprawdzenie, czy model odpowiada:

```bash
curl -s http://127.0.0.1:8790/api/health | python3 -m json.tool
```

`agent: true` i `modelGotowy: true` oznaczają gotowy model; `konto` i `klucz` mówią, czy konfiguracja jest kompletna,
a `komunikat` podpowiada, co poprawić. Gdy nie da się pobrać listy modeli konta (np. token nie ma uprawnień
do jej czytania), serwer i tak odpowiada, wybierając model z katalogu.

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
cp .env.example .env               # wpisz CLOUDFLARE_ACCOUNT_ID i CLOUDFLARE_API_TOKEN
docker compose up --build
```

W kontenerze nie trzeba nic instalować poza Dockerem: model działa w Cloudflare, a konto i token biorą się z `.env`.
Bez Compose:

```bash
docker build -t mobywatel-ai .
docker run --rm --env-file .env -p 127.0.0.1:8790:8790 mobywatel-ai
```

**Po każdej zmianie `.env` użyj `docker compose up -d --force-recreate`.** Zwykłe `restart` (i przycisk
w Docker Desktop) nie czyta pliku ponownie — kontener zachowuje zmienne z momentu utworzenia.

### Gdy serwer nie widzi konta albo tokenu

1. `curl -s localhost:8790/api/health` — pole `config` mówi, który plik `.env` został wczytany
   (albo że żaden), a `ostrzezenia` pokazuje podejrzane wartości, np. Account ID, który nie ma 32 znaków.
2. `docker compose exec mobywatel printenv | grep CLOUDFLARE` — co faktycznie dostał kontener.
3. `python3 serwer/model.py` — raport z maskowanym kontem, maską tokenu i powodem, dla którego lista
   modeli się nie pobrała.

Typowe przyczyny: `restart` zamiast `--force-recreate`, `.env` w innym katalogu niż `docker-compose.yml`,
Global API Key wklejony zamiast tokenu (Cloudflare odpowiada wtedy 401), token bez uprawnienia
*Workers AI: Read*, albo podmienione miejscami Account ID i token.

### Frontend deweloperski bez serwera API

`npm run dev` proxuje `/api` na `http://127.0.0.1:8790` (zmienisz przez `API_TARGET`). Gdy backend nie
działa, przeglądarka dostaje czytelne **503** z wyjaśnieniem zamiast `socket hang up`.

## Ustawienia (zmienne środowiskowe)

| Zmienna | Domyślnie | Opis |
|---|---|---|
| `CLOUDFLARE_ACCOUNT_ID` | puste | identyfikator konta Cloudflare; wymagany |
| `CLOUDFLARE_API_TOKEN` | puste | token z uprawnieniem Workers AI; wymagany, zostaje na serwerze |
| `MODEL` | `auto` | `auto` = najszybszy model z katalogu, inaczej pełna nazwa `@cf/...` z katalogu |
| `MODEL_PREFERUJ` | `auto` | `auto` i `szybkosc` = najszybszy, `jakosc` = najpierw modele mocne |
| `MODELE_DOWOLNE` | `0` | `1` = dopuść nazwy spoza katalogu (odradzane: modele bez narzędzi albo spoza planu Free) |
| `MODEL_NUM_CTX` | `32768` | okno kontekstu; instrukcja + 66 narzędzi to ok. 14,6 tys. tokenów, więc mniejsze wartości uciskają historię |
| `MODEL_MAX_TOKENS` | `1200` | limit długości odpowiedzi (i kosztu w neuronach) |
| `MODEL_TEMPERATURE`, `MODEL_TOP_P` | `0.1`, `0.95` | próbkowanie; niska temperatura stabilizuje wywoływanie narzędzi |
| `MODEL_SEED` | `-1` | `-1` = losowo; stała liczba = powtarzalne odpowiedzi w testach |
| `MODEL_TIMEOUT` | `180` | czas oczekiwania na odpowiedź (s) |
| `CLOUDFLARE_AI_BASE` | adres z `ACCOUNT_ID` | nadpisanie adresu API (testy, AI Gateway) |
| `HOST`, `PORT` | `127.0.0.1`, `8790` | adres i port serwera (w Dockerze `HOST=0.0.0.0`) |
| `AGENT_LOG` | `serwer/agent.log` | plik dziennika |
| `MOCKUP` | `frontend/dist` | katalog z plikami statycznymi |

Cloudflare nie udostępnia `GET /v1/models` na tym API, więc serwer sprawdza listę modeli osobnym zapytaniem do API
konta (`/accounts/{id}/ai/models/search`) i trzyma ją minutę w pamięci. Wszystkie ustawienia modelu czyta
`serwer/model.py` — jedno miejsce na konto, token, nazwę modelu, okno kontekstu i próbkowanie:

```bash
python3 serwer/katalog.py            # katalog darmowych modeli z prędkościami
python3 serwer/model.py              # co jest ustawione i co widzi konto Cloudflare
```

### Tylko dozwolone modele

Katalog `serwer/katalog.py` jest zamknięty: darmowe modele Workers AI z wywoływaniem narzędzi. Nazwa spoza katalogu
(np. `gpt-4o` albo wycofany `@cf/meta/llama-2-7b-chat-int8`) kończy się czytelnym komunikatem w `/api/health`,
ostrzeżeniem w interfejsie i błędem 503 na `/api/agent` — zamiast po cichu odpowiadać modelem, za który trzeba płacić.
`MODELE_DOWOLNE=1` zdejmuje blokadę — przydaje się do porównań.

## Jak działa asystent

1. `frontend/src/lib/rozmowa.ts` wysyła historię rozmowy do `/api/agent`.
2. `serwer/agent.py` dokłada instrukcję systemową, 66 narzędzi i woła
   `POST https://api.cloudflare.com/client/v4/accounts/{id}/ai/v1/chat/completions` z `Authorization: Bearer`.
3. Model wybiera narzędzie, serwer czyta dane z fikcyjnych rejestrów (`serwer/dane.py`) albo przygotowuje
   kartę potwierdzenia (`serwer/akcje.py`). Czynność wykonuje się dopiero po potwierdzeniu na karcie.
4. Karta trafia do przeglądarki jako zdarzenie (`card`, `confirm`, `chips`, `qrflow`), a frontend rysuje ją
   komponentem `DataCard.vue`.

Narzędzia wymagają modelu z obsługą wywoływania funkcji, dlatego katalog zawiera wyłącznie takie modele.
Opisy narzędzi zajmują kilkanaście tysięcy tokenów, więc `MODEL_NUM_CTX` musi być odpowiednio duży: przy 16384
całe okno zjada instrukcja z narzędziami i w historii zostaje jedno zdanie. Serwer liczy dostępne miejsce i przycina
najstarsze tury (`przytnij()` w `serwer/agent.py`), zamiast pozwolić dostawcy po cichu uciąć początek promptu.
Całą konfiguracją modelu rządzi `serwer/model.py` (`temperature`, `top_p`, `max_tokens`, `MODEL_NUM_CTX`).

## Bez płatnych usług: co się zmieniło

- **Modele**: nie ma OpenAI, Anthropic ani Claude, nie ma lokalnej Ollamy ani innych dostawców. Rozmowę prowadzi
  darmowy model otwarty z katalogu `serwer/katalog.py`, wywołany przez Cloudflare Workers AI tokenem z `.env`.
  Nazwa spoza katalogu jest odrzucana (503), zanim żądanie wyjdzie na zewnątrz.
- **Głos**: nie ma `/api/stt` ani `/api/tts`, nie ma ElevenLabs. Rozpoznawanie mowy to Web Speech API
  (`SpeechRecognition`), a czytanie odpowiedzi to `speechSynthesis` — oba w przeglądarce, bez tokenów.
  Gdy przeglądarka nie ma rozpoznawania mowy, mikrofon jest nieaktywny, a rozmowa działa tekstem.
- **Tłumaczenie rozmowy**: nie ma tłumaczenia maszynowego. Asystent rozmawia po polsku, interfejs korzysta
  ze słowników w `serwer/i18n/`. Teksty, których w słowniku nie ma, zostają po polsku i trafiają do rejestru
  `serwer/i18n/_zrodla.json` (tworzony przy pierwszym braku). Etykiety kart, podpisy pól i nazwy dokumentów
  też przechodzą przez `t()`, więc `/de/aplikacja` pokazuje niemiecki interfejs; polskie zostają tylko dane
  z rejestrów i zdania wygenerowane przez model.
- **Tryb skryptowy**: usunięty. Aplikacja ma jedną ścieżkę (agent na modelu z Cloudflare), a przy niedostępnym
  modelu pokazuje komunikat i nie udaje odpowiedzi.
- **Błędy**: brak konta, brak tokenu, token odrzucony, model niedostępny, wyczerpany dzienny limit neuronów,
  przekroczony czas — każde z nich kończy się komunikatem po polsku i kodem 503. Serwer nigdy nie przełącza się
  na inną (płatną) usługę.
- **Prywatność**: treść rozmowy trafia do Cloudflare — token zostaje na serwerze, przeglądarka go nie widzi.
  Diagnostyka nagrań (`/api/glos`) została usunięta.

## Co sprawdzić w kodzie i jak testować

Pełna lista miejsc do przeglądu i kryteria testów: [`docs/SPRAWDZENIE.md`](docs/SPRAWDZENIE.md).

## Bezpieczeństwo i prywatność

- Serwer nie ma logowania ani limitów. Każdy, kto dostanie się do jego adresu, korzysta z Twojego modelu
  i Twojego tokenu Cloudflare — dlatego domyślnie słucha tylko na `127.0.0.1`, a `docker-compose.yml`
  wystawia port tylko lokalnie. Nie wystawiaj go do internetu bez własnej ochrony.
- Serwer zapisuje dziennik (`serwer/agent.log`): wiadomości wpisane do asystenta, użyte narzędzia i czasy odpowiedzi.
- Rozpoznawanie mowy w przeglądarce może korzystać z usługi dostawcy przeglądarki (tak działa Chrome).
  Jeśli to nieakceptowalne, korzystaj z tekstu albo z przeglądarki z lokalnym rozpoznawaniem mowy.

## Licencja

Kod prototypu (pliki `.py`, `.ts`, `.vue`, `.html`, `.css`, słowniki interfejsu i pliki konfiguracyjne) jest
udostępniony na licencji MIT. Pełny tekst jest w pliku `LICENSE`. Możesz go używać, zmieniać i rozpowszechniać,
także komercyjnie, pod warunkiem zachowania informacji o autorze i treści licencji.

Licencja MIT nie obejmuje:
- godła Rzeczypospolitej Polskiej, nazwy, logo i oznaczeń mObywatela ani wyglądu dokumentów
  (m.in. `frontend/public/assets/icon-mobywatel.svg`, `logo-mobywatel*`, `card-*`, `strip-*`).
  Są w prototypie wyłącznie w celach pokazowych, a ich użycie podlega odrębnym przepisom i prawom ich właścicieli;
- zdjęć osób z pokazu (`frontend/public/assets/foto-*.jpg`);
- opisów usług w `serwer/wiedza/`, które pochodzą z serwisu gov.pl. Przy ich ponownym wykorzystaniu sprawdź
  warunki podane na gov.pl;
- wag modeli otwartych uruchamianych w Cloudflare Workers AI, które podlegają warunkom ich wydawców.

Osoby i dane w prototypie są fikcyjne. Projekt nie jest usługą administracji publicznej ani oficjalną aplikacją mObywatel.
