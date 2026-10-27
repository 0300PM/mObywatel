# -*- coding: utf-8 -*-
"""Pętla agenta: darmowy model z Cloudflare Workers AI + narzędzia.
Bezstanowa: klient przechowuje historię rozmowy i stan świata."""
import json, os, re, time, copy, urllib.request, urllib.error, html
import dane, akcje, persony, threading, katalog, model
_JEZ = threading.local()
from narzedzia import WSZYSTKIE, NAZWY_ODCZYTOW, NAZWY_AKCJI, NAZWY_UI, NAZWY_KLIENT

DNI = ['poniedziałek', 'wtorek', 'środa', 'czwartek', 'piątek', 'sobota', 'niedziela']

SYSTEM = """Jesteś asystentem w aplikacji mObywatel. Rozmawiasz z {zalogowana}: {kto}, PESEL {pesel}, {okolica} (tożsamość potwierdzona mDowodem). Dziś jest {dzis} ({dzien}).{meski}

Działasz na prawdziwych (w tej wersji: demonstracyjnych) danych z rejestrów państwowych przez narzędzia i załatwiasz sprawy w imieniu {dop}. Różnisz się od czatbota z bazą wiedzy tym, że sprawdzasz dane i wykonujesz usługi.

Zasady:
- Pisz wyłącznie po polsku, poprawną polszczyzną i alfabetem łacińskim. Nigdy nie wstawiaj słów z innych języków (np. rosyjskich czy angielskich). Pisz krótko i ciepło: 1–3 zdania w wiadomości. Zwracaj się na „Ty” w formie {forma}. Bez list, nagłówków i tabel: dane pokazują karty w aplikacji. Ważne wartości możesz wyróżnić **pogrubieniem**.
- Dane bierz WYŁĄCZNIE z narzędzi. Nie zgaduj numerów, dat ani kwot. Gdy czegoś brakuje, zapytaj.
- Karta z danymi z narzędzia jest widoczna dla użytkowniczki. Nie powtarzaj wszystkich jej wartości, tylko skomentuj najważniejsze lub zaproponuj krok.
- Każda czynność ze skutkiem prawnym lub finansowym idzie przez narzędzie akcji. Aplikacja sama pokaże kartę potwierdzenia z Face ID, więc NIE pytaj w tekście „czy potwierdzasz?”. Gdy masz komplet danych, od razu wywołaj akcję. Pytaj tylko o brakujące dane albo o wybór, którego nie da się ustalić z rejestrów.
- Gdy brakuje szczegółu, który ma rozsądną wartość domyślną, przyjmij ją i pokaż na karcie potwierdzenia zamiast pytać: urząd do odcisków palców i odbioru dowodu to urząd najbliżej miejsca, gdzie mieszka (może wybrać dowolny w Polsce), odpis aktu elektronicznie do skrzynki e-Doręczeń, płatność BLIK (Apple Pay, Google Pay lub karta tylko tam, gdzie gmina je udostępnia). Miejsce zgłoszenia (sanepid, GIOŚ) bierzesz z jej słów; GPS przyjmij tylko, gdy mówi o miejscu, w którym jest teraz. Użytkowniczka może to zmienić, anulując kartę. Wyjątki, o które zawsze pytasz: imię dziecka (najwyżej dwa imiona, w pełnej formie, nie zdrobnienie: Zofia, nie Zosia), nazwa firmy i forma opodatkowania (skala, liniowy, ryczałt), wybór terminu, a przy kilku pojazdach: którego dotyczy sprawa. Opis zgłoszenia (sanepid, GIOŚ, CERT, internet) bierzesz z jej słów, nie pytaj o więcej szczegółów.
- Jedna akcja naraz. Po wyniku krótko powiedz, co się stało, i zaproponuj sensowny następny krok (zaproponuj_odpowiedzi). Nigdy nie wywołuj kolejnej czynności, o którą użytkowniczka nie poprosiła, zanim się nie zgodzi.
- Gdy akcja zwraca błąd z wyjaśnieniem (np. sprawa wymaga wizyty, termin jeszcze nie biegnie, dokument jest unieważniony), nie ponawiaj jej: przekaż to własnymi słowami i zaproponuj, co da się zrobić (np. gdzie_zalatwic, przypomnienie).
- Prawie każdą odpowiedź kończ wywołaniem zaproponuj_odpowiedzi z 2–4 krótkimi opcjami: gdy pytasz o wybór (np. termin, wariant), gdy proponujesz coś zrobić („Mogę…”), gdy sprawa ma naturalny następny krok. Pomiń je tylko, gdy sprawa jest zamknięta albo pytasz o dane do wpisania (imię, numer). Wybór kilku pozycji naraz: wybor_wielokrotny.
- Gdy użytkowniczka kończy rozmowę („dziękuję, to wszystko”, „nic więcej”, „do widzenia”, inne pożegnanie), ZAWSZE w tej samej odpowiedzi napisz jedno krótkie zdanie pożegnania i wywołaj narzędzie zakoncz_rozmowe (bez zaproponuj_odpowiedzi). Bez tego mikrofon dalej słucha. Samo „dziękuję” po wykonanej sprawie, bez sygnału końca, to jeszcze nie koniec.
- Nie pisz o tym, że coś „wyświetliłaś” albo o przyciskach. Nie używaj długich myślników (—), zamiast nich przecinki lub kropki.
- Myśl jak dobry urzędnik, który zna całą sprawę:
  Zgubiony portfel: zapytaj, co w nim było i czy portfel może się znaleźć. Słowa: „zastrzec” to wpis w bankach (System Dokumenty Zastrzeżone, cofniesz tutaj), „zablokować” to blokada dowodu na 14 dni (odblokujesz tutaj, po 14 dniach bez odblokowania dowód zostanie unieważniony), „unieważnić” to na zawsze. Gdy może się znaleźć: zaproponuj zastrzeżenie dowodu i paszportu w bankach (zastrzez_dokumenty) i blokadę dowodu (zawies_dowod), oba da się cofnąć; jedno po drugim, każde po jej zgodzie; PESEL wtedy nie zastrzega się sam, możesz go zaproponować osobno. Gdy przepadł albo został skradziony: zastrzeż i unieważnij (zastrzez_dokumenty z uniewaznij=true), powiedz, że tego nie da się cofnąć, a PESEL zastrzeże się sam, więc go nie proponuj. Potem zaproponuj wniosek o nowy dowód. Prawa jazdy nie zastrzeżesz ani nie unieważnisz: to wniosek o wtórnik za 100 zł w wydziale komunikacji (gdzie_zalatwic). Karty płatnicze zastrzega bank, nie Ty: w jego aplikacji, na infolinii albo pod numerem +48 828 828 828, jeśli bank jest w systemie Zastrzegam.pl; zastrzeżonej karty bank nie odblokuje, wyda nową. Przy kradzieży doradź zgłoszenie na policji. Gdy dokument się znajdzie: zastrzeżenie w bankach cofniesz (cofnij_zastrzezenie_dokumentu), blokadę zdejmiesz (odwies_dowod), unieważnionego nie: powiedz, że jest już unieważniony, trzeba go oddać w dowolnym urzędzie gminy, a nowy wniosek złożysz tutaj.
  Dowód osobisty: wniosek wyślesz stąd, ale w ciągu 30 dni trzeba pójść do urzędu na odciski palców i wzór podpisu, a dowód odbiera się tam osobiście, do 30 dni po wizycie (dziecko poniżej 12 lat: bez odcisków, przy odbiorze dziecko od 5 lat). Powiedz to, zanim wywołasz akcję, a po wyniku zaproponuj przypomnienie o wizycie.
  Paszport: online złożysz tylko wniosek dla dziecka poniżej 12 lat (wniosek_paszport; zgoda drugiego rodzica, odbiór z dzieckiem od 5 lat). Dorosły, dziecko od 12 lat i paszport tymczasowy: tylko osobiście w punkcie paszportowym (gdzie_zalatwic), potem zaproponuj przypomnienie i listę do zabrania.
  PESEL: gdy jest już zastrzeżony, nie zastrzegaj go ponownie, pokaż status. Zastrzeżenie nie blokuje lekarza, apteki, bankomatu ani urzędu; bank musi je sprawdzić przed kredytem.
  Kupno auta: historia pojazdu (numer rejestracyjny, VIN i data pierwszej rejestracji; gdy ich brak, poproś o nie albo o zdjęcie dowodu rejestracyjnego od sprzedającego), OC (polisa sprzedającego przechodzi na Ciebie i nie przedłuży się sama), czerwone flagi, umowa (podpis zaufany lub osobisty obu stron), PCC-3: 2% wartości rynkowej w 14 dni, bez podatku przy wartości do 1000 zł albo zakupie na fakturę od firmy. Rejestracja w 30 dni w wydziale komunikacji, tablice i dowód rejestracyjny odbiera się osobiście; nie obiecuj rejestracji w aplikacji.
  Narodziny: gratulacje, potem zgłoszenie urodzenia (21 dni od wystawienia karty urodzenia; zgłasza mama albo tata, a tata, który nie jest mężem mamy, tylko po uznaniu ojcostwa). PESEL i odpis aktu przychodzą zwykle następnego dnia roboczego. Potem zaproponuj 800+ (wniosek w ciągu 3 miesięcy od urodzenia daje świadczenie od dnia urodzenia). Przypomnij, że dziecko do ubezpieczenia zdrowotnego zgłasza pracodawca albo sam rodzic w eZUS, w ciągu 7 dni. Przy trzecim dziecku albo gdy rodzina ma już KDR, zaproponuj kartę dla dziecka (gdzie_zalatwic).
  Stłuczka lub wypadek z udziałem kierowców: najpierw zapytaj, czy ktoś jest ranny; jeśli tak, każ dzwonić pod 112 i nie spisuj oświadczenia. mStłuczka działa, gdy oboje macie mObywatela, zgadzacie się, kto jest sprawcą, i oba auta mają polską rejestrację; jeśli nie, spiszcie oświadczenie na papierze albo wezwijcie policję. Gdy sprawcą jest użytkowniczka, szkodę zgłasza druga strona. Gdy ktoś podaje numer rejestracyjny auta, które uszkodziło jej samochód, od razu sprawdź jego OC.
  Podejrzany SMS: analiza, ostrzeżenie, pytanie, czy podała dane, zgłoszenie strony z linku do CERT Polska (zglos_incydent_cert), a sam SMS niech prześle na bezpłatny numer 8080. Mów, że domena jest na Liście Ostrzeżeń CERT, tylko gdy narzędzie to podaje. Jeśli podała dane karty, niech od razu dzwoni do banku; jeśli dane dowodu, zaproponuj unieważnienie dowodu (PESEL zastrzeże się sam).
  Płatności: tutaj płacisz tylko podatki i opłaty lokalne z ePłatności. Składek ZUS, mandatów i podatku w gminie spoza ePłatności nie zapłacisz tutaj; powiedz, gdzie i jak to zrobić (podają to naleznosci i wynik akcji) i zaproponuj przypomnienie.
  Firma: zapytaj o formę opodatkowania, a po wniosku przypomnij, że do ubezpieczeń w ZUS zgłasza się w 7 dni na biznes.gov.pl, a VAT-R składa osobno.
  Głosowanie w innym miejscu: jednorazowo zmienisz je od 44. do 3. dnia przed wyborami, a wybory do Sejmu jeszcze nie są zarządzone, więc zaproponuj przypomnienie. Jeśli mieszka w tej gminie na stałe bez meldunku, możesz już teraz złożyć zmianę stałego obwodu (zmien_miejsce_glosowania, rodzaj=staly; urząd ma 5 dni).
  Podróż: w Odyseuszu dopisujesz dzieci, dorośli zgłaszają się sami; zaproponuj dodanie kraju do obserwowanych. Nie mów, że w kraju nie ma ostrzeżeń, jeśli narzędzie tego nie podaje.
  Dane kontaktowe: po zmianie telefonu lub e-maila poproś o kod z SMS-a lub e-maila i wywołaj akcję ponownie z kodem.
  Ulgi z legitymacji studenckiej: mów tylko o ustawowej uldze kolejowej 51% do 26 lat; resztę ustala przewoźnik lub miasto.
- Procedury, opłaty, terminy, wymagane dokumenty i to, co trzeba zrobić osobiście, bierz z karty_uslugi (oficjalne karty gov.pl). Sprawdź ją, zanim powiesz, jak, gdzie albo czy da się coś załatwić, i trzymaj się jej treści. Gdy karta mówi, że trzeba iść do urzędu (np. odciski palców do dowodu, odbiór dokumentu, tablice rejestracyjne), powiedz to wprost w pierwszym zdaniu i nie obiecuj, że załatwisz to w aplikacji. Gdy karty brak, nie zgaduj: odeślij do gov.pl albo właściwego urzędu.
- Załatwiasz tylko to, na co masz narzędzia. Gdy sprawy nie zrobisz w tej aplikacji, od razu wywołaj gdzie_zalatwic i w pierwszym zdaniu powiedz, gdzie ją załatwić: online na gov.pl lub w innym oficjalnym serwisie (zameldowanie, wymeldowanie, zmiana nazwiska przez e-Doręczenia, Karta Dużej Rodziny na empatia.gov.pl, roczny PIT w Twoim e-PIT, do którego zalogujesz się mObywatelem) albo w urzędzie (ślub, zgłoszenie zgonu, rejestracja pojazdu, prawo jazdy, paszport dla dorosłego). Nie mów, że czegoś nie da się zrobić przez internet, jeśli karta podaje drogę online. Nie zbieraj danych do takiej sprawy i nie udawaj, że ją przygotowujesz. Możesz zaproponować to, co w aplikacji pomoże (np. przypomnienie albo sprawdzenie danych).
- Nie interpretujesz wiążąco przepisów. W sprawach spornych lub nietypowych kieruj do właściwego urzędu. Nie udzielaj porad inwestycyjnych ani medycznych.
- Prośby spoza spraw urzędowych (wiersze, opowiadania, przepisy kulinarne, zadania szkolne, opinie polityczne) uprzejmie odmawiaj jednym zdaniem i powiedz, w czym możesz pomóc. Nie spełniaj ich nawet częściowo.
- Gdy użytkowniczka prosi o pokazanie dokumentu, użyj pokaz_dokument.
- Przekazywanie danych (usługa Potwierdź swoje dane; w tej wersji znak mObywatela zamiast kodu QR) działa jednym skanerem: kto skanuje znak mObywatela, ten przekazuje swoje dane właścicielowi znaku, a zakres danych ustala właściciel znaku. Gdy ktoś inny (strona na komputerze, wypożyczalnia, urzędnik, kasjerka) chce dostać JEJ dane, użyj przekaz_dane: ona zeskanuje znak odbiorcy i potwierdzi Face ID. Gdy ONA chce dostać lub sprawdzić dane innej osoby, użyj przyjmij_dane: pokażesz jej znak, a tamta osoba zeskanuje go u siebie. Przy stłuczce dane drugiego kierowcy pobierasz tak samo (cel=mstluczka). Przed wywołaniem napisz jedno krótkie zdanie, co się zaraz stanie. Po wyniku krótko podsumuj.
- Wiadomość zaczynająca się od [głos] była powiedziana na głos, a Twoje odpowiedzi w tej rozmowie są czytane przez syntezator: pisz krótko, pełnymi zdaniami, bez skrótów i symboli (zamiast „r.” pisz „roku”, zamiast „zł” pisz „złotych”), daty z nazwą miesiąca (29 października), ale liczby i numery zostaw cyframi. Najważniejszą informację z karty powiedz w tekście. Przycisków nie słychać: zanim wywołasz zaproponuj_odpowiedzi albo wybor_wielokrotny, zawsze zadaj pytanie w tekście.
- Wiadomość zaczynająca się od [zdjęcie] zawiera wynik odczytu zdjęcia zrobionego aparatem."""

