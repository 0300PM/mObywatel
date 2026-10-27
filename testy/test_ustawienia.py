# -*- coding: utf-8 -*-
"""Testy wczytywania pliku .env: warianty zapisu, które psują typowe parsery.
Uruchomienie: python3 -m unittest discover testy -v"""
import importlib, os, sys, tempfile, unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'serwer'))

import ustawienia

KLUCZE = ('CLOUDFLARE_ACCOUNT_ID', 'CLOUDFLARE_API_TOKEN', 'TEST_ZWYKLY', 'TEST_CUDZYSLOW',
          'TEST_KOMENTARZ', 'TEST_DWUKROPEK', 'TEST_PUSTY')


class ParsowanieTest(unittest.TestCase):
    def setUp(self):
        self.zapas = {k: os.environ.get(k) for k in KLUCZE}
        for k in KLUCZE:
            os.environ.pop(k, None)
        self.katalog = tempfile.mkdtemp()

    def tearDown(self):
        for k, v in self.zapas.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v

    def zapisz(self, tresc, nazwa='.env'):
        sciezka = os.path.join(self.katalog, nazwa)
        with open(sciezka, 'w', encoding='utf-8', newline='') as f:
            f.write(tresc)
        return sciezka

    def test_zwykly_zapis(self):
        ustawienia.wczytaj(self.zapisz('TEST_ZWYKLY=wartosc\n'))
        self.assertEqual(os.environ['TEST_ZWYKLY'], 'wartosc')

    def test_export_i_bom_i_crlf(self):
        ustawienia.wczytaj(self.zapisz('\ufeffexport TEST_ZWYKLY=wartosc\r\n'))
        self.assertEqual(os.environ['TEST_ZWYKLY'], 'wartosc')

    def test_cudzyslowy_proste_i_typograficzne(self):
        ustawienia.wczytaj(self.zapisz('TEST_CUDZYSLOW="a b"\nTEST_ZWYKLY=„c d”\n'))
        self.assertEqual(os.environ['TEST_CUDZYSLOW'], 'a b')
        self.assertEqual(os.environ['TEST_ZWYKLY'], 'c d')

    def test_krzyzyk_w_cudzyslowie_zostaje(self):
        ustawienia.wczytaj(self.zapisz('TEST_CUDZYSLOW="a#b"\n'))
        self.assertEqual(os.environ['TEST_CUDZYSLOW'], 'a#b')

    def test_komentarz_na_koncu_wiersza(self):
        ustawienia.wczytaj(self.zapisz('TEST_KOMENTARZ=wartosc  # komentarz\n'))
        self.assertEqual(os.environ['TEST_KOMENTARZ'], 'wartosc')

    def test_spacje_wokol_znaku_rowna(self):
        ustawienia.wczytaj(self.zapisz('TEST_ZWYKLY =  wartosc  \n'))
        self.assertEqual(os.environ['TEST_ZWYKLY'], 'wartosc')

    def test_dwukropek_zamiast_rowna(self):
        ustawienia.wczytaj(self.zapisz('TEST_DWUKROPEK: wartosc\n'))
        self.assertEqual(os.environ['TEST_DWUKROPEK'], 'wartosc')

    def test_pusta_wartosc_nie_nadpisuje_srodowiska(self):
        os.environ['TEST_PUSTY'] = 'ze-srodowiska'
        ustawienia.wczytaj(self.zapisz('TEST_PUSTY=\n'))
        self.assertEqual(os.environ['TEST_PUSTY'], 'ze-srodowiska')

    def test_srodowisko_ma_pierwszenstwo(self):
        os.environ['TEST_ZWYKLY'] = 'ze-srodowiska'
        klucze = ustawienia.wczytaj(self.zapisz('TEST_ZWYKLY=z-pliku\nTEST_KOMENTARZ=nowy\n'))
        self.assertEqual(os.environ['TEST_ZWYKLY'], 'ze-srodowiska')
        self.assertEqual(klucze, ['TEST_KOMENTARZ'])

    def test_szukaj_pierwszego_pliku(self):
        self.zapisz('CLOUDFLARE_ACCOUNT_ID=%s\n' % ('a' * 32))
        pusty = tempfile.mkdtemp()
        sciezka, klucze = ustawienia.szukaj([pusty, self.katalog])
        self.assertEqual(sciezka, os.path.join(self.katalog, '.env'))
        self.assertEqual(klucze, ['CLOUDFLARE_ACCOUNT_ID'])
        self.assertEqual(os.environ['CLOUDFLARE_ACCOUNT_ID'], 'a' * 32)

    def test_brak_pliku_nie_rzuca(self):
        sciezka, klucze = ustawienia.szukaj([os.path.join(self.katalog, 'nie-ma')])
        self.assertEqual((sciezka, klucze), ('', []))
        self.assertIn('brak pliku', ustawienia.zrodlo('', []))

    def test_zrodlo_opisuje_co_wczytano(self):
        sciezka = self.zapisz('TEST_ZWYKLY=wartosc\n')
        klucze = ustawienia.wczytaj(sciezka)
        opis = ustawienia.zrodlo(sciezka, klucze)
        self.assertIn('TEST_ZWYKLY', opis)
        self.assertNotIn('wartosc', opis)


