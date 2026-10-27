# Co sprawdzić w kodzie i jak testować

Dokument dla osoby, która przejmuje prototyp. Sekcja 1 to lista miejsc w kodzie, które warto przeczytać
przy zmianie modelu, dostawcy albo interfejsu. Sekcja 2 to kryteria testowania: scenariusze, oczekiwane wyniki,
budżety czasu i lista rzeczy, które muszą pozostać prawdą po każdej zmianie.

## 1. Miejsca w kodzie do sprawdzenia

### 1.1 Model i dostawcy API

| Plik | Miejsce | Co sprawdzić |
|---|---|---|
| `serwer/bielik.py` | całość | jedno źródło konfiguracji: `PROVIDER`, `MODEL`, `NUM_CTX`, `OPCJE` (temperatura, top_p, top_k, min_p, kara powtórzeń), `KEEP_ALIVE`, `TYLKO_BIELIK`; `czy_bielik()` i `wymagaj_bielika()` pilnują, żeby modelem był wyłącznie Bielik |
| `serwer/agent.py` | `PROVIDER`, `MODEL`, `MODEL_NUM_CTX`, `MODEL_KEEP_ALIVE` | wartości pochodzą z `serwer/bielik.py` (nie czytać `os.environ` w drugim miejscu); `NUM_CTX` nie może być mniejsze niż liczba tokenów instrukcji systemowej i definicji narzędzi (dziś ok. 12–15 tys.) |
| `serwer/agent.py` | `llm()` | na wejściu `bielik.wymagaj_bielika()`: przy `BIELIK_TYLKO=1` inny model kończy się `BladAPI` (503), nie cichą odpowiedzią; dalej `przytnij()` przycina historię do okna kontekstu |
| `serwer/agent.py` | `zajete_tokeny()`, `przytnij()` | budżet = `NUM_CTX − MAX_TOKENS − 512 − (instrukcja + narzędzia)`; przycięcie nigdy nie zaczyna się od `tool_result` ani od odpowiedzi asystenta, bo to psuje format dla modelu |
| `serwer/agent.py` | `napraw_wyciek()` | oprócz `to=functions.x {…}` łapie też czysty JSON `{"name": …, "arguments": {…}}`, którym Bielik odpowiada według modelfile dla narzędzi |
| `serwer/agent.py` | `ollama()` | treść żądania `POST /api/chat`: `tools`, całe `options` z `bielik.OPCJE` (`num_ctx`, `num_predict`, `temperature`, `top_p`, `top_k`, `min_p`, `repeat_penalty`, `repeat_last_n`, `seed`), `keep_alive`; wycięcie `<think>…</think>` (`_tekst_z_odpowiedzi`); branie tylko pierwszego `tool_call` (`_wywolania`) |
| `serwer/agent.py` | `zgodny()` | ten sam kontrakt dla API w formacie OpenAI; obsługa serwera, który nie zna `parallel_tool_calls`; `MODEL_API_KEY` tylko gdy wymagany |
| `serwer/agent.py` | `_podlacz()`, `_blad_modelu()` | czy każdy błąd HTTP i sieci zamienia się na komunikat po polsku i `BladAPI`; **nie może** tu być żadnego drugiego dostawcy jako zapasowego |
| `serwer/agent.py` | `stan_modelu()`, `rozgrzej()` | cache 5 s (żeby `/api/health` był szybki), porównanie nazwy modelu z `ollama list`, flaga `bielik` w odpowiedzi, wczytywanie modelu przy starcie bez blokowania serwera |
| `serwer/agent.py` | `system_prompt()`, `SYSTEM` | instrukcje nadal mówią o narzędziach, potwierdzaniu kartą i trybie głosowym; po zmianie modelu sprawdź, czy nie ma zdań opisujących zachowanie dawnych modeli |
| `serwer/narzedzia.py` | `ODCZYTY`, `AKCJE`, `UI`, `KLIENT` | liczba i rozmiar opisów narzędzi: każde nowe narzędzie zwiększa kontekst i pogarsza wybór u mniejszych modeli |
| `serwer/server.py` | `zdrowie()`, `agent()` | `/api/health` pokazuje `agent`, `modelGotowy`, `bielik`, `komunikat`; `/api/agent` zwraca 503 z `error`, a nie 200 z pustą odpowiedzią |
| `serwer/server.py` | `start()` | na starcie wypisuje `bielik.opis()` (model, dostawca, kontekst, próbkowanie, czy pobrany) |
| `.env.example` | całość | czy każda zmienna z kodu ma tu opis i sensowną wartość domyślną |

### 1.2 Brak płatnych usług (kontrola regresji)

