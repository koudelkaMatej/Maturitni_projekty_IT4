"""
testy.py - Automatizované testy hry City Rescue Simulator
Autor: [tvoje jméno]

Testuje klíčové herní mechaniky pomocí modulu unittest:
  1. Párování jednotka ↔ událost (správná/špatná jednotka, timeout)
  2. Výpočet skóre:
       +1 bod  — správná jednotka vyřeší událost
       -1 bod  — událost vyprší bez vyřešení (minimum skóre je 0)

Testy používají zjednodušené třídy FakeJednotka a FakeUdalost,
které simulují herní logiku bez Pygame vykreslování.
"""

import unittest
import sys
import os

# Přidáme nadřazený adresář do sys.path, aby šly importovat herní třídy
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


# ============================================================
# POMOCNÉ TŘÍDY (zjednodušené verze bez Pygame vykreslení)
# ============================================================

class FakeJednotka:
    """
    Zjednodušená jednotka pro testování — bez Pygame vykreslení.

    Simuluje pohyb a doražení na místo pomocí atributu cil:
      cil != None → jednotka je na cestě
      cil == None → jednotka dorazila nebo je na základně
    """

    def __init__(self, jmeno):
        """
        Args:
            jmeno (str): Typ jednotky ('Policie' | 'Hasiči' | 'Sanitka')
        """
        self.jmeno        = jmeno
        self.cil          = None    # None = na místě / na základně
        self.start_pozice = [0, 0]
        self.pozice       = [0, 0]

    def jede_na(self, pozice):
        """Nastaví cíl — simuluje vyslání jednotky."""
        self.cil = pozice

    def doraz_na_misto(self):
        """Simuluje dojezd na místo — vynuluje cíl."""
        self.cil = None


class FakeUdalost:
    """
    Zjednodušená událost pro testování — obsahuje logiku párování
    bez Pygame animací a vykreslování.

    Skórování (řeší volající kód nebo SpravceHry):
      aktivni = False + prirazena_jednotka != None → správně vyřešeno → +1 bod
      aktivni = False + prirazena_jednotka == None → timeout            → -1 bod
    """

    # Mapování typu události na požadovaný typ jednotky
    TYPY = {
        "pozar":     "Hasiči",
        "nehoda":    "Sanitka",
        "kradez":    "Policie",
        "povoden":   "Hasiči",
        "vybuch":    "Hasiči",
        "prepadeni": "Policie",
    }

    def __init__(self, typ):
        """
        Args:
            typ (str): Typ události (klíč v TYPY)
        """
        self.typ                 = typ
        self.vyzadovana_jednotka = self.TYPY[typ]
        self.aktivni             = True
        self.prirazena_jednotka  = None
        self.timer               = 0
        self.casovy_limit        = 1800   # výchozí: 30 sekund při 60 FPS

    def prirad_jednotku(self, jednotka):
        """Přiřadí jednotku k řešení této události."""
        self.prirazena_jednotka = jednotka

    def update(self):
        """
        Jeden krok herní logiky.

        Pokud přiřazená jednotka dorazila (cil == None):
          - správný typ → událost vyřešena (aktivni = False)
          - špatný typ  → odmítni jednotku, čekej dál

        Po překročení casovy_limit → timeout (aktivni = False).
        """
        if self.prirazena_jednotka and not self.prirazena_jednotka.cil:
            if self.prirazena_jednotka.jmeno == self.vyzadovana_jednotka:
                # Správná jednotka — vyřešeno
                self.aktivni = False
            else:
                # Špatná jednotka — odmítni
                self.prirazena_jednotka = None

        self.timer += 1
        if self.timer >= self.casovy_limit:
            # Timeout — událost vyprší
            self.aktivni = False


# ============================================================
# TEST 1 — Párování jednotka ↔ událost
# ============================================================

