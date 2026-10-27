# -*- coding: utf-8 -*-
"""Serwer prototypu: pliki statyczne z frontend/dist + API agenta (darmowy model Cloudflare Workers AI)
i znaku mObywatela.

Uruchomienie: python3 serwer/server.py [port]   (domyślnie 8790)
Bez płatnych usług: rozmowę prowadzi darmowy model otwarty z Workers AI na dzienny limit neuronów,
a mowę obsługuje przeglądarka."""
import json, os, sys, time, threading, traceback
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import ustawienia


ENV_PLIK, ENV_KLUCZE = ustawienia.szukaj([ROOT_DIR, os.getcwd()])
import agent, katalog, model, tlumacz

ROOT = os.environ.get('MOCKUP') or os.path.join(os.path.dirname(HERE), 'frontend', 'dist')
LOG = os.environ.get('AGENT_LOG') or os.path.join(HERE, 'agent.log')
_lock = threading.Lock()

# --- znak mObywatela: każde urządzenie pokazuje zmieniający się żeton; kto go zeskanuje, przekazuje dane jego właścicielowi ---
ZN = {'devs': {}, 'skrz': {}, 'skan': {}}
ZN_TTL = 120
ZN_SWIEZY = 15


def log(x):
    x = dict(x, ts=time.strftime('%Y-%m-%d %H:%M:%S'))
    with _lock:
        with open(LOG, 'a', encoding='utf-8') as f:
            f.write(json.dumps(x, ensure_ascii=False) + '\n')


def zn_clean():
    t = time.time()
    for d in [d for d, v in ZN['devs'].items() if t - v['t'] > ZN_TTL]:
        ZN['devs'].pop(d, None)
        ZN['skrz'].pop(d, None)
        ZN['skan'].pop(d, None)


def zn_kto(tok, dev):
    now = time.time()
    for d, v in ZN['devs'].items():
        if d == dev or now - v['t'] > ZN_SWIEZY:
            continue
        if v['token'] == tok or (v.get('prev') == tok and now - v['tt'] < 60):
            return d, v
    return None, None


def zdrowie():
    stan = agent.stan_modelu()
    return dict(
        agent=bool(stan['ok']),
        provider=agent.DOSTAWCA,
        model=stan.get('model') or model.model(),
        modelGotowy=bool(stan['ok']),
        bielik=bool(stan.get('bielik', model.czy_bielik())),
        klucz=bool(stan.get('klucz')),
        konto=bool(stan.get('konto')),
        kontoOk=bool(model.KONTO_SPRAWDZONE),
        kluczRodzaj=model.rodzaj_klucza(),
        ostrzezenia=model.ostrzezenia(),
        config=ustawienia.zrodlo(ENV_PLIK, ENV_KLUCZE),
        glos=dict(stt='przegladarka', tts='przegladarka'),
        stt=True,
        tts=True,
        komunikat=stan.get('komunikat') or '',
    )


def katalog_modeli():
    """Co wolno uruchomić, co jest wybrane i co z tego jest naprawdę widoczne na koncie Cloudflare."""
    stan = agent.stan_modelu()
    nazwa = stan.get('model') or model.model()
    widoczne = stan.get('dostepne')
    pozycje = []
    for m in katalog.uporzadkuj(model.PREFERUJ):
        d = m.jako_dict()
        d['dostepny'] = widoczne is None or m.nazwa in widoczne
        d['wybrany'] = m.nazwa == nazwa
        pozycje.append(d)
    return dict(
        katalog=pozycje,
        dostawca=agent.DOSTAWCA,
        adres=model.adres(),
        konto=model.KONTO_USTAWIONE,
        kontoOk=model.KONTO_SPRAWDZONE,
        config=ustawienia.zrodlo(ENV_PLIK, ENV_KLUCZE),
        klucz=bool(model.KLUCZ_USTAWIONY),
        model=nazwa,
        bielik=bool(stan.get('bielik')),
        auto=model.AUTO,
        preferuj=model.PREFERUJ,
        okno=model.NUM_CTX,
        lista_znana=widoczne is not None,
        dostepne=widoczne or [],
        komunikat=stan.get('komunikat') or '',
    )