def system_prompt():
    p = persony.P(); k = p['plec'] == 'K'
    s = SYSTEM.format(dzis=dane.pl(dane.DZIS), dzien=DNI[dane.DZIS.weekday()], kto=p['osoba']['imie'] + ' ' + p['osoba']['nazwisko'], pesel=p['osoba']['pesel'],
        okolica=p['okolica'], dop=p['dop'], zalogowana='zalogowaną użytkowniczką' if k else 'zalogowanym użytkownikiem',
        forma='żeńskiej (np. „zgubiłaś”)' if k else 'męskiej (np. „zgubiłeś”)',
        meski='' if k else '\nUWAGA: rozmawiasz z mężczyzną. Gdzie poniższe zasady i opisy narzędzi mówią „użytkowniczka”, „ona”, „jej”, chodzi o niego. Zawsze używaj form męskich.')
    return s

def bez_myslnikow(t):
    return re.sub(r'\s*—\s*', ', ', re.sub(r'\s+–\s+', ', ', t)).replace(', ,', ',').replace(', .', '.')

def md(t):
    t = html.escape(bez_myslnikow(t.strip()), quote=False)
    t = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', t)
    t = re.sub(r'(?m)^\s*[-•]\s+', '• ', t)
    return t.replace('\n\n', '<br><br>').replace('\n', '<br>')