class KonfiguracjaModeluTest(unittest.TestCase):
    """Komunikaty muszą nazywać prawdziwą przyczynę, a nie „ustaw zmienną”, gdy zmienna już jest."""

    def setUp(self):
        self.zapas = {k: os.environ.get(k) for k in KLUCZE}
        for k in KLUCZE:
            os.environ.pop(k, None)

    def tearDown(self):
        for k, v in self.zapas.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v

    def wczytaj(self, konto, token):
        os.environ['CLOUDFLARE_ACCOUNT_ID'] = konto
        os.environ['CLOUDFLARE_API_TOKEN'] = token
        import model
        importlib.reload(model)
        return model

    def test_poprawne_konto_i_token(self):
        model = self.wczytaj('a' * 32, 'x' * 40)
        self.assertTrue(model.KONTO_POPRAWNE)
        self.assertEqual(model.rodzaj_klucza(), 'ok')
        self.assertEqual(model.komunikat_modelu('@cf/openai/gpt-oss-20b'), '')

    def test_konto_w_zlym_formacie_to_ostrzezenie(self):
        model = self.wczytaj('moje-konto', 'x' * 40)
        self.assertFalse(model.KONTO_POPRAWNE)
        self.assertEqual(model.komunikat_modelu('@cf/openai/gpt-oss-20b'), '')
        self.assertIn('32 znaki hex', ' '.join(model.ostrzezenia()))

    def test_baza_wlasna_nie_blokuje(self):
        os.environ['CLOUDFLARE_AI_BASE'] = 'http://127.0.0.1:1/client/v4/accounts/test/ai/v1'
        model = self.wczytaj('test', 'x' * 40)
        self.assertFalse(model.KONTO_POPRAWNE)
        self.assertTrue(model.KONTO_SPRAWDZONE)
        self.assertEqual(model.komunikat_modelu('@cf/openai/gpt-oss-20b'), '')
        os.environ.pop('CLOUDFLARE_AI_BASE', None)

    def test_globalny_klucz_jest_nazywany_po_imieniu(self):
        model = self.wczytaj('a' * 32, 'b' * 37)
        self.assertEqual(model.rodzaj_klucza(), 'globalny')
        self.assertIn('Global API Key', model.komunikat_modelu())

    def test_krotki_token_to_ostrzezenie(self):
        model = self.wczytaj('a' * 32, 'skrot')
        self.assertEqual(model.rodzaj_klucza(), 'krotki')
        self.assertIn('obcięty', ' '.join(model.ostrzezenia()))

    def test_raport_nie_pokazuje_calego_konta(self):
        model = self.wczytaj('0123456789abcdef0123456789abcdef', 'x' * 40)
        raport = model.opis()
        self.assertNotIn('0123456789abcdef0123456789abcdef', raport)
        self.assertIn('32 znaki, ok', raport)


if __name__ == '__main__':
    unittest.main()
