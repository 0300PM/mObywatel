import os, sys
from urllib.parse import urlparse, parse_qs

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'serwer'))
import vercel_glue


class handler(vercel_glue.Handler):
    """GET /api/i18n?lang=xx — słownik interfejsu w danym języku."""
    def do_GET(self):
        q = parse_qs(urlparse(self.path).query)
        lang = (q.get('lang') or ['pl'])[0]
        vercel_glue.respond(self, lambda: vercel_glue.i18n_slownik(lang))