class BladAPI(Exception):
    pass

DOSTAWCA = 'cloudflare'
MODEL_MAX_TOKENS = model.MAX_TOKENS
MODEL_TIMEOUT = model.TIMEOUT
MODEL_NUM_CTX = model.NUM_CTX
MYSLI = re.compile(r'(?s)<think>.*?</think>\s*')
_stan = {}
_stan_lock = threading.Lock()

TOOLS = [{'type': 'function', 'function': {'name': t['name'], 'description': t['description'], 'parameters': t['input_schema']}}
         for t in WSZYSTKIE]


def _id9(x):
    """Stały, 9-znakowy identyfikator wywołania (część szablonów czatu wymaga krótkich identyfikatorów)."""
    import hashlib
    return hashlib.sha1(str(x).encode()).hexdigest()[:9]


def do_chat(messages):
    """Historia w formacie bloków (text/tool_use/tool_result) -> wiadomości Chat Completions."""
    out = [{'role': 'system', 'content': system_prompt()}]
    for m in messages:
        c = m['content']
        if isinstance(c, str):
            out.append({'role': m['role'], 'content': c})
            continue
        txt = '\n\n'.join(b.get('text', '') for b in c if b.get('type') == 'text' and b.get('text', '').strip())
        if m['role'] == 'assistant':
            calls = [{'id': _id9(b['id']), 'type': 'function', 'function': {'name': b['name'], 'arguments': json.dumps(b.get('input') or {}, ensure_ascii=False)}}
                     for b in c if b.get('type') == 'tool_use']
            if txt or calls:
                msg = {'role': 'assistant', 'content': txt}
                if calls:
                    msg['tool_calls'] = calls
                out.append(msg)
            continue
        for b in c:
            if b.get('type') == 'tool_result':
                o = b.get('content')
                out.append({'role': 'tool', 'tool_call_id': _id9(b['tool_use_id']), 'content': o if isinstance(o, str) else json.dumps(o, ensure_ascii=False)})
        if txt:
            out.append({'role': 'user', 'content': txt})
    return out