Przed wydaniem dowolnej wersji:

```bash
grep -rniE "openai|anthropic|elevenlabs|api\.openai|api\.anthropic" serwer frontend/src
```

Dozwolone trafienia: `OPENAI_BASE_URL` i `TOOLS_OPENAI` (format API, nie usługa) oraz teksty w dokumentacji.
Każde inne trafienie oznacza wyciek płatnej zależności.

| Plik | Miejsce | Co sprawdzić |
|---|---|---|
| `serwer/tlumacz.py` | całość | zostały tylko słowniki i rejestr braków; brak wywołań HTTP |
| `serwer/server.py` | `do_POST` | nie ma `/api/stt`, `/api/tts`, `/api/glos`; `Cache-Control: no-store` tylko dla `/api/` |
| `frontend/src/lib/speech.ts` | całość | wyłącznie `SpeechRecognition` i `speechSynthesis`; brak `fetch` do serwera mowy |
| `frontend/src/lib/rozmowa.ts` | `zapytajAgent()` | po błędzie jest komunikat i koniec; brak ponowień na innym dostawcy |

### 1.3 Głos w przeglądarce

| Plik | Miejsce | Co sprawdzić |
|---|---|---|
| `frontend/src/lib/speech.ts` | `nasluchuj()` | `onend` zawsze kończy obietnicę (brak „wiszącego” mikrofonu), limit czasu 12 s, rozpoznanie błędu `not-allowed` jako brak mikrofonu |
| `frontend/src/lib/speech.ts` | `czytaj()`, `przerwijCzytanie()` | wybór głosu dla języka, `mowi` wraca do `false` także przy błędzie |
| `frontend/src/lib/rozmowa.ts` | `petlaGlosowa()`, `wznowGlos()`, `dotknijMikrofonu()` | brak dwóch pętli naraz, pauza przy karcie potwierdzenia i przy skanerze, powrót do słuchania po odpowiedzi |
| `frontend/src/lib/rozmowa.ts` | `wypowiedz()` | mikrofon zatrzymany przed czytaniem (asystent nie odpowiada sam sobie) |
| `frontend/src/components/VoiceOverlay.vue` | całość | stany `idle/listen/stt/think/speak/wait` mają tekst dla użytkownika; wyjście z trybu głosowego czyści scenę |

### 1.4 Frontend (Vue + TypeScript + Tailwind)

| Plik | Miejsce | Co sprawdzić |
|---|---|---|
| `frontend/src/lib/rozmowa.ts` | `dodaj()`, `zablokujStare()` | historia rośnie liniowo; stare karty tracą przyciski i opcje, więc nie da się potwierdzić czynności z poprzedniej tury |
| `frontend/src/lib/rozmowa.ts` | `trwa`, `potwierdzenieWToku` | licznik żądań w toku wraca do zera także po błędzie (`finally`) |
| `frontend/src/components/ChatPanel.vue` | `watch` na długości listy | przewijanie na dół tylko przy nowej wiadomości, nie przy każdym renderze |
| `frontend/src/components/DocumentSheet.vue` | szablon | arkusz rysuje kartę komponentem `DocumentFace`, bez wklejonego zrzutu ekranu (`mdowod-ekran.png` usunięty), więc nie ma „ekranu w ekranie”, a cztery akcje mieszczą się nad zgięciem |
| `frontend/src/components/Wallet.vue` | karty dokumentów | karty to `div role="button"` z obsługą Enter i spacji, a nie `<button>` w `<button>` — wewnętrzne przyciski karty (znak, „Pokaż dane”) działają bez otwierania arkusza |
| `frontend/src/components/Composer.vue` | mikrofon | przycisk nigdy nie jest `disabled`; bez rozpoznawania mowy pokazuje podpowiedź (`App.vue`, `podpowiedzGlosu`), więc każde kliknięcie coś robi |
| `frontend/src/App.vue` | `ekran-aplikacji`, `ramka-telefonu` | powłoka centruje ramkę telefonu (`display:flex`, `align-items:center`, `justify-content:center`, `min-height:100dvh`); ramka ma `flex:none` i `max-height: calc(100dvh - 48px)`, a poniżej 520 px zajmuje cały ekran bez paddingu |
| `frontend/src/components/Wallet.vue` | `sledzPrzewijanie()` | jedno źródło prawdy dla aktywnej karty w karuzeli i karuzeli pionowej; brak `setInterval` |
| `frontend/src/lib/sylwetki.ts` | `svg()` | identyfikatory gradientów są unikalne (`uid`), inaczej dwie sylwetki na ekranie kradną sobie kolory |
| `frontend/src/lib/znak.ts` | `odkodujZnak()` | dekoder nie alokuje w pętli 90 ms więcej niż potrzebne; `plansza` jest poza pętlą |
| `frontend/src/App.vue` | `onMounted`, `onBeforeUnmount` | timery i nasłuchy są zwalniane (zegar tokenu, `keydown`, mikrofon) |
| wszystkie komponenty | szablony | brak `v-html` z danymi użytkownika (tylko treści z serwera i własne ikony) |
| `frontend/tailwind` | klasy | brak własnych reguł w stylach inline poza dynamicznymi wartościami (`backgroundImage`, offsety) |

