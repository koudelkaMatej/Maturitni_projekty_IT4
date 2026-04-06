"""
scoreboard.py - Žebříček nejlepších hráčů
Autor: [tvoje jméno]

Stahuje a zobrazuje top 10 hráčů ze školního serveru.
Načítání probíhá v samostatném vlákně (threading) aby
obrazovka nezamrzla při pomalém připojení.

Parsování: HTML odpověď z zebricek.php se parsuje regexem —
hledáme obsah <td> tagů a ze čtyřsloupcové tabulky
(Pořadí, Hráč, Body, Datum) skládáme záznamy.
"""

import pygame
from classes.mys import get_pos
import threading
import requests
import urllib3
import re
from config import *

# Potlač SSL varování pro školní server bez důvěryhodného certifikátu
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class Scoreboard:
    """
    Obrazovka žebříčku — načítá a zobrazuje top 10 ze serveru.

    Stavy načítání:
      nacitani = True   — vlákno stahuje data
      chyba    = str    — chybová zpráva (server nedostupný apod.)
      skore_data = list — úspěšně načtené záznamy
    """

    # URL skriptu zebříčku na školním serveru
    URL = "http://xeon.spskladno.cz/~tkadleco/zebricek.php"

    def __init__(self, screen):
        """
        Inicializace žebříčku.

        Args:
            screen: Pygame surface
        """
        self.screen = screen

        # Fonty pro různé části UI
        self.font_nadpis  = pygame.font.Font(None, 64)
        self.font_tabulka = pygame.font.Font(None, 38)
        self.font_maly    = pygame.font.Font(None, 28)

        # Stav načítání
        self.skore_data = []      # seznam záznamů [{hrac, body, datum}, ...]
        self.nacitani   = False   # True pokud probíhá stahování
        self.chyba      = None    # chybová zpráva nebo None

        # Tlačítka — sdílená draw i handle_event
        self.tl_zpet    = pygame.Rect(20,          20, 150, 50)
        self.tl_obnovit = pygame.Rect(WIDTH - 200, 20, 170, 50)

    def nacti_skore(self):
        """
        Spustí načítání žebříčku v samostatném vlákně.

        Vynuluje předchozí data a chybu před novým načtením.
        """
        self.nacitani   = True
        self.chyba      = None
        self.skore_data = []
        t = threading.Thread(target=self._nacti_task, daemon=True)
        t.start()

    def _nacti_task(self):
        """
        Stáhne stránku zebricek.php a parsuje top 10 záznamů.

        Probíhá v samostatném vlákně. Parsování:
          - HTTP GET na self.URL
          - Regex najde všechny <td>...</td> hodnoty
          - Tabulka má 4 sloupce: Pořadí, Hráč, Body, Datum
          - Skáčeme po 4 a bereme sloupce 1, 2, 3 (index, hráč, body, datum)
        """
        try:
            r          = requests.get(self.URL, timeout=5, verify=False)
            r.encoding = "utf-8"

            # Najdi všechny buňky tabulky
            bunky = re.findall(r"<td[^>]*>\s*(.*?)\s*</td>", r.text, re.DOTALL)

            # Tabulka má 4 sloupce → skáčeme po 4
            for i in range(0, len(bunky) - 3, 4):
                hrac  = bunky[i + 1].strip()
                body  = bunky[i + 2].strip()
                datum = bunky[i + 3].strip()[:10]   # pouze YYYY-MM-DD

                # Přidej záznam jen pokud obsahuje jméno a číselné body
                if hrac and body.lstrip("-").isdigit():
                    self.skore_data.append({
                        "hrac":  hrac,
                        "body":  body,
                        "datum": datum,
                    })
                    if len(self.skore_data) >= 10:
                        break   # top 10 stačí
        except Exception as e:
            self.chyba = f"Chyba: {e}"
        finally:
            self.nacitani = False

    def handle_event(self, udalost):
        """
        Zpracování vstupů (ESC, kliknutí na tlačítka).

        Returns:
            'menu' — návrat do menu
            None   — žádná akce
        """
        if udalost.type == pygame.KEYDOWN and udalost.key == pygame.K_ESCAPE:
            return "menu"
        if udalost.type == pygame.MOUSEBUTTONDOWN and udalost.button == 1:
            poz = get_pos()
            if self.tl_zpet.collidepoint(poz):
                return "menu"
            if self.tl_obnovit.collidepoint(poz):
                self.nacti_skore()   # znovu stáhne data ze serveru
        return None

    def draw(self):
        """
        Vykreslení žebříčku.

        Zobrazí:
          - Stav načítání ("Načítám data...")
          - Chybovou zprávu s tipy pro opravu
          - Tabulku top 10 s medailovým zvýrazněním prvních 3 míst
        """
        self.screen.fill((18, 18, 28))

        # Nadpis stránky
        nadpis = self.font_nadpis.render("Nejlepší záchranáři", True, ZLUTA)
        self.screen.blit(nadpis, (WIDTH // 2 - nadpis.get_width() // 2, 18))

        # Tlačítka Zpět a Obnovit s hover efektem
        myska = get_pos()
        for rect, text in [
            (self.tl_zpet,    "<  Zpět"),
            (self.tl_obnovit, "Obnovit"),
        ]:
            hover = rect.collidepoint(myska)
            barva = (70, 70, 130) if hover else (45, 45, 90)
            pygame.draw.rect(self.screen, barva,            rect, border_radius=6)
            pygame.draw.rect(self.screen, (100, 100, 160),  rect, 1, border_radius=6)
            t = self.font_maly.render(text, True, BILA)
            self.screen.blit(t, (rect.centerx - t.get_width() // 2,
                                 rect.centery - t.get_height() // 2))

        # --- Stavy načítání ---
        if self.nacitani:
            t = self.font_tabulka.render("Načítám data...", True, BILA)
            self.screen.blit(t, (WIDTH // 2 - t.get_width() // 2, HEIGHT // 2))
            return

        if self.chyba:
            # Chybová zpráva rozložená na více řádků
            radky_chyby = [
                "Nepodařilo se načíst žebříček.",
                "",
                "Možné příčiny:",
                "  1. Soubor zebricek.php není nahrán na server",
                "  2. Adresa serveru je nedostupná",
                "  3. Chybí připojení k internetu",
                "",
                "Jak opravit: nahraj zebricek.php do",
                "  public_html/ na xeon.spskladno.cz",
            ]
            y_err = HEIGHT // 2 - 120
            for radek in radky_chyby:
                if radek.startswith("Nepodařilo"):
                    barva_r = CERVENA
                elif radek.startswith("Možné") or radek.startswith("Jak"):
                    barva_r = ZLUTA
                else:
                    barva_r = (180, 180, 180)
                if radek:
                    t = self.font_maly.render(radek, True, barva_r)
                    self.screen.blit(t, (WIDTH // 2 - t.get_width() // 2, y_err))
                y_err += 30
            return

        if not self.skore_data:
            t = self.font_tabulka.render("Zatím žádná skóre.", True, (120, 120, 140))
            self.screen.blit(t, (WIDTH // 2 - t.get_width() // 2, HEIGHT // 2))
            return

        # --- Tabulka výsledků ---
        y   = 90
        SL  = [70, 150, 450, 700]   # X pozice sloupců: #, Jméno, Skóre, Datum
        hl  = ["#", "Jméno", "Skóre", "Datum"]
        hlb = [ZLUTA, BILA, BILA, (140, 140, 140)]

        # Záhlaví tabulky
        pygame.draw.rect(self.screen, (35, 35, 55),
                         (50, y - 6, WIDTH - 100, 42), border_radius=6)
        for hx, txt, barva in zip(SL, hl, hlb):
            t = self.font_tabulka.render(txt, True, barva)
            self.screen.blit(t, (hx, y))
        y += 50

        # Barvy pro medailová místa (zlato, stříbro, bronz)
        BARVY_PORADI = {1: (255, 215, 0), 2: (192, 192, 192), 3: (205, 127, 50)}

        # Řádky tabulky — každý druhý tmavší (zebra efekt)
        for i, zaz in enumerate(self.skore_data, 1):
            if i % 2 == 0:
                pygame.draw.rect(self.screen, (28, 28, 44),
                                 (50, y - 5, WIDTH - 100, 40), border_radius=4)

            bp       = BARVY_PORADI.get(i, BILA)
            hodnoty  = [str(i), zaz["hrac"], zaz["body"], zaz["datum"]]
            barvy_r  = [bp, BILA, ZLUTA, (130, 130, 150)]
            for hx, val, barva in zip(SL, hodnoty, barvy_r):
                t = self.font_tabulka.render(val, True, barva)
                self.screen.blit(t, (hx, y))
            y += 44