class TestParovaniJednotekAUdalosti(unittest.TestCase):
    """
    Testy logiky párování správné jednotky se správnou událostí.

    Každá událost vyžaduje konkrétní typ jednotky.
    Správná jednotka ji vyřeší, špatná se vrátí bez výsledku.
    """

    def test_spravna_jednotka_vyresi_udalost(self):
        """Hasiči dorazí na požár → událost se vyřeší (aktivni = False)."""
        udalost  = FakeUdalost("pozar")
        jednotka = FakeJednotka("Hasiči")

        udalost.prirad_jednotku(jednotka)
        jednotka.doraz_na_misto()
        udalost.update()

        self.assertFalse(udalost.aktivni,
            "Událost měla být vyřešena, ale stále je aktivní.")

    def test_spatna_jednotka_nevyresi_udalost(self):
        """Policie na požár → událost NENÍ vyřešena a zůstává aktivní."""
        udalost  = FakeUdalost("pozar")
        jednotka = FakeJednotka("Policie")

        udalost.prirad_jednotku(jednotka)
        jednotka.doraz_na_misto()
        udalost.update()

        self.assertTrue(udalost.aktivni,
            "Událost neměla být vyřešena špatnou jednotkou.")

    def test_spatna_jednotka_je_odmitnuta(self):
        """Po odmítnutí špatné jednotky je prirazena_jednotka None."""
        udalost  = FakeUdalost("pozar")
        jednotka = FakeJednotka("Sanitka")

        udalost.prirad_jednotku(jednotka)
        jednotka.doraz_na_misto()
        udalost.update()

        self.assertIsNone(udalost.prirazena_jednotka,
            "Špatná jednotka měla být odmítnuta (prirazena_jednotka == None).")

    def test_sanitka_vyresi_nehodu(self):
        """Sanitka vyřeší nehodu správně."""
        udalost  = FakeUdalost("nehoda")
        jednotka = FakeJednotka("Sanitka")

        udalost.prirad_jednotku(jednotka)
        jednotka.doraz_na_misto()
        udalost.update()

        self.assertFalse(udalost.aktivni)

    def test_policie_vyresi_kradez(self):
        """Policie vyřeší krádež správně."""
        udalost  = FakeUdalost("kradez")
        jednotka = FakeJednotka("Policie")

        udalost.prirad_jednotku(jednotka)
        jednotka.doraz_na_misto()
        udalost.update()

        self.assertFalse(udalost.aktivni)

    def test_hasici_vyresi_povoden(self):
        """Hasiči vyřeší povodeň správně."""
        udalost  = FakeUdalost("povoden")
        jednotka = FakeJednotka("Hasiči")

        udalost.prirad_jednotku(jednotka)
        jednotka.doraz_na_misto()
        udalost.update()

        self.assertFalse(udalost.aktivni)

    def test_policie_nevyresi_nehodu(self):
        """Policie nemůže vyřešit nehodu — to je práce sanitky."""
        udalost  = FakeUdalost("nehoda")
        jednotka = FakeJednotka("Policie")

        udalost.prirad_jednotku(jednotka)
        jednotka.doraz_na_misto()
        udalost.update()

        self.assertTrue(udalost.aktivni)
        self.assertIsNone(udalost.prirazena_jednotka,
            "Špatná jednotka měla být odmítnuta.")

    def test_udalost_na_ceste_je_stale_aktivni(self):
        """Dokud jednotka nedorazila (cil != None), událost zůstává aktivní."""
        udalost  = FakeUdalost("pozar")
        jednotka = FakeJednotka("Hasiči")

        jednotka.jede_na((500, 300))    # jednotka jede, ale nedorazila
        udalost.prirad_jednotku(jednotka)
        udalost.update()

        self.assertTrue(udalost.aktivni,
            "Událost neměla být vyřešena — jednotka ještě nedorazila.")

    def test_timeout_udalosti(self):
        """Událost bez přiřazené jednotky expiruje po časovém limitu."""
        udalost = FakeUdalost("kradez")
        udalost.casovy_limit = 5   # krátký limit pro test

        for _ in range(6):
            udalost.update()

        self.assertFalse(udalost.aktivni,
            "Událost měla expirovat po vypršení časového limitu.")

    def test_vsechny_typy_maji_spravnou_jednotku(self):
        """Všechny typy událostí mají přiřazenou správnou jednotku."""
        ocekavane = {
            "pozar":     "Hasiči",
            "nehoda":    "Sanitka",
            "kradez":    "Policie",
            "povoden":   "Hasiči",
            "vybuch":    "Hasiči",
            "prepadeni": "Policie",
        }
        for typ, jednotka in ocekavane.items():
            u = FakeUdalost(typ)
            self.assertEqual(u.vyzadovana_jednotka, jednotka,
                f"Událost '{typ}' měla vyžadovat '{jednotka}', "
                f"ne '{u.vyzadovana_jednotka}'.")


# ============================================================
# TEST 2 — Výpočet skóre
# ============================================================

