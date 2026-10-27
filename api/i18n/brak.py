import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'serwer'))
import vercel_glue


class handler(vercel_glue.Handler):
    """POST /api/i18n/brak — tłumaczenia ze słownika i rejestr brakujących tekstów."""
    def do_POST(self):
        vercel_glue.respond(self, lambda: vercel_glue.i18n_brak(self))