### 1.5 Dane, akcje i bezpieczeństwo

| Plik | Miejsce | Co sprawdzić |
|---|---|---|
| `serwer/dane.py` | `READ`, `stan_poczatkowy()` | odczyty nie zmieniają stanu; wszystko jest fikcyjne |
| `serwer/akcje.py` | `A`, `podglad` i `wykonaj` | `podglad` nic nie zmienia, `wykonaj` wymaga potwierdzenia z `confirm` (droga przez `agent._run`) |
| `serwer/agent.py` | `_run()` — gałąź `confirm` | potwierdzenie dotyczy wyłącznie `tool_use` o podanym `id` z historii; nie da się wykonać akcji bez karty |
| `serwer/agent.py` | `napraw()`, `napraw_wyciek()` | każde `tool_use` ma `tool_result`; wyciek `functions.x {…}` w tekście staje się wywołaniem |
| `serwer/server.py` | `wczytaj_env`, `do_GET`, `do_POST` | `.env` z katalogu głównego czytany przy starcie (bez nadpisywania zmiennych środowiska), limity rozmiaru ciała (`/api/znak/przekaz` 20 kB, `/api/i18n/brak` 60 kB), brak podglądu plików spoza `ROOT` |
| `serwer/server.py` | `ZN`, `zn_kto()` | żetony wygasają (`ZN_TTL`, `ZN_SWIEZY`), nie można odebrać danych samemu sobie |

## 2. Kryteria testowania

### 2.1 Środowisko i model

1. `ollama list` pokazuje model z `.env` (`MODEL`). Kryterium: `curl -s localhost:8790/api/health` zwraca
   `"agent": true`, `"modelGotowy": true`, `"komunikat": ""`.
2. Zatrzymaj Ollamę (`pkill ollama`). Kryterium: `/api/health` w ciągu 5 s zwraca `agent: false` i komunikat
   „Nie mogę połączyć się z Ollamą…”, a `/api/agent` zwraca **503** z `error` po polsku.
3. Ustaw `MODEL=nie-ma-takiego-modelu` i wywołaj `/api/agent`. Kryterium: 503 z podpowiedzią
   `ollama pull …`; brak ponowień i brak innych dostawców w `serwer/agent.log`.
4. Ustaw `MODEL_NUM_CTX=2048` i zadaj „Jakie mam dokumenty?”. Kryterium: brak wywołania narzędzia albo błąd
   kontekstu — to potwierdza, że parametr jest używany i pokazuje, dlaczego domyślnie jest 32768.
5. `python3 serwer/bielik.py`. Kryterium: raport pokazuje model, dostawcę, kontekst, próbkowanie i czy model
   jest pobrany; przy braku modelu podpowiada `--pobierz`.
6. Ustaw `MODEL=llama3:8b` (przy `BIELIK_TYLKO=1`). Kryterium: `/api/health` zwraca `bielik: false`,
   `agent: false` i komunikat o wyborze Bielika, `/api/agent` zwraca **503** z tym samym wyjaśnieniem,
   a interfejs pokazuje ostrzeżenie zamiast rozmowy.
7. To samo z `BIELIK_TYLKO=0`. Kryterium: model działa, ale `/api/health` ma `bielik: false` i ostrzeżenie,
   że projekt jest strojony pod Bielika.
8. Bielik w innym wariancie (`MINITRON`, `Q8_0`, `4.5B`). Kryterium: `bielik: true`, brak blokady;
   jakość wyboru narzędzi może się różnić i to jest oczekiwane.

### 2.2 Rozmowa i narzędzia (model prawdziwy)