class TestVypocetSkore(unittest.TestCase):
    """
    Testy logiky počítání skóre.

    Pravidla (shodná se SpravceHry):
      +1 bod  — správná jednotka vyřeší událost
      -1 bod  — událost vyprší bez vyřešení (timeout)
      minimum skóre = 0 (skóre neklesne pod nulu)
    """

    def test_jedno_spravne_vyreseni(self):
        """Jedna správně vyřešená událost = 1 bod."""
        skore    = 0
        udalost  = FakeUdalost("pozar")
        jednotka = FakeJednotka("Hasiči")

        udalost.prirad_jednotku(jednotka)
        jednotka.doraz_na_misto()
        udalost.update()

        if not udalost.aktivni and udalost.prirazena_jednotka is not None:
            skore += 1

        self.assertEqual(skore, 1)

    def test_spatna_jednotka_nedava_bod(self):
        """Špatná jednotka na událost = 0 bodů (událost zůstane aktivní)."""
        skore    = 0
        udalost  = FakeUdalost("pozar")
        jednotka = FakeJednotka("Policie")   # špatná!

        udalost.prirad_jednotku(jednotka)
        jednotka.doraz_na_misto()
        udalost.update()

        # Událost stále aktivní → žádná změna skóre
        if not udalost.aktivni and udalost.prirazena_jednotka is not None:
            skore += 1

        self.assertEqual(skore, 0, "Špatná jednotka nesmí dát bod.")

    def test_skore_roste_po_kazdem_vyreseni(self):
        """Tři správně vyřešené události = 3 body."""
        skore    = 0
        kombinace = [
            ("pozar",  "Hasiči"),
            ("nehoda", "Sanitka"),
            ("kradez", "Policie"),
        ]
        for typ_u, typ_j in kombinace:
            u = FakeUdalost(typ_u)
            j = FakeJednotka(typ_j)
            u.prirad_jednotku(j)
            j.doraz_na_misto()
            u.update()
            if not u.aktivni and u.prirazena_jednotka is not None:
                skore += 1

        self.assertEqual(skore, 3)

    def test_expiraci_odebere_bod(self):
        """Expirovaná událost (timeout) odebere 1 bod."""
        skore   = 1   # začínáme s 1 bodem
        udalost = FakeUdalost("pozar")
        udalost.casovy_limit = 1   # okamžitý timeout

        udalost.update()   # timer = 1 >= limit = 1 → expiruje

        self.assertFalse(udalost.aktivni, "Událost měla expirovat.")

        # Timeout: prirazena_jednotka je None → odečti bod
        if not udalost.aktivni and udalost.prirazena_jednotka is None:
            skore = max(0, skore - 1)

        self.assertEqual(skore, 0, "Timeout měl odebrat 1 bod.")

    def test_skore_neklesne_pod_nulu(self):
        """Skóre neklesne pod 0 ani při timeoutu."""
        skore   = 0   # začínáme s 0 body
        udalost = FakeUdalost("pozar")
        udalost.casovy_limit = 1

        udalost.update()

        if not udalost.aktivni and udalost.prirazena_jednotka is None:
            skore = max(0, skore - 1)   # max(0, ...) zabrání záporným hodnotám

        self.assertEqual(skore, 0, "Skóre nesmí klesnout pod 0.")

    def test_skore_nula_bez_akce(self):
        """Bez jakékoli akce je skóre 0."""
        skore = 0
        self.assertEqual(skore, 0)

    def test_vice_udalosti_ruzne_vysledky(self):
        """Smíšená hra: 2 správné (+2), 1 špatná (0), 1 timeout (-1) → skóre = 1."""
        skore = 0

        # 1. Správná — +1
        u1 = FakeUdalost("pozar")
        j1 = FakeJednotka("Hasiči")
        u1.prirad_jednotku(j1); j1.doraz_na_misto(); u1.update()
        if not u1.aktivni and u1.prirazena_jednotka is not None:
            skore += 1

        # 2. Správná — +1
        u2 = FakeUdalost("nehoda")
        j2 = FakeJednotka("Sanitka")
        u2.prirad_jednotku(j2); j2.doraz_na_misto(); u2.update()
        if not u2.aktivni and u2.prirazena_jednotka is not None:
            skore += 1

        # 3. Špatná jednotka — událost zůstane aktivní → 0
        u3 = FakeUdalost("kradez")
        j3 = FakeJednotka("Hasiči")   # špatná!
        u3.prirad_jednotku(j3); j3.doraz_na_misto(); u3.update()
        if not u3.aktivni and u3.prirazena_jednotka is not None:
            skore += 1

        # 4. Timeout — -1
        u4 = FakeUdalost("prepadeni")
        u4.casovy_limit = 1
        u4.update()
        if not u4.aktivni and u4.prirazena_jednotka is None:
            skore = max(0, skore - 1)

        # Výsledek: 2 + 0 - 1 = 1
        self.assertEqual(skore, 1, f"Očekáváno skóre 1, dostali jsme {skore}.")


# ============================================================
# SPUŠTĚNÍ TESTŮ
# ============================================================

if __name__ == "__main__":
    print("=" * 60)
    print("TESTY — City Rescue Simulator")
    print("=" * 60)

    loader = unittest.TestLoader()
    suite  = unittest.TestSuite()

    suite.addTests(loader.loadTestsFromTestCase(TestParovaniJednotekAUdalosti))
    suite.addTests(loader.loadTestsFromTestCase(TestVypocetSkore))

    runner  = unittest.TextTestRunner(verbosity=2)
    vysledek = runner.run(suite)

    print()
    print(f"Úspěšné: {vysledek.testsRun - len(vysledek.failures) - len(vysledek.errors)}"
          f" / {vysledek.testsRun}")

    sys.exit(0 if vysledek.wasSuccessful() else 1)
