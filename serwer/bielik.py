# -*- coding: utf-8 -*-
"""Jedno miejsce konfiguracji modelu: Bielik (SpeakLeash) w Ollamie albo w API zgodnym z OpenAI.

Wszystkie ustawienia pochodzą ze zmiennych środowiskowych (plik .env). Domyślne wartości są dobrane
pod Bielika 11B v3.0 Instruct: niska temperatura i ograniczony wybór tokenów stabilizują wywoływanie
narzędzi, a powtórzeniowa kara trzyma odpowiedzi w jednym języku.

Sprawdzenie konfiguracji: python3 serwer/bielik.py
Pobranie modelu:          python3 serwer/bielik.py --pobierz
"""
import json, os, sys, urllib.request


NAZWA = 'SpeakLeash/bielik-11b-v3.0-instruct:Q4_K_M'
WARIANTY = (
    ('SpeakLeash/bielik-11b-v3.0-instruct:Q4_K_M', '6,7 GB, ok. 12 GB RAM, domyślny'),
    ('SpeakLeash/bielik-11b-v3.0-instruct:Q8_0', '12 GB, ok. 20 GB RAM, lepsza jakość'),
    ('SpeakLeash/bielik-minitron-7B-v3.0-instruct:Q4_K_M', 'mniejszy, szybszy na 8 GB RAM'),
    ('SpeakLeash/bielik-4.5b-v3.0-instruct:Q8_0', 'najmniejszy, do testów'),
)
RODZINA = 'bielik'
STOP = ('<|endoftext|>', '<|im_start|>', '<|im_end|>', '<|start_header_id|>', '<|end_header_id|>')


def _env(klucz, domyslna=''):
    wartosc = os.environ.get(klucz)
    return wartosc if wartosc not in (None, '') else domyslna


def _liczba(klucz, domyslna, typ):
    try:
        return typ(_env(klucz, domyslna))
    except (TypeError, ValueError):
        return typ(domyslna)


def _flaga(klucz, domyslna=True):
    return _env(klucz, '1' if domyslna else '0').strip().lower() not in ('0', 'false', 'nie', 'no')


PROVIDER = _env('PROVIDER', 'ollama').strip().lower()
OLLAMA_URL = _env('OLLAMA_URL', 'http://127.0.0.1:11434').rstrip('/')
ZGODNY_BAZA = _env('OPENAI_BASE_URL', OLLAMA_URL + '/v1').rstrip('/')
MODEL = _env('MODEL', NAZWA)
MODEL_API_KEY = _env('MODEL_API_KEY')
TYLKO_BIELIK = _flaga('BIELIK_TYLKO', True)

NUM_CTX = _liczba('MODEL_NUM_CTX', 32768, int)
MAX_TOKENS = _liczba('MODEL_MAX_TOKENS', 1200, int)
TIMEOUT = _liczba('MODEL_TIMEOUT', 180, int)
KEEP_ALIVE = _env('MODEL_KEEP_ALIVE', '30m')
TEMPERATURE = _liczba('MODEL_TEMPERATURE', 0.1, float)
TOP_P = _liczba('MODEL_TOP_P', 0.95, float)
TOP_K = _liczba('MODEL_TOP_K', 40, int)
MIN_P = _liczba('MODEL_MIN_P', 0.05, float)
REPEAT_PENALTY = _liczba('MODEL_REPEAT_PENALTY', 1.1, float)
REPEAT_LAST_N = _liczba('MODEL_REPEAT_LAST_N', 256, int)
SEED = _liczba('MODEL_SEED', -1, int)
ROZGRZEWANIE = _flaga('MODEL_WARMUP', True)

OPCJE = dict(temperature=TEMPERATURE, top_p=TOP_P, top_k=TOP_K, min_p=MIN_P, repeat_penalty=REPEAT_PENALTY,
             repeat_last_n=REPEAT_LAST_N, num_ctx=NUM_CTX, num_predict=MAX_TOKENS, seed=SEED)

OPCJE_ZGODNE = dict(temperature=TEMPERATURE, top_p=TOP_P, max_tokens=MAX_TOKENS)


def adres():
    return ZGODNY_BAZA if PROVIDER == 'zgodny' else OLLAMA_URL


def czy_bielik(nazwa=None):
    """Czy nazwa modelu wskazuje na rodzinę Bielik (dowolny wariant i kwantyzacja)."""
    return RODZINA in (nazwa or MODEL).lower()


