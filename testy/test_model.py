# -*- coding: utf-8 -*-
"""Testy katalogu modeli i konfiguracji Cloudflare Workers AI.
Uruchomienie: python3 -m unittest discover testy -v"""
import importlib, os, sys, unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'serwer'))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import katalog
from atrapa import AtrapaCloudflare

ZMIENNE = ('CLOUDFLARE_ACCOUNT_ID', 'CLOUDFLARE_API_TOKEN', 'CF_API_TOKEN', 'MODEL_API_KEY',
           'CLOUDFLARE_AI_BASE', 'MODEL', 'MODEL_PREFERUJ', 'MODELE_DOWOLNE', 'MODEL_NUM_CTX', 'MODEL_SEED')

SZYBKI = '@cf/ibm-granite/granite-4.0-h-micro'
MOCNY = '@cf/openai/gpt-oss-120b'


def wczytaj(atrapa=None, **env):
    """Przeładowuje model.py i agent.py z podanym środowiskiem — moduły czytają .env przy imporcie."""
    for nazwa in ZMIENNE:
        os.environ.pop(nazwa, None)
    os.environ.update({k: str(v) for k, v in env.items()})
    import agent, katalog as kat, model
    importlib.reload(kat)
    importlib.reload(model)
    if atrapa is not None:
        model.API = atrapa.api
        model.CLOUDFLARE_AI_BASE_TEST = atrapa.baza
        os.environ['CLOUDFLARE_AI_BASE'] = atrapa.baza
        importlib.reload(model)
        model.API = atrapa.api
    importlib.reload(agent)
    return model, agent


def cisza(_):
    pass


class KatalogTest(unittest.TestCase):
    def test_katalog_jest_darmowy_i_z_narzedziami(self):
        self.assertEqual(len(katalog.KATALOG), 12)
        for model in katalog.KATALOG:
            self.assertTrue(model.darmowy, model.nazwa)
            self.assertTrue(model.narzedzia, model.nazwa)
            self.assertGreaterEqual(model.kontekst, 32768, model.nazwa)
            self.assertTrue(model.nazwa.startswith('@cf/'), model.nazwa)

    def test_modele_spoza_workers_ai_sa_odrzucane(self):
        for nazwa in ('gpt-4o', '@cf/meta/llama-2-7b-chat-int8', '@cf/qwen/qwq-32b',
                      'SpeakLeash/Bielik-11B-v3.0-Instruct', ''):
            self.assertFalse(katalog.czy_dozwolony(nazwa), nazwa)

    def test_kolejnosc_wyboru(self):
        self.assertEqual(katalog.uporzadkuj('auto')[0].nazwa, SZYBKI)
        predkosci = [m.tok_s for m in katalog.uporzadkuj('auto')]
        self.assertEqual(predkosci, sorted(predkosci, reverse=True))
        self.assertTrue(katalog.uporzadkuj('jakosc')[0].mocny)

    def test_wybierz_najszybszy_bez_listy_konta(self):
        self.assertEqual(katalog.wybierz(None, 'auto').nazwa, SZYBKI)

    def test_wybierz_tylko_z_listy_konta(self):
        self.assertEqual(katalog.wybierz([MOCNY, '@cf/zai-org/glm-4.7-flash'], 'auto').nazwa,
                         '@cf/zai-org/glm-4.7-flash')
        self.assertIsNone(katalog.wybierz(['@cf/meta/llama-3.2-1b-instruct'], 'auto'))

    def test_wybierz_szanuje_okno(self):
        self.assertIsNone(katalog.wybierz([SZYBKI], 'auto', okno=10 ** 7))


