import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'serwer'))
import vercel_glue


class handler(vercel_glue.Handler):
    """POST /api/agent — jedno pytanie do asystenta (model z Cloudflare Workers AI)."""
    def do_POST(self):
        vercel_glue.respond(self, lambda: vercel_glue.agent_run(self))