def _blad_modelu(txt, kod=None):
    """Zamienia odpowiedź Cloudflare na czytelny komunikat po polsku (bez przełączania na płatne API)."""
    tresc = (txt or '').lower()
    if kod in (401, 403):
        return BladAPI('Cloudflare odrzucił żądanie (kod %s). Sprawdź token CLOUDFLARE_API_TOKEN (%s).'
                       % (kod, model.klasa_klucza()))
    if kod == 429:
        if 'neuron' in tresc or 'capacity' in tresc or 'limit' in tresc:
            return BladAPI('Skończył się dzienny limit darmowych neuronów Cloudflare (10 000 na dobę).'
                           ' Limit odnawia się o północy UTC, a mniejszy model z katalogu zużywa go wolniej'
                           ' (MODEL=auto).')
        return BladAPI('Cloudflare jest zajęty (za dużo żądań). Spróbuj za chwilę.')
    if kod == 404 or (kod == 400 and 'model' in tresc):
        return BladAPI('Cloudflare nie udostępnia modelu %s na tym koncie. Wybierz inny z katalogu'
                       ' (MODEL=auto): %s.'
                       % (model.model() or '(brak)', ', '.join(m.nazwa for m in katalog.najszybsze(3))))
    if kod in (408, 504):
        return BladAPI('Model nie odpowiedział w czasie. Spróbuj jeszcze raz.')
    if kod:
        return BladAPI('Cloudflare zwrócił błąd %s: %s' % (kod, (txt or '')[:200]))
    return BladAPI(txt or 'brak odpowiedzi modelu')


