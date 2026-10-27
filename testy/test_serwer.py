# -*- coding: utf-8 -*-
"""Testy całego serwera: odpowiedzi API, odporność na błędy i wczytywanie .env.
Uruchomienie: python3 -m unittest discover testy -v"""
import json, os, socket, subprocess, sys, tempfile, time, unittest, urllib.error, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'serwer'))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from atrapa import AtrapaCloudflare

KONTO = '0123456789abcdef0123456789abcdef'
TOKEN = 'cf-token-' + 'x' * 31
WOLNE = ('CLOUDFLARE_ACCOUNT_ID', 'CLOUDFLARE_API_TOKEN', 'CF_API_TOKEN', 'MODEL_API_KEY',
         'CLOUDFLARE_AI_BASE', 'MODEL', 'MODEL_PREFERUJ')


def wolny_port():
    with socket.socket() as s:
        s.bind(('127.0.0.1', 0))
        return s.getsockname()[1]


class SerwerTest(unittest.TestCase):
    atrapa = None
    katalog = False

    def start(self, env_extra=None, katalog=None):
        self.atrapa = AtrapaCloudflare(['@cf/openai/gpt-oss-20b', '@cf/ibm-granite/granite-4.0-h-micro'])
        env = {k: v for k, v in os.environ.items() if k not in WOLNE}
        env.update(PORT=str(wolny_port()), HOST='127.0.0.1', MODEL='auto',
                   CLOUDFLARE_ACCOUNT_ID=KONTO, CLOUDFLARE_API_TOKEN=TOKEN,
                   CLOUDFLARE_AI_BASE=self.atrapa.baza)
        env.update(env_extra or {})
        self.port = int(env['PORT'])
        self.proc = subprocess.Popen([sys.executable, os.path.join(ROOT, 'serwer', 'server.py')],
                                     cwd=katalog or ROOT, env=env,
                                     stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        self.czytaj('/api/health')

    def stop(self):
        self.proc.terminate()
        try:
            self.proc.wait(5)
        except subprocess.TimeoutExpired:
            self.proc.kill()
        if self.atrapa:
            self.atrapa.zamknij()

    def czytaj(self, sciezka, kod=200, jsonowo=True):
        for _ in range(80):
            try:
                tresc = urllib.request.urlopen('http://127.0.0.1:%d%s' % (self.port, sciezka),
                                               timeout=5).read()
                return json.loads(tresc) if jsonowo else tresc
            except urllib.error.HTTPError as e:
                if e.code == kod:
                    return json.loads(e.read() or b'{}') if jsonowo else b''
                raise
            except (urllib.error.URLError, ConnectionError):
                time.sleep(0.15)
        raise AssertionError('serwer nie odpowiedział na %s' % sciezka)


class ZdrowieTest(SerwerTest):
    def setUp(self):
        self.start()

    def tearDown(self):
        self.stop()

    def test_health_i_modele(self):
        stan = self.czytaj('/api/health')
        self.assertTrue(stan['agent'])
        self.assertEqual(stan['provider'], 'cloudflare')
        self.assertTrue(stan['klucz'])
        self.assertTrue(stan['konto'])
        self.assertEqual(stan['komunikat'], '')
        self.assertIn('config', stan)
        self.assertEqual(stan['ostrzezenia'], [])
        katalog = self.czytaj('/api/modele')
        self.assertEqual(len(katalog['katalog']), 12)
        self.assertTrue(katalog['lista_znana'])
        self.assertNotIn(TOKEN, json.dumps(katalog))
        self.assertNotIn(KONTO, json.dumps(katalog))

    def test_serwer_przezywa_blad_i_dalej_odpowiada(self):
        self.czytaj('/api/nie-ma-takiego', kod=404, jsonowo=False)
        self.czytaj('/api/modele')
        self.atrapa.kod = 401
        self.assertTrue(self.czytaj('/api/health')['agent'])
        self.atrapa.kod = 200
        stan = self.czytaj('/api/health')
        self.assertTrue(stan['agent'])
        self.assertEqual(stan['komunikat'], '')


class EnvZPlikuTest(SerwerTest):
    def setUp(self):
        self.katalog = tempfile.mkdtemp()
        with open(os.path.join(self.katalog, '.env'), 'w', encoding='utf-8', newline='') as f:
            f.write('\ufeffexport CLOUDFLARE_ACCOUNT_ID=%s   # konto\r\n' % KONTO)
            f.write('CLOUDFLARE_API_TOKEN=„%s”\r\n' % TOKEN)
            f.write('MODEL=auto\r\n')
        self.start({'CLOUDFLARE_ACCOUNT_ID': '', 'CLOUDFLARE_API_TOKEN': ''}, katalog=self.katalog)

    def tearDown(self):
        self.stop()

    def test_plik_env_z_nietypowym_zapisem(self):
        stan = self.czytaj('/api/health')
        self.assertTrue(stan['konto'], stan['config'])
        self.assertTrue(stan['klucz'], stan['config'])
        self.assertTrue(stan['kontoOk'])
        self.assertIn('.env', stan['config'])
        self.assertEqual(stan['ostrzezenia'], [])
        self.assertEqual(stan['komunikat'], '')


class ZleDaneTest(SerwerTest):
    def test_zamienione_miejscami_konto_i_token(self):
        self.start({'CLOUDFLARE_ACCOUNT_ID': TOKEN, 'CLOUDFLARE_API_TOKEN': KONTO})
        stan = self.czytaj('/api/health')
        self.assertTrue(stan['klucz'])
        self.assertTrue(any('32 znaki hex' in tekst for tekst in stan['ostrzezenia']), stan['ostrzezenia'])
        self.assertTrue(any('32 znaki hex' in tekst for tekst in stan['ostrzezenia']), stan['ostrzezenia'])

    def tearDown(self):
        self.stop()


if __name__ == '__main__':
    unittest.main()
