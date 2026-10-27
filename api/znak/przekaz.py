import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'serwer'))
import vercel_glue


class handler(vercel_glue.Handler):
    """POST /api/znak/przekaz — przekazanie danych do urządzenia pokazującego znak."""
    def do_POST(self):
        vercel_glue.respond(self, lambda: vercel_glue.znak_przekaz(self))