def _podlacz(req, timeout):
    """Pojedyncze żądanie HTTP do serwera modelu; błędy sieci dostają komunikat po polsku."""
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        raise _blad_modelu(e.read().decode('utf-8', 'replace'), e.code)
    except (urllib.error.URLError, ConnectionError, OSError) as e:
        raise BladAPI('Nie mogę połączyć się z Cloudflare pod adresem %s. Sprawdź internet, CLOUDFLARE_ACCOUNT_ID'
                      ' i CLOUDFLARE_API_TOKEN. (%s)' % (model.adres(), getattr(e, 'reason', e)))


def _tekst_z_odpowiedzi(txt):
    if isinstance(txt, list):
        txt = ''.join(p.get('text', '') for p in txt if isinstance(p, dict))
    return MYSLI.sub('', txt or '').strip()


def _odpowiedz(out):
    """Wyciąga wiadomość i statystyki z odpowiedzi Cloudflare.

    `/ai/v1/chat/completions` zwraca format OpenAI, a `/ai/run` opakowuje go w `result` i używa pola
    `response`. Obsługujemy oba, żeby podmiana adresu nie wymagała zmian w kodzie.
    """
    dane = out.get('result') if isinstance(out.get('result'), dict) else out
    msg = ((dane.get('choices') or [{}])[0] or {}).get('message') or {}
    if not msg and dane.get('response') is not None:
        msg = {'content': dane.get('response'), 'tool_calls': dane.get('tool_calls')}
    return msg, dane


def _wywolania(calls):
    """Jedna czynność naraz, tak jak u wszystkich dostawców."""
    out = []
    for i, c in enumerate((calls or [])[:1]):
        f = c.get('function') or c
        a = f.get('arguments')
        if isinstance(a, str):
            try:
                a = json.loads(a or '{}')
            except Exception:
                a = {}
        out.append(dict(type='tool_use', id=c.get('id') or _id9('%s-%d-%d' % (f.get('name'), i, time.time() * 1000)),
                        name=f.get('name'), input=a if isinstance(a, dict) else {}))
    return out


def czat(messages, log):
    """Rozmowa przez Cloudflare Workers AI (OpenAI Chat Completions).

    Żądanie idzie z serwera z tokenem z `.env`, więc wnioskowanie nie odbywa się na tej maszynie.
    """
    nazwa = model.model()
    if not nazwa:
        raise BladAPI(model.komunikat_modelu() or 'Nie wybrano modelu')
    body = dict(model=nazwa, messages=do_chat(messages), tools=TOOLS, tool_choice='auto',
                parallel_tool_calls=False, **model.OPCJE)
    naglowki = model.naglowki()
    ostatni = None
    for proba in range(2):
        req = urllib.request.Request(model.adres() + '/chat/completions', data=json.dumps(body).encode(),
                                     headers=naglowki)
        t0 = time.time()
        try:
            out = _podlacz(req, MODEL_TIMEOUT)
        except BladAPI as e:
            ostatni = str(e)
            if proba == 0 and 'parallel_tool_calls' in ostatni and 'parallel_tool_calls' in body:
                body.pop('parallel_tool_calls')
                continue
            if proba == 0 and 'Nie mogę połączyć' in ostatni:
                time.sleep(1.0)
                continue
            raise
        msg, dane = _odpowiedz(out)
        content = []
        txt = _tekst_z_odpowiedzi(msg.get('content'))
        if txt:
            content.append(dict(type='text', text=txt))
        content += _wywolania(msg.get('tool_calls'))
        u = dane.get('usage') or {}
        log(dict(t='llm', model=dane.get('model', nazwa), provider=DOSTAWCA, ms=int((time.time() - t0) * 1000),
                 usage=dict(input=u.get('prompt_tokens'), output=u.get('completion_tokens'))))
        return dict(content=content, stop_reason='tool_use' if any(b['type'] == 'tool_use' for b in content) else 'end_turn')
    raise BladAPI(ostatni or 'brak odpowiedzi modelu')


ZNACZNIKOW_NA_TOKEN = 3
REZERWA_TOKENOW = 512


def _rozmiar(wiadomosc):
    tresc = wiadomosc.get('content')
    return len(tresc) if isinstance(tresc, str) else len(json.dumps(tresc, ensure_ascii=False))


def _tylko_wyniki(wiadomosc):
    tresc = wiadomosc.get('content')
    return (wiadomosc.get('role') == 'user' and isinstance(tresc, list) and bool(tresc)
            and all(b.get('type') == 'tool_result' for b in tresc))


def zajete_tokeny():
    """Ile tokenów zjada to, czego przyciąć nie można: instrukcja systemowa i definicje narzędzi."""
    return (len(system_prompt()) + len(json.dumps(TOOLS, ensure_ascii=False))) // ZNACZNIKOW_NA_TOKEN


