import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'serwer'))
import vercel_glue


class handler(vercel_glue.Handler):
    """GET /api/modele — katalog darmowych modeli Workers AI i wybrany model."""
    def do_GET(self):
        vercel_glue.respond(self, vercel_glue.katalog_modeli)