| Scenariusz | Krok | Oczekiwany wynik |
|---|---|---|
| Odczyt danych | „Jakie mam dokumenty?” | odpowiedź po polsku, 1–3 zdania, karta z listą dokumentów, propozycja 2–4 dalszych kroków |
| Odczyt z parametrem | „Ile mam punktów karnych?” | karta z `punkty_karne`, żadna liczba nie pochodzi z tekstu modelu |
| Akcja z potwierdzeniem | „Zastrzeż mój PESEL” | karta `confirm` z przyciskami Anuluj/Potwierdź, **brak** wykonania przed potwierdzeniem |
| Potwierdzenie | dotknij „Potwierdź” | animacja Face ID, karta wyniku (`tone: ok`), stan świata zmieniony; w dzienniku `akcja ok: true` |
| Anulowanie | dotknij „Anuluj” | brak zmiany stanu, model mówi, że nic nie wysłano; w dzienniku `akcja ok: false` |
| Jedna czynność naraz | poproś o dwie akcje w jednym zdaniu | druga akcja jest zablokowana (`blokada_lancucha` w dzienniku) i model pyta o zgodę |
| Zakończenie rozmowy | „Dziękuję, to wszystko” | jedno zdanie pożegnania i zdarzenie `koniec`; w trybie głosowym mikrofon przestaje słuchać |
| Wyjście poza temat | „Napisz wiersz o morzu” | odmowa jednym zdaniem i powrót do spraw urzędowych |

Dodatkowe kryterium jakości: w 10 kolejnych odpowiedziach nie ma słów w innym alfabecie (cyrylica, greka)
ani angielskich wtrętów; jeśli się pojawią, `popraw_jezyk()` je usuwa, a wpis `jezyk` nie występuje w dzienniku
(bo nie ma już dodatkowego wywołania modelu).

### 2.3 Frontend

1. **Start**: `python3 serwer/server.py`, wejście na `/aplikacja`. Kryterium: brak błędów w konsoli,
   karty dokumentów mają tła i dane, przełączanie `?uklad=stos|karuzela|pion|lista|siatka` działa bez przeładowania.
2. **Osoby**: menu układów → wybór Kacpra. Kryterium: adres zawiera `?osoba=kacper`, dane i sprawy się zmieniają,
   wybór jest pamiętany po odświeżeniu.
3. **Prywatność mDowodu**: po wejściu widać tylko imię. Kryterium: „Pokaż dane” odsłania pełne dane, a ukrycie
   karty przeglądarki (`visibilitychange`) znów je zasłania.
4. **Karta dokumentu**: dotknięcie karty. Kryterium: arkusz ma nagłówek z nazwą, grafikę, status ważności,
   cztery akcje, „Wróć” zamyka.
5. **Klikalność**: przejdź wszystkie ekrany i kliknij każdy przycisk. Kryterium: każdy robi coś widocznego —
   arkusz dokumentu (4 akcje), „Wróć”, znak mObywatela, „Skrzynka” (pyta asystenta), „Powiadomienia”,
   wysyłanie wiadomości, opcje pod odpowiedzią, karta potwierdzenia, a na `/komputer` „Przejdź do płatności”
   i „Zacznij od nowa”. Przycisk mikrofonu bez rozpoznawania mowy pokazuje podpowiedź, a nie milczy.
6. **Bez ekranu w ekranie**: wejdź w mDowód. Kryterium: arkusz pokazuje kartę rysowaną przez aplikację,
   bez drugiego paska statusu, drugiego „Wróć” i wklejonej daty ze zrzutu.
7. **Wyśrodkowanie**: okno szersze niż 520 px i wyższe niż 900 px. Kryterium: ramka telefonu leży na środku
   ekranu w obu osiach (`align-items: center`, `justify-content: center`), ma równy margines z każdej strony,
   a przy niskim oknie kurczy się przez `max-height` zamiast wychodzić poza ekran. Poniżej 520 px szerokości
   ramka zajmuje cały ekran bez paddingu i bez zaokrągleń.
8. **Sprawy**: przycisk „Do załatwienia”. Kryterium: lista terminów, dotknięcie pozycji otwiera rozmowę z gotowym
   pytaniem, `Esc` zamyka arkusz.
6. **Historia rozmów**: dwie rozmowy, przełączanie. Kryterium: tytuły, godziny, nieprzeczytane, „Nowa rozmowa”.
7. **Wydajność**: Lighthouse (mobile) na `/aplikacja` bez modelu. Kryterium: JS ≤ 120 kB gzip na start,
   LCP ≤ 1,5 s na lokalnym serwerze, brak żądań zewnętrznych (poza własnym `/api`).
8. **Dostępność**: klawiatura. Kryterium: każdy przycisk ma nazwę (`aria-label`), `Esc` zamyka arkusze,
   fokus widoczny, kontrast tekstu ≥ 4,5:1.

### 2.4 Głos

