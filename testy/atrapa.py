# -*- coding: utf-8 -*-
"""Atrapa Cloudflare Workers AI: lista modeli konta i Chat Completions, bez sieci i bez zużycia neuronów."""
import json, threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


class AtrapaCloudflare:
    def __init__(self, modele=(), kod=200, tresc='Gotowe.', lista=True, opakuj=False):
        self.modele = list(modele)
        self.kod = kod
        self.tresc = tresc
        self.lista = lista
        self.opakuj = opakuj
        self.zadania = []
        self.naglowki = []
        self.sciezki = []
        atrapa = self

        class H(BaseHTTPRequestHandler):
            def log_message(self, *a):
                pass

            def _json(self, obj, kod=200):
                b = json.dumps(obj).encode()
                self.send_response(kod)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Content-Length', str(len(b)))
                self.end_headers()
                self.wfile.write(b)

            def do_GET(self):
                atrapa.sciezki.append(self.path)
                if atrapa.kod != 200:
                    return self._json({'success': False, 'errors': [{'message': 'blad atrapy'}]}, atrapa.kod)
                if '/ai/models/search' in self.path:
                    if not atrapa.lista:
                        return self._json({'success': False, 'errors': [{'message': 'brak'}]}, 500)
                    return self._json({'success': True, 'result': [{'name': m} for m in atrapa.modele]})
                self._json({'success': True, 'result': []})

            def do_POST(self):
                dl = int(self.headers.get('Content-Length') or 0)
                atrapa.zadania.append(json.loads(self.rfile.read(dl) or b'{}'))
                atrapa.naglowki.append(dict(self.headers))
                atrapa.sciezki.append(self.path)
                if atrapa.kod != 200:
                    tresc = 'neurons limit' if atrapa.kod == 429 else 'blad atrapy'
                    return self._json({'success': False, 'errors': [{'message': tresc}]}, atrapa.kod)
                odp = {'model': atrapa.zadania[-1].get('model'),
                       'choices': [{'message': {'role': 'assistant', 'content': atrapa.tresc},
                                    'finish_reason': 'stop'}],
                       'usage': {'prompt_tokens': 10, 'completion_tokens': 3}}
                self._json({'result': odp} if atrapa.opakuj else odp)

        self.serwer = ThreadingHTTPServer(('127.0.0.1', 0), H)
        self.port = self.serwer.server_address[1]
        self.watek = threading.Thread(target=self.serwer.serve_forever, daemon=True)
        self.watek.start()

    @property
    def baza(self):
        return 'http://127.0.0.1:%d/client/v4/accounts/test/ai/v1' % self.port

    @property
    def api(self):
        return 'http://127.0.0.1:%d/client/v4' % self.port

    def ostatni(self):
        return self.zadania[-1] if self.zadania else {}

    def klucz(self):
        return self.naglowki[-1].get('Authorization') if self.naglowki else None

    def zamknij(self):
        self.serwer.shutdown()
        self.serwer.server_close()