class ChatTest(unittest.TestCase):
    def setUp(self):
        self.cf = AtrapaCloudflare([SZYBKI, '@cf/openai/gpt-oss-20b'])
        self.model, self.agent = wczytaj(self.cf, CLOUDFLARE_ACCOUNT_ID='konto123',
                                         CLOUDFLARE_API_TOKEN='cf-token-123', MODEL='auto')

    def tearDown(self):
        os.environ.pop('CLOUDFLARE_AI_BASE', None)
        self.cf.zamknij()

    def test_token_i_opis_bez_wycieku(self):
        self.assertTrue(self.model.KLUCZ_USTAWIONY)
        self.assertTrue(self.model.KONTO_USTAWIONE)
        self.assertEqual(self.model.komunikat_modelu(), '')
        self.assertNotIn('cf-token-123', self.model.opis())

    def test_auto_wybiera_najszybszy_model_z_konta(self):
        self.assertEqual(self.model.model(), SZYBKI)

    def test_zadanie_ma_bearer_i_66_narzedzi(self):
        odp = self.agent.llm([{'role': 'user', 'content': 'Cześć'}], set(), cisza)
        self.assertTrue(odp['content'])
        self.assertEqual(self.cf.klucz(), 'Bearer cf-token-123')
        self.assertEqual(self.cf.ostatni().get('model'), SZYBKI)
        self.assertEqual(len(self.cf.ostatni()['tools']), 66)
        self.assertTrue(self.cf.sciezki[-1].endswith('/ai/v1/chat/completions'))

    def test_odpowiedz_opakowana_w_result(self):
        cf = AtrapaCloudflare([SZYBKI], opakuj=True)
        try:
            _model, agent = wczytaj(cf, CLOUDFLARE_ACCOUNT_ID='konto123',
                                    CLOUDFLARE_API_TOKEN='cf-token-123', MODEL='auto')
            odp = agent.llm([{'role': 'user', 'content': 'Cześć'}], set(), cisza)
            self.assertEqual(odp['content'][0]['text'], 'Gotowe.')
        finally:
            os.environ.pop('CLOUDFLARE_AI_BASE', None)
            cf.zamknij()

    def test_brak_listy_nie_blokuje_agenta(self):
        self.cf.lista = False
        model, agent = wczytaj(self.cf, CLOUDFLARE_ACCOUNT_ID='konto123',
                               CLOUDFLARE_API_TOKEN='cf-token-123', MODEL='auto')
        self.assertIsNone(model.dostepne())
        self.assertEqual(model.model(), SZYBKI)
        self.assertEqual(model.komunikat_modelu(), '')
        self.assertTrue(agent.llm([{'role': 'user', 'content': 'Cześć'}], set(), cisza)['content'])


class BrakKonfiguracjiTest(unittest.TestCase):
    def setUp(self):
        self.cf = AtrapaCloudflare([SZYBKI])

    def tearDown(self):
        os.environ.pop('CLOUDFLARE_AI_BASE', None)
        self.cf.zamknij()

    def test_brak_konta(self):
        model, agent = wczytaj(self.cf, CLOUDFLARE_API_TOKEN='cf-token-123', MODEL='auto')
        self.assertIn('CLOUDFLARE_ACCOUNT_ID', model.komunikat_modelu())
        with self.assertRaises(agent.BladAPI):
            agent.llm([{'role': 'user', 'content': 'Cześć'}], set(), cisza)
        self.assertEqual(self.cf.zadania, [])

    def test_brak_tokenu(self):
        model, agent = wczytaj(self.cf, CLOUDFLARE_ACCOUNT_ID='konto123', MODEL='auto')
        self.assertFalse(model.KLUCZ_USTAWIONY)
        self.assertIn('CLOUDFLARE_API_TOKEN', model.komunikat_modelu())
        with self.assertRaises(agent.BladAPI):
            agent.llm([{'role': 'user', 'content': 'Cześć'}], set(), cisza)
        self.assertEqual(self.cf.zadania, [])


class BladCloudflareTest(unittest.TestCase):
    def sprawdz(self, kod, fragment):
        cf = AtrapaCloudflare([SZYBKI], kod=kod)
        try:
            _model, agent = wczytaj(cf, CLOUDFLARE_ACCOUNT_ID='konto123',
                                    CLOUDFLARE_API_TOKEN='cf-token-123', MODEL='auto')
            with self.assertRaises(agent.BladAPI) as e:
                agent.llm([{'role': 'user', 'content': 'Cześć'}], set(), cisza)
            self.assertIn(fragment, str(e.exception))
        finally:
            os.environ.pop('CLOUDFLARE_AI_BASE', None)
            cf.zamknij()

    def test_zly_token(self):
        self.sprawdz(401, 'odrzucił')

    def test_brak_neuronow(self):
        self.sprawdz(429, 'neuronów')

    def test_model_niedostepny(self):
        self.sprawdz(404, 'nie udostępnia modelu')


class ModelSpozaKataloguTest(unittest.TestCase):
    def setUp(self):
        self.cf = AtrapaCloudflare([SZYBKI])
        self.model, self.agent = wczytaj(self.cf, CLOUDFLARE_ACCOUNT_ID='konto123',
                                         CLOUDFLARE_API_TOKEN='cf-token-123', MODEL='gpt-4o')

    def tearDown(self):
        os.environ.pop('CLOUDFLARE_AI_BASE', None)
        self.cf.zamknij()

    def test_model_platny_nie_wychodzi_na_zewnatrz(self):
        self.assertIn('nie jest na liście dozwolonych', self.model.komunikat_modelu())
        with self.assertRaises(self.agent.BladAPI):
            self.agent.llm([{'role': 'user', 'content': 'Cześć'}], set(), cisza)
        self.assertEqual(self.cf.zadania, [])

    def test_dowolny_model_po_fladze(self):
        model, _agent = wczytaj(self.cf, CLOUDFLARE_ACCOUNT_ID='konto123',
                                CLOUDFLARE_API_TOKEN='cf-token-123', MODEL='gpt-4o', MODELE_DOWOLNE=1)
        self.assertEqual(model.komunikat_modelu(), '')


if __name__ == '__main__':
    unittest.main()
