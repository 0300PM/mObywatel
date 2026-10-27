# -*- coding: utf-8 -*-
"""Wersje językowe interfejsu: słowniki z katalogu serwer/i18n i rejestr tekstów, których jeszcze nie ma.

Interfejs tłumaczą gotowe słowniki. Tłumaczenia maszynowego nie ma: tekst bez tłumaczenia zostaje po polsku
i trafia do rejestru _zrodla.json. Asystent (Bielik) rozmawia po polsku, więc nie tłumaczymy rozmowy w locie.
Teksty są szablonami: liczby, daty i godziny zamieniamy na {0}, {1}…, więc „Za 11 dni, 29.10” i „Za 12 dni, 30.10”
to jeden wpis."""
import json, os, re, threading

# kod: (nazwa po angielsku, nazwa własna)
JEZYKI = {
    'pl': ('Polish', 'Polski'), 'en': ('English', 'English'), 'de': ('German', 'Deutsch'), 'fr': ('French', 'Français'),
    'es': ('Spanish', 'Español'), 'it': ('Italian', 'Italiano'), 'pt': ('Portuguese (European)', 'Português'),
    'nl': ('Dutch', 'Nederlands'), 'cs': ('Czech', 'Čeština'), 'sk': ('Slovak', 'Slovenčina'), 'sl': ('Slovenian', 'Slovenščina'),
    'hu': ('Hungarian', 'Magyar'), 'ro': ('Romanian', 'Română'), 'el': ('Greek', 'Ελληνικά'), 'sv': ('Swedish', 'Svenska'),
    'uk': ('Ukrainian', 'Українська'),
}
KAT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'i18n')
os.makedirs(KAT, exist_ok=True)
NUM = re.compile(r'\d+(?:[.,:/]\d+)*')
LITERA = re.compile(r'[^\W\d_]', re.U)
SKROTY = re.compile(r'\b(OC|PESEL|ZUS|KDR|UFG)\b')
_lock = threading.Lock()
_cache = {}
_mtime = {}


def szablon(s):
    """Zamienia liczby na {0}, {1}…, żeby jeden wpis obsłużył wiele wartości."""
    nums = []
    def rep(m):
        nums.append(m.group(0))
        return '{%d}' % (len(nums) - 1)
    return NUM.sub(rep, s), nums


def wypelnij(t, nums):
    return re.sub(r'\{(\d+)\}', lambda m: nums[int(m.group(1))] if int(m.group(1)) < len(nums) else m.group(0), t)


def do_tlumaczenia(s):
    return bool(s and s.strip() and (SKROTY.search(s) or (LITERA.search(s) and re.search(r'[a-ząćęłńóśźż]', s))))


def slownik(lang):
    """Słownik języka; doczytuje zmiany z dysku."""
    with _lock:
        p = os.path.join(KAT, lang + '.json')
        try:
            mt = os.path.getmtime(p)
        except OSError:
            mt = None
        if lang not in _cache or (mt and mt != _mtime.get(lang)):
            try:
                d = json.load(open(p, encoding='utf-8'))
                if lang in _cache:
                    d.update({k: v for k, v in _cache[lang].items() if k not in d})
                _cache[lang] = d
            except Exception:
                _cache.setdefault(lang, {})
            _mtime[lang] = mt
        return _cache[lang]


def zrodla():
    try:
        return set(json.load(open(os.path.join(KAT, '_zrodla.json'), encoding='utf-8')))
    except Exception:
        return set()


def _dodaj_zrodla(teksty):
    with _lock:
        z = zrodla()
        nowe = set(teksty)
        if nowe - z:
            json.dump(sorted(z | nowe), open(os.path.join(KAT, '_zrodla.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=0)


def przetlumacz(lang, teksty):
    """Zwraca {szablon: tłumaczenie} tylko ze słownika. Braki trafiają do rejestru _zrodla.json."""
    if lang not in JEZYKI or lang == 'pl':
        return {}
    teksty = [t for t in dict.fromkeys(teksty) if do_tlumaczenia(t) and len(t) <= 700]
    sl = slownik(lang)
    _dodaj_zrodla([t for t in teksty if t not in sl])
    return {t: sl[t] for t in teksty if t in sl}