def przytnij(messages, dostepne=None):
    """Zostawia najnowszą część historii mieszczącą się w oknie kontekstu.

    Okno musi pomieścić instrukcję systemową, opisy narzędzi i odpowiedź modelu, a historia rośnie
    z każdą turą. Bez przycinania dostawca po cichu obcina początek promptu, więc model traci instrukcję
    i przestaje wywoływać narzędzia.
    """
    dostepne = MODEL_NUM_CTX - MODEL_MAX_TOKENS - REZERWA_TOKENOW - zajete_tokeny() if dostepne is None else dostepne
    if dostepne <= 0:
        return messages[-1:]
    suma, start = 0, len(messages)
    for i in range(len(messages) - 1, -1, -1):
        suma += _rozmiar(messages[i]) // ZNACZNIKOW_NA_TOKEN
        if suma > dostepne:
            break
        start = i
    while start < len(messages) and (messages[start].get('role') != 'user' or _tylko_wyniki(messages[start])):
        start += 1
    return messages[start:] if start < len(messages) else messages[-1:]


def llm(messages, keys, log):
    try:
        model.sprawdz_model()
    except ValueError as e:
        raise BladAPI(str(e))
    przyciete = przytnij(messages)
    if len(przyciete) < len(messages):
        log(dict(t='kontekst', wszystkich=len(messages), wyslanych=len(przyciete), zajete=zajete_tokeny(), okno=MODEL_NUM_CTX))
    return czat(przyciete, log)


def stan_modelu(odswiez=False):
    """Czy model jest gotowy w Cloudflare. Wynik trzymamy chwilę, żeby /api/health był szybki."""
    with _stan_lock:
        teraz = time.time()
        if not odswiez and _stan and teraz - _stan.get('t', 0) < 5:
            return _stan
        nazwa = model.model(odswiez)
        wynik = dict(t=teraz, ok=False, model=nazwa, provider=DOSTAWCA,
                     bielik=model.czy_bielik(nazwa), klucz=model.KLUCZ_USTAWIONY,
                     konto=model.KONTO_USTAWIONE, komunikat='')
        widoczne = model.dostepne()
        if widoczne:
            wynik['dostepne'] = widoczne
        if nazwa and (widoczne is None or nazwa in widoczne):
            wynik['ok'] = True
        elif nazwa:
            wynik['komunikat'] = ('Model %s nie jest dostępny na koncie Cloudflare. Ustaw MODEL=auto.'
                                  % nazwa)
        ostrzezenie = model.komunikat_modelu(nazwa) if nazwa else ''
        if ostrzezenie:
            wynik['komunikat'] = ostrzezenie
            wynik['ok'] = False
        _stan.clear()
        _stan.update(wynik)
        return wynik


WYCIEK = re.compile(r'\s*(?:to=)?functions\.(\w+)\s*(\{.*?\})', re.S)
JSONOWE = re.compile(r'```(?:json)?\s*|\{')
NAZWY_NARZEDZI = {t['name'] for t in WSZYSTKIE}


def _wywolanie_z_jsonu(tekst):
    """Model czasem odpowiada wyłącznie JSON-em {"name": ..., "arguments": {...}} zamiast tool_calls.

    Zwraca (wywołanie, tekst_bez_jsonu) albo (None, tekst).
    """
    dekoder = json.JSONDecoder()
    for m in JSONOWE.finditer(tekst):
        poczatek = tekst.index('{', m.start())
        try:
            obiekt, koniec = dekoder.raw_decode(tekst[poczatek:])
        except ValueError:
            continue
        if not isinstance(obiekt, dict) or obiekt.get('name') not in NAZWY_NARZEDZI:
            continue
        argumenty = obiekt.get('arguments', obiekt.get('parameters'))
        if isinstance(argumenty, str):
            try:
                argumenty = json.loads(argumenty or '{}')
            except ValueError:
                argumenty = {}
        reszta = (tekst[:m.start()] + tekst[poczatek + koniec:]).strip()
        reszta = re.sub(r'```(?:json)?', '', reszta).strip()
        return dict(type='tool_use', id='json_%d' % int(time.time() * 1000), name=obiekt['name'],
                    input=argumenty if isinstance(argumenty, dict) else {}), reszta
    return None, tekst


def napraw_wyciek(content):
    """Zamienia wywołanie narzędzia wypisane w tekście na prawdziwe wywołanie.

    Obsługuje dwa warianty typowe dla modeli czatu z formatem ChatML: `to=functions.x {...}` oraz sam JSON
    {"name": ..., "arguments": {...}} (tak działa szablon czatu tych modeli).
    """
    out = []
    for b in content:
        if b['type'] != 'text':
            out.append(b); continue
        tekst = b.get('text', '')
        m = WYCIEK.search(tekst)
        if m:
            txt = tekst[:m.start()].strip() or re.sub(r'(?s)\s*(?:to=)?functions\..*$', '', tekst).strip()
            if txt: out.append(dict(type='text', text=txt))
            if not any(x['type'] == 'tool_use' for x in content):
                try:
                    out.append(dict(type='tool_use', id='wyciek_%d' % int(time.time() * 1000), name=m.group(1), input=json.loads(m.group(2))))
                except Exception:
                    pass
            continue
        if '"name"' in tekst and not any(x['type'] == 'tool_use' for x in content):
            wywolanie, reszta = _wywolanie_z_jsonu(tekst)
            if wywolanie:
                if reszta: out.append(dict(type='text', text=reszta))
                out.append(wywolanie)
                continue
        if tekst.strip():
            out.append(b)
    return out

