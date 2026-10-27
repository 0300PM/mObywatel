import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'serwer'))
import vercel_glue


class handler(vercel_glue.Handler):
    """GET /api/health — czy model i konto Cloudflare są gotowe."""
    def do_GET(self):
        vercel_glue.respond(self, vercel_glue.zdrowie)