1. Chrome/Edge, `https://` lub `localhost`. Kryterium: mikrofon w komponencie przyjmuje mowę, tekst trafia
   do rozmowy z prefiksem `[głos]`, odpowiedź jest czytana, mikrofon wznawia się po zakończeniu czytania.
2. Odmowa dostępu do mikrofonu. Kryterium: komunikat „Brak dostępu do mikrofonu…”, brak pętli błędów.
3. Przeglądarka bez `SpeechRecognition` (np. Firefox). Kryterium: przycisk mikrofonu nieaktywny z podpowiedzią,
   rozmowa tekstowa działa.
4. Karta potwierdzenia w trybie głosowym. Kryterium: stan „Potwierdź na karcie”, mikrofon nie nasłuchuje,
   po potwierdzeniu/odrzuceniu wraca słuchanie.

### 2.5 Znak mObywatela

1. Telefon (`/aplikacja`) → „Przyjmij dane”, komputer (`/komputer`) skanuje znak z ekranu telefonu.
   Kryterium: komputer pokazuje dane, żeton zmienia się co 30 s, „Zakończ” czyści ekran po 180 s.
2. Drugi telefon w tej samej sieci, „Potwierdź swoje dane” skanuje znak z komputera. Kryterium: zgoda z listą
   zakresu, „Udostępnij” → dane na komputerze, „Odmów” → komputer wraca do czekania.
3. Skanowanie własnego znaku. Kryterium: komunikat „To Twój własny znak…”, brak przekazania.
4. Wyjście z ekranu skanera. Kryterium: kamera zwolniona (dioda gaśnie), brak `getUserMedia` w tle.

### 2.6 Wersje językowe

1. `/de/aplikacja`. Kryterium: interfejs i etykiety kart z `serwer/i18n/de.json`, brak tekstów w innych
   językach; nieprzetłumaczone zdania zostają po polsku i pojawiają się w `serwer/i18n/_zrodla.json`
   (plik powstaje przy pierwszym braku). Tekst z modelu (`body`, `note`, propozycje) zostaje po polsku —
   to treść generowana, nie etykieta.
2. Rozmowa z asystentem po niemiecku. Kryterium: asystent odpowiada po polsku (brak tłumaczenia maszynowego) —
   to zachowanie zamierzone i musi być opisane w interfejsie.

### 2.7 Docker

1. `docker compose up --build` z `OLLAMA_URL=http://host.docker.internal:11434`.
   Kryterium: `/api/health` widzi model, `modelGotowy: true`, port wystawiony tylko na `127.0.0.1`.
2. Pusty `.env`. Kryterium: serwer startuje, `/api/health` zwraca komunikat o modelu, aplikacja działa
   w trybie przeglądania dokumentów.
3. Brakujący `frontend/dist`. Kryterium: czytelny komunikat „uruchom npm run build”, kod 503, brak śladu wyjątku.

## 3. Szybki test dymny (bez modelu)

```bash
python3 serwer/server.py &
curl -s localhost:8790/api/health | python3 -m json.tool          # agent: false + komunikat
curl -s -o /dev/null -w "%{http_code}\n" localhost:8790/aplikacja  # 200
curl -s -o /dev/null -w "%{http_code}\n" localhost:8790/komputer   # 200
curl -s -X POST localhost:8790/api/agent -H 'Content-Type: application/json' \
  -d '{"messages":[{"role":"user","content":"Cześć"}],"osoba":"marta"}' -w " %{http_code}\n"   # 503
```

## 4. Znane ograniczenia

- Jakość rozmów zależy od kwantyzacji. Q4_K_M bywa niespójny przy długich rozmowach; Q8_0 jest lepszy, ale wolniejszy.
- Bielik 11B nie jest trenowany pod wywoływanie narzędzi tak dobrze jak modele komercyjne: czasem wywoła
  narzędzie niepotrzebnie albo pominie krok. `napraw_wyciek()` łagodzi tylko przypadek wywołania w tekście.
- Rozpoznawanie mowy w przeglądarce może wysyłać dźwięk do usługi dostawcy przeglądarki (tak działa Chrome).
- Interfejs tłumaczy stałe etykiety, nazwy dokumentów i podpisy pól kart (`t()` w `DocumentFace.vue`,
  `DocumentSheet.vue`, `Wallet.vue`, `DataCard.vue`). Nie tłumaczy wartości z rejestrów ani tekstu
  generowanego przez model — przy `?lang=de` zdania Bielika i dane osobowe zostają po polsku.
- Serwer nie ma uwierzytelniania, limitów żądań ani kolejki do modelu: dwa równoległe pytania kolejkują się
  w Ollamie i oba mogą czekać dłużej niż `MODEL_TIMEOUT`.