OBCE = re.compile('[\u0370-\u03ff\u0400-\u052f\u0590-\u06ff\u10a0-\u10ff\u3040-\u30ff\u4e00-\u9fff]')
def popraw_jezyk(text):
    """Model pisze po polsku; gdy mimo to wtrąci obce słowo albo alfabet, usuwamy je lokalnie, bez dodatkowych wywołań."""
    if not OBCE.search(text):
        return text
    for obce, polskie in {'Если': 'Jeśli', 'если': 'jeśli', 'или': 'lub', 'нет': 'nie', 'да': 'tak', 'но': 'ale', 'и': 'i'}.items():
        text = re.sub(r'(?<![\w])' + obce + r'(?![\w])', polskie, text)
    return OBCE.sub('', text).replace('  ', ' ')


def napraw(messages):
    """Każdy tool_use musi mieć tool_result w następnej wiadomości użytkownika."""
    out = []
    for i, m in enumerate(messages):
        out.append(m)
        if m['role'] != 'assistant' or not isinstance(m['content'], list): continue
        ids = [b for b in m['content'] if b.get('type') == 'tool_use']
        if not ids: continue
        nxt = messages[i + 1] if i + 1 < len(messages) else None
        have = set()
        if nxt and isinstance(nxt['content'], list):
            have = {b.get('tool_use_id') for b in nxt['content'] if b.get('type') == 'tool_result'}
        brak = [b for b in ids if b['id'] not in have]
        if not brak or nxt is None: continue
        nowe = []
        for b in brak:
            if b['name'] in NAZWY_AKCJI: tr = 'Użytkowniczka nie potwierdziła tej czynności (NIE wykonano). Zamiast tego napisała wiadomość poniżej.'
            elif b['name'] in NAZWY_KLIENT: tr = 'Skaner zamknięto bez wyniku. Odpowiedź użytkowniczki poniżej.'
            else: tr = 'Wyświetlono. Odpowiedź użytkowniczki poniżej.'
            nowe.append({'type': 'tool_result', 'tool_use_id': b['id'], 'content': tr})
        c = nxt['content'] if isinstance(nxt['content'], list) else [{'type': 'text', 'text': nxt['content']}]
        messages[i + 1] = dict(nxt, content=nowe + c)
    return messages

def wykonaj_odczyt(name, a, stan):
    f = dane.READ.get(name)
    if not f: return dict(blad='nieznane narzędzie'), None
    try:
        return f(a, stan)
    except Exception as e:
        return dict(blad=str(e)), None

PREFIKS = re.compile(r'^(\[(?:głos|zdjęcie)\]\s*)')
KONIEC = re.compile(r'\b(to wszystko|to by było wszystko|nic więcej|do widzenia|do usłyszenia|na razie|pa,? pa|żegnaj|cześć!?$|kończ(ymy|my)?\b|zakończ)', re.I)
def run(messages, stan, confirm=None, log=lambda x: None, osoba=None, jezyk='pl'):
    """Zwraca (messages, stan, events, czeka). osoba: id persony (persony.py), jezyk: kod języka interfejsu.

    Agent rozmawia wyłącznie po polsku na modelu z Cloudflare Workers AI. Interfejs tłumaczą słowniki w serwer/i18n,
    a treści z rejestrów zostają po polsku (nie ma tłumaczenia maszynowego i płatnych API)."""
    ostatnia = messages[-1]['content'] if messages and not confirm and isinstance(messages[-1].get('content'), str) else ''
    m, s, ev, cz = _run(messages, stan, confirm, log, osoba)
    if not cz and ev and all(e.get('t') == 'text' for e in ev) and not ev[-1]['plain'].rstrip().endswith('?') and KONIEC.search(PREFIKS.sub('', ostatnia)):
        ev.append(dict(t='koniec'))
        cz = 'koniec'
        log(dict(t='koniec_auto'))
    dodaj_mowe(ev)
    return m, s, ev, cz


def dodaj_mowe(ev):
    """Tryb głosowy czyta pole mow: przy karcie potwierdzenia i przy przyciskach, gdy w turze nie ma tekstu (inaczej asystent milczy)."""
    for e in ev:
        if e.get('t') == 'confirm':
            e['mow'] = (e['title'].rstrip('.') + '. ' if e.get('title') else '') + 'Sprawdź dane na karcie i potwierdź.'
    if any(e.get('t') == 'text' for e in ev): return
    for e in ev:
        o = [x.rstrip(' .!?') for x in e.get('opcje') or [] if x.strip()]
        if e.get('t') not in ('chips', 'multi') or not o: continue
        e['mow'] = ('Możesz wybrać kilka: ' + ', '.join(o) if e['t'] == 'multi' else 'Do wyboru: ' + (', '.join(o[:-1]) + ' albo ' + o[-1] if len(o) > 1 else o[0])) + '.'

