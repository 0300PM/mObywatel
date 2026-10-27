import os, sys
from urllib.parse import urlparse, parse_qs

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'serwer'))
import vercel_glue


class handler(vercel_glue.Handler):
    """GET /api/znak/kto?t=token&dev=urzadzenie — kto pokazuje dany żeton znaku."""
    def do_GET(self):
        q = parse_qs(urlparse(self.path).query)
        try:
            tok = int((q.get('t') or ['-1'])[0])
        except ValueError:
            tok = -1
        dev = (q.get('dev') or [''])[0]
        vercel_glue.respond(self, lambda: vercel_glue.znak_kto(tok, dev))