def komunikat_modelu(nazwa=None):
    """Pusty tekst, gdy modelem jest Bielik; inaczej zdanie wyjaśniające, co ustawić."""
    nazwa = nazwa or MODEL
    if czy_bielik(nazwa):
        return ''
    if TYLKO_BIELIK:
        return ('Model %s nie jest Bielikiem, a ten projekt obsługuje wyłącznie Bielika. '
                'Ustaw MODEL=%s albo pozwól na inne modele lokalne: BIELIK_TYLKO=0.' % (nazwa, NAZWA))
    return 'Model %s nie jest Bielikiem. Projekt jest strojony pod Bielika, więc odpowiedzi mogą się różnić.' % nazwa


def wymagaj_bielika():
    """Rzuca ValueError, gdy wybrano inny model przy włączonym BIELIK_TYLKO."""
    if TYLKO_BIELIK and not czy_bielik():
        raise ValueError(komunikat_modelu())


def dostepne():
    """Nazwy modeli widocznych w lokalnym serwerze; pusty słownik, gdy serwer nie odpowiada."""
    try:
        adres_ = OLLAMA_URL + '/api/tags' if PROVIDER != 'zgodny' else ZGODNY_BAZA + '/models'
        with urllib.request.urlopen(adres_, timeout=4) as r:
            odp = json.loads(r.read())
        lista = odp.get('models') if PROVIDER != 'zgodny' else odp.get('data')
        klucz = 'name' if PROVIDER != 'zgodny' else 'id'
        return [m.get(klucz) for m in (lista or []) if m.get(klucz)]
    except Exception:
        return []


def pobierz(nazwa=None):
    """Pobiera model przez Ollamę i wypisuje postęp. Zwraca True po sukcesie."""
    nazwa = nazwa or MODEL
    if PROVIDER == 'zgodny':
        print('PROVIDER=zgodny: model pobiera serwer, który go udostępnia.')
        return False
    dane = json.dumps({'model': nazwa, 'stream': True}).encode()
    req = urllib.request.Request(OLLAMA_URL + '/api/pull', data=dane, headers={'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(req, timeout=3600) as r:
            for linia in r:
                try:
                    s = json.loads(linia)
                except ValueError:
                    continue
                if s.get('error'):
                    print('Błąd: %s' % s['error'])
                    return False
                if s.get('status'):
                    print('\r%s %s' % (s['status'], s.get('completed', '')) if s.get('total') else '\r%s' % s['status'], end='', flush=True)
        print()
        return True
    except Exception as e:
        print('Nie mogę pobrać modelu z %s: %s. Sprawdź, czy Ollama działa (ollama serve).' % (OLLAMA_URL, e))
        return False


def opis():
    """Krótki raport konfiguracji dla człowieka (i dla dziennika serwera)."""
    gotowe = dostepne()
    model_ok = any(n == MODEL or n.split(':')[0] == MODEL.split(':')[0] for n in gotowe)
    linie = [
        'Model:      %s' % MODEL,
        'Dostawca:   %s (%s)' % (PROVIDER, adres()),
        'Bielik:     %s' % ('tak' if czy_bielik() else 'nie'),
        'Tylko Bielik: %s' % ('tak' if TYLKO_BIELIK else 'nie'),
        'Kontekst:   %d tokenów, odpowiedź do %d tokenów' % (NUM_CTX, MAX_TOKENS),
        'Próbkowanie: temperatura %.2f, top_p %.2f, top_k %d, min_p %.2f, kara powtórzeń %.2f' % (
            TEMPERATURE, TOP_P, TOP_K, MIN_P, REPEAT_PENALTY),
        'Pobrany:    %s' % ('tak' if model_ok else 'nie'),
    ]
    if not model_ok:
        linie.append('Pobierz:    python3 serwer/bielik.py --pobierz')
    ostrzezenie = komunikat_modelu()
    if ostrzezenie:
        linie.append('Uwaga:      %s' % ostrzezenie)
    if gotowe:
        linie.append('Widoczne modele: %s' % ', '.join(gotowe))
    return '\n'.join(linie)


if __name__ == '__main__':
    if '--pobierz' in sys.argv:
        sys.exit(0 if pobierz() else 1)
    print(opis())
