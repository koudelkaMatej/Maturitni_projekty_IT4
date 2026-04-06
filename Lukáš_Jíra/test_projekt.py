import os
import tempfile
import unittest

import databaze
import web


PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))


class TestDatabaze(unittest.TestCase):
    def setUp(self):
        self.original_db = databaze.SOUBOR
        fd, self.test_db = tempfile.mkstemp(prefix="test_skore_", suffix=".db", dir=PROJECT_DIR)
        os.close(fd)
        databaze.SOUBOR = self.test_db
        databaze.vytvorit_tabulku()

    def tearDown(self):
        databaze.SOUBOR = self.original_db
        if os.path.exists(self.test_db):
            os.remove(self.test_db)

    def test_registrace_a_prihlaseni_funguji(self):
        self.assertTrue(databaze.registrace("tester", "heslo123"))
        self.assertTrue(databaze.prihlaseni("tester", "heslo123"))
        self.assertFalse(databaze.prihlaseni("tester", "spatneheslo"))

    def test_duplicitni_registrace_je_zamitnuta(self):
        self.assertTrue(databaze.registrace("duplicitni", "abc"))
        self.assertFalse(databaze.registrace("duplicitni", "abc"))

    def test_vysledek_lze_ulozit_jen_existujicimu_uctu(self):
        self.assertFalse(databaze.pridat_vysledek("neznamy", 7))
        databaze.registrace("hrac", "tajne")
        self.assertTrue(databaze.pridat_vysledek("hrac", 7))

    def test_zebricek_vraci_jen_nejlepsi_vysledek_na_ucet(self):
        databaze.registrace("lukas", "a")
        databaze.registrace("anna", "b")
        databaze.pridat_vysledek("lukas", 3)
        databaze.pridat_vysledek("lukas", 8)
        databaze.pridat_vysledek("lukas", 5)
        databaze.pridat_vysledek("anna", 6)

        data = databaze.ziskej_data()

        self.assertEqual(len(data), 2)
        self.assertEqual(data[0][0], "lukas")
        self.assertEqual(data[0][1], 8)
        self.assertEqual(data[1][0], "anna")
        self.assertEqual(data[1][1], 6)

    def test_smazani_uctu_odstrani_i_vysledky(self):
        databaze.registrace("mazany", "heslo")
        databaze.pridat_vysledek("mazany", 4)
        self.assertTrue(databaze.smazat_ucet("mazany"))
        self.assertFalse(databaze.prihlaseni("mazany", "heslo"))
        self.assertEqual(databaze.ziskej_data(), [])


class TestWeb(unittest.TestCase):
    def setUp(self):
        self.original_db = databaze.SOUBOR
        fd, self.test_db = tempfile.mkstemp(prefix="test_web_", suffix=".db", dir=PROJECT_DIR)
        os.close(fd)
        databaze.SOUBOR = self.test_db
        databaze.vytvorit_tabulku()
        web.app.config["TESTING"] = True
        self.client = web.app.test_client()

    def tearDown(self):
        databaze.SOUBOR = self.original_db
        if os.path.exists(self.test_db):
            os.remove(self.test_db)

    def test_hlavni_stranka_se_nacte(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("Flappy Bird - web projektu", response.get_data(as_text=True))

    def test_registrace_uzivatele_pres_web(self):
        response = self.client.post(
            "/",
            data={"action": "register", "jmeno": "webtester", "heslo": "1234"},
            follow_redirects=True,
        )

        html = response.get_data(as_text=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn("Registrace uspesna", html)
        self.assertIn("Prihlasen: webtester", html)

    def test_admin_prihlaseni_funguje(self):
        response = self.client.post(
            "/admin",
            data={
                "action": "admin_login",
                "admin_name": web.ADMIN_USERNAME,
                "admin_pass": web.ADMIN_PASSWORD,
            },
            follow_redirects=True,
        )

        html = response.get_data(as_text=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn("Admin panel", html)
        self.assertIn("Uzivatel", html)


if __name__ == "__main__":
    unittest.main(verbosity=2)