class H(SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=ROOT, **kw)

    def log_message(self, *a):
        pass

    def end_headers(self):
        if self.path.startswith('/api/'):
            self.send_header('Cache-Control', 'no-store')
        elif self.path.startswith('/assets/'):
            self.send_header('Cache-Control', 'public, max-age=31536000, immutable')
        else:
            self.send_header('Cache-Control', 'no-cache')
        super().end_headers()

    def js(self, obj, code=200):
        b = json.dumps(obj, ensure_ascii=False).encode()
        self.send_response(code)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(b)))
        self.send_header('Cache-Control', 'no-store')
        self.end_headers()
        self.wfile.write(b)

    def body(self):
        n = int(self.headers.get('Content-Length') or 0)
        return self.rfile.read(n) if n else b''

    def do_GET(self):
        try:
            return self.pobierz()
        except agent.BladAPI as e:
            log(dict(t='model_err', path=self.path, msg=str(e)))
            return self.js(dict(error=str(e)), 503)
        except (BrokenPipeError, ConnectionResetError):
            return None
        except Exception as e:
            log(dict(t='err', path=self.path, msg=str(e), tb=traceback.format_exc()[-800:]))
            return self.js(dict(error='Błąd serwera: %s' % e), 500)

    def pobierz(self):
        p = urlparse(self.path).path
        if p == '/api/health':
            return self.js(zdrowie())
        if p == '/api/modele':
            return self.js(katalog_modeli())
        if p == '/api/i18n':
            lang = (parse_qs(urlparse(self.path).query).get('lang') or ['pl'])[0]
            d = tlumacz.slownik(lang) if lang in tlumacz.JEZYKI and lang != 'pl' else {}
            return self.js(dict(lang=lang, t=d))
        if p == '/api/znak/kto':
            q = parse_qs(urlparse(self.path).query)
            try:
                tok = int((q.get('t') or ['-1'])[0])
            except ValueError:
                tok = -1
            dev = (q.get('dev') or [''])[0]
            with _lock:
                d, v = zn_kto(tok, dev)
                if d:
                    ZN['skan'][d] = time.time()
            log(dict(t='znak_kto', ok=bool(d), kind=v and v['kind'], cel=v and v.get('cel')))
            if not d:
                return self.js(dict(dev=None))
            return self.js(dict(dev=d, kind=v['kind'], kto=v.get('kto'), cel=v.get('cel'), zakres=v.get('zakres')))
        if p == '/v2' or p.startswith('/v2/'):
            self.send_response(301)
            self.send_header('Location', '/')
            self.end_headers()
            return
        if not os.path.exists(ROOT):
            return self.js(dict(error='brak zbudowanego frontendu: uruchom npm run build w katalogu frontend'), 503)
        if p == '/komputer':
            self.path = '/komputer.html'
        elif p == '/aplikacja' or p == '/aplikacja/':
            q = urlparse(self.path).query
            self.path = '/index.html' + ('?' + q if q else '')
        elif os.path.splitext(p)[1] == '' and not os.path.exists(os.path.join(ROOT, p.lstrip('/'))):
            q = urlparse(self.path).query
            self.path = '/index.html' + ('?' + q if q else '')
        return super().do_GET()

    def do_POST(self):
        p = urlparse(self.path).path
        try:
            if p == '/api/agent':
                return self.agent()
            if p == '/api/i18n/brak':
                raw = self.body()
                if len(raw) > 60000:
                    return self.js(dict(error='za duzo'), 413)
                req = json.loads(raw or b'{}')
                lang = req.get('lang')
                if lang not in tlumacz.JEZYKI or lang == 'pl':
                    return self.js(dict(t={}))
                teksty = [str(x)[:700] for x in (req.get('teksty') or [])][:150]
                d = tlumacz.przetlumacz(lang, teksty)
                log(dict(t='i18n', lang=lang, n=len(teksty), brak=len(teksty) - len(d)))
                return self.js(dict(t=d))
            if p == '/api/znak/beat':
                req = json.loads(self.body() or b'{}')
                dev = str(req.get('dev', ''))[:40]
                try:
                    tok = int(req.get('token')) & 0xffff
                except (TypeError, ValueError):
                    return self.js(dict(error='zly zeton'), 400)
                with _lock:
                    zn_clean()
                    now = time.time()
                    v = ZN['devs'].get(dev)
                    zajety = any(d != dev and now - w['t'] < ZN_SWIEZY and tok in (w['token'], w.get('prev')) for d, w in ZN['devs'].items())
                    if v is None:
                        v = ZN['devs'][dev] = dict(token=tok, prev=None, tt=now)
                    elif v['token'] != tok:
                        v['prev'], v['token'], v['tt'] = v['token'], tok, now
                    v.update(t=now, kind='web' if req.get('kind') == 'web' else 'telefon',
                             kto=str(req.get('kto') or '')[:80], cel=req.get('cel'), zakres=req.get('zakres'))
                    otrz = ZN['skrz'].pop(dev, [])
                    skanuje = now - ZN['skan'].get(dev, 0) < 45
                    if otrz:
                        ZN['skan'].pop(dev, None)
                return self.js(dict(otrzymane=otrz, skanuje=skanuje and not otrz, zmien=zajety))
            if p == '/api/znak/przekaz':
                raw = self.body()
                if len(raw) > 20000:
                    return self.js(dict(error='za duzo danych'), 413)
                req = json.loads(raw or b'{}')
                to = req.get('to')
                with _lock:
                    if to not in ZN['devs']:
                        return self.js(dict(ok=False, error='odbiorca niedostepny'), 404)
                    ZN['skrz'].setdefault(to, []).append(dict(ok=bool(req.get('ok')), dane=req.get('dane') if req.get('ok') else None, t=time.time()))
                    kind = ZN['devs'][to]['kind']
                log(dict(t='znak_przekaz', ok=bool(req.get('ok')), kind=kind))
                return self.js(dict(ok=True))
            return self.js(dict(error='nie ma takiego adresu'), 404)
        except agent.BladAPI as e:
            log(dict(t='model_err', path=p, msg=str(e)))
            return self.js(dict(error=str(e)), 503)
        except (BrokenPipeError, ConnectionResetError):
            return None
        except Exception as e:
            log(dict(t='err', path=p, msg=str(e), tb=traceback.format_exc()[-800:]))
            return self.js(dict(error='Błąd serwera: %s' % e), 500)

    def agent(self):
        """Jedno pytanie do asystenta. Błąd modelu kończy się komunikatem, nigdy przełączeniem na płatne API."""
        req = json.loads(self.body() or b'{}')
        t0 = time.time()
        user = req.get('messages', [])[-1] if req.get('messages') else None
        log(dict(t='req', osoba=req.get('osoba'), conv=req.get('conv'),
                 user=user.get('content') if user and isinstance(user.get('content'), str) else None,
                 confirm=req.get('confirm')))
        msgs, stan, events, czeka = agent.run(req.get('messages', []), req.get('stan'), req.get('confirm'),
                                              lambda x: log(dict(x, conv=req.get('conv'))),
                                              osoba=req.get('osoba'), jezyk=req.get('lang') or 'pl')
        log(dict(t='resp', conv=req.get('conv'), ms=int((time.time() - t0) * 1000), events=[e.get('t') for e in events], czeka=czeka))
        return self.js(dict(messages=msgs, stan=stan, events=events, czeka=czeka))


def start():
    port = int(sys.argv[1]) if len(sys.argv) > 1 else int(os.environ.get('PORT') or 8790)
    host = os.environ.get('HOST') or '127.0.0.1'
    if not os.path.exists(ROOT):
        print('brak katalogu %s: uruchom "npm run build" w katalogu frontend' % ROOT, flush=True)
    try:
        import wiedza
        threading.Thread(target=wiedza._wczytaj, daemon=True).start()
    except Exception as e:
        print('wiedza:', e, flush=True)
    srv = ThreadingHTTPServer((host, port), H)
    srv.daemon_threads = True
    print('mObywatel: http://%s:%d  (pliki: %s)' % ('127.0.0.1' if host in ('0.0.0.0', '::') else host, port, ROOT), flush=True)
    print('Konfiguracja: %s' % ustawienia.zrodlo(ENV_PLIK, ENV_KLUCZE), flush=True)
    print(model.opis(), flush=True)
    srv.serve_forever()


if __name__ == '__main__':
    start()