def _run(messages, stan, confirm, log, osoba):
    _JEZ.j = 'pl'
    persony.ustaw(osoba)
    stan = stan or dane.stan_poczatkowy()
    events = []
    if confirm:
        last = messages[-1] if messages else None
        tu = next((b for b in (last or {}).get('content', []) if isinstance(b, dict) and b.get('type') == 'tool_use' and b.get('id') == confirm.get('id')), None)
        if tu and tu['name'] in NAZWY_KLIENT:
            if confirm.get('ok'):
                res = json.dumps(dict(zakonczono=True, wynik=confirm.get('wynik')), ensure_ascii=False)
            else:
                res = 'Użytkowniczka zamknęła swój znak, dane od drugiej osoby nie dotarły.' if tu['name'] == 'przyjmij_dane' else 'Użytkowniczka zamknęła skaner bez przekazania danych.'
            log(dict(t='qr', name=tu['name'], ok=bool(confirm.get('ok'))))
            messages.append({'role': 'user', 'content': [{'type': 'tool_result', 'tool_use_id': tu['id'], 'content': res}]})
        elif tu and tu['name'] in NAZWY_AKCJI:
            if confirm.get('ok'):
                d, karta = akcje.A[tu['name']]['wykonaj'](tu['input'], stan)
                events.append(dict(t='card', **karta))
                res = json.dumps(dict(wykonano=True, potwierdzono_face_id=True, wynik=d), ensure_ascii=False)
                log(dict(t='akcja', name=tu['name'], input=tu['input'], ok=True))
            else:
                res = 'Użytkowniczka anulowała na karcie potwierdzenia. NIE wykonano.'
                log(dict(t='akcja', name=tu['name'], ok=False))
            messages.append({'role': 'user', 'content': [{'type': 'tool_result', 'tool_use_id': tu['id'], 'content': res}]})
    napraw(messages)
    po_akcji = bool(confirm)
    czeka = None
    for krok in range(10):
        out = llm(messages, {}, log)
        content = napraw_wyciek([b for b in out['content'] if b.get('type') in ('text', 'tool_use')])
        for b in content:
            if b['type'] == 'text': b['text'] = popraw_jezyk(b['text'])
        content = [dict(type='text', text=b['text']) if b['type'] == 'text' else dict(type='tool_use', id=b['id'], name=b['name'], input=b.get('input') or {}) for b in content if b['type'] != 'text' or b['text'].strip()]
        if not content:
            messages.append({'role': 'assistant', 'content': [dict(type='text', text='(brak odpowiedzi)')]}); break
        messages.append({'role': 'assistant', 'content': content})
        wyniki = []
        for b in content:
            if b['type'] == 'text':
                events.append(dict(t='text', md=b['text'], html=md(b['text']), plain=bez_myslnikow(re.sub(r'\*\*', '', b['text']).strip())))
                continue
            n, a = b['name'], b['input']
            log(dict(t='tool', name=n, input=a))
            if n in NAZWY_ODCZYTOW:
                d, karta = wykonaj_odczyt(n, a, stan)
                if karta and a.get('pokaz_karte', True) is not False:
                    if karta.get('t') == 'qr':
                        events.append(dict(karta, t='qr'))
                    else:
                        events.append(dict(t='card', **karta))
                wyniki.append({'type': 'tool_result', 'tool_use_id': b['id'], 'content': json.dumps(d, ensure_ascii=False) + ('' if not karta else ' [karta wyświetlona]')})
            elif n == 'pokaz_dokument':
                events.append(dict(t='doc', id={'dowod': 'dowod', 'prawo_jazdy': 'pj', 'kdr': 'kdr', 'pojazd': 'auto', 'legitymacja': 'leg'}.get(a.get('dokument'), 'dowod')))
                wyniki.append({'type': 'tool_result', 'tool_use_id': b['id'], 'content': 'Dokument wyświetlony z przyciskiem Potwierdź swoje dane.'})
            elif n in NAZWY_KLIENT:
                events.append(dict(t='qrflow', id=b['id'], mode='scan' if n == 'przekaz_dane' else 'show', cel=a.get('cel') or 'tozsamosc', kto=a.get('kto'), dok=a.get('dokument')))
                czeka = 'qr'
            elif n == 'zakoncz_rozmowe':
                events.append(dict(t='koniec'))
                czeka = 'koniec'
            elif n in ('zaproponuj_odpowiedzi', 'wybor_wielokrotny'):
                opcje = [str(x) for x in (a.get('opcje') or [])][:6]
                events.append(dict(t='chips' if n == 'zaproponuj_odpowiedzi' else 'multi', opcje=opcje))
                czeka = 'odpowiedz'
            elif n in NAZWY_AKCJI and po_akcji:
                log(dict(t='blokada_lancucha', name=n))
                wyniki.append({'type': 'tool_result', 'tool_use_id': b['id'], 'is_error': True,
                               'content': 'NIE wykonano. Przed chwilą zakończyła się inna czynność. Najpierw krótko powiedz jej wynik i zapytaj, czy użytkowniczka chce tego kroku (zaproponuj_odpowiedzi). Kolejną czynność wywołaj dopiero po jej odpowiedzi.'})
            elif n in NAZWY_AKCJI:
                try:
                    karta = akcje.A[n]['podglad'](a, stan)
                except Exception as e:
                    wyniki.append({'type': 'tool_result', 'tool_use_id': b['id'], 'content': 'Błąd danych: %s' % e, 'is_error': True}); continue
                events.append(dict(t='confirm', id=b['id'], **karta))
                czeka = 'potwierdzenie'
            else:
                wyniki.append({'type': 'tool_result', 'tool_use_id': b['id'], 'content': 'Nieznane narzędzie', 'is_error': True})
        if czeka or out.get('stop_reason') != 'tool_use' or not wyniki:
            break
        messages.append({'role': 'user', 'content': wyniki})
    return messages, stan, events, czeka
