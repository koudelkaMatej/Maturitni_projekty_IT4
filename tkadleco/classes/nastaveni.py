"""
nastaveni.py - Obrazovka nastavení hry
Autor: [tvoje jméno]

Umožňuje změnit obtížnost a rozlišení okna.
FPS je pevně nastaveno na 60 a nelze měnit.

handle_event() vrací:
  'ulozit' — uložit nastavení a zpět do menu
  'zpet'   — zahodit změny a zpět do menu
  None     — žádná akce
"""

import pygame
from classes.mys import get_pos
from config import *

# Barvy odznaků obtížnosti
BARVY_OBTIZNOSTI = {
    "Lehká":   (50,  200, 80),    # zelená = snadné
    "Střední": (240, 180, 30),    # žlutá = střední
    "Těžká":   (210, 40,  40),    # červená = těžké
}

# Popisky obtížností zobrazené pod odznakem
POPIS_OBTIZNOSTI = {
    "Lehká":   "Události každých 5 sekund",
    "Střední": "Události každých 3 sekundy",
    "Těžká":   "Události každých 1,5 sekundy",
}


class Nastaveni:
    """
    Obrazovka nastavení — obtížnost a rozlišení.

    Obtížnost a rozlišení se mění šipkami (< a >).
    Po kliknutí na Uložit se nastavení zapíše a předá main.py.
    Zpět zahodí změny a vrátí do menu.
    """

    OBTIZNOSTI = ["Lehká", "Střední", "Těžká"]

    # Y souřadnice řádků nastavení
    _RADKY = {
        "obtiznost": 240,
        "rozliseni": 400,
    }
    _X_LABEL = 90    # X pozice popisků (vlevo)
    _X_CTL   = 600   # X pozice ovládacích prvků (vpravo)

    def __init__(self, screen):
        """
        Inicializace nastavení.

        Args:
            screen: Pygame surface
        """
        self.screen = screen

        # Aktuální indexy výběru (odkazují do seznamů OBTIZNOSTI a MOZNOSTI_ROZLISENI)
        self.index_obtiznosti = 1   # výchozí: "Střední"
        self.index_rozliseni  = INDEX_ROZLISENI

        # Veřejné atributy čtené main.py po kliknutí na Uložit
        self.obtiznost = self.OBTIZNOSTI[self.index_obtiznosti]
        self.rozliseni = MOZNOSTI_ROZLISENI[self.index_rozliseni]

        # Fonty
        self.font_nadpis  = pygame.font.Font(None, 64)
        self.font_label   = pygame.font.Font(None, 38)
        self.font_hodnota = pygame.font.Font(None, 38)
        self.font_maly    = pygame.font.Font(None, 26)

        # Tlačítka Uložit a Zpět — definovaná jednou, sdílená draw i handle_event
        self._tl_ulozit = pygame.Rect(WIDTH // 2 + 40,  HEIGHT - 80, 210, 54)
        self._tl_zpet   = pygame.Rect(WIDTH // 2 - 250, HEIGHT - 80, 210, 54)

        # Obdélníky šipek pro každé nastavení
        self._sipky: dict = {}
        self._build_sipky()

    def _build_sipky(self):
        """
        Vytvoří Recty pro šipky (< a >) u každého nastavení.

        Levá šipka je vlevo od středové hodnoty,
        pravá šipka vpravo od ní.
        """
        for klic in ("obtiznost", "rozliseni"):
            y  = self._RADKY[klic]
            cx = self._X_CTL
            # Levá šipka (mínus)
            self._sipky[f"{klic}_minus"] = pygame.Rect(cx - 140, y - 20, 44, 40)
            # Pravá šipka (plus)
            self._sipky[f"{klic}_plus"]  = pygame.Rect(cx +  96, y - 20, 44, 40)

    # ------------------------------------------------------------------ #

    def handle_event(self, udalost):
        """
        Zpracování vstupů od uživatele.

        Returns:
            'ulozit' — uložit změny a vrátit do menu
            'zpet'   — zahodit změny a vrátit do menu
            None     — žádná akce
        """
        # ESC = zahodit změny
        if udalost.type == pygame.KEYDOWN and udalost.key == pygame.K_ESCAPE:
            return "zpet"

        if udalost.type == pygame.MOUSEBUTTONDOWN and udalost.button == 1:
            poz = get_pos()

            # Tlačítko Uložit — uloží nastavení do veřejných atributů
            if self._tl_ulozit.collidepoint(poz):
                self._uloz()
                return "ulozit"

            # Tlačítko Zpět — vrátí bez uložení
            if self._tl_zpet.collidepoint(poz):
                return "zpet"

            # Šipky pro výběr obtížnosti a rozlišení
            for klic, rect in self._sipky.items():
                if rect.collidepoint(poz):
                    self._klik_sipka(klic)
                    return

        return None

    def _klik_sipka(self, klic):
        """
        Změní aktuální index obtížnosti nebo rozlišení o ±1 (cyklicky).

        Args:
            klic (str): Klíč šipky (např. 'obtiznost_plus', 'rozliseni_minus')
        """
        if klic == "obtiznost_plus":
            self.index_obtiznosti = (self.index_obtiznosti + 1) % len(self.OBTIZNOSTI)
        elif klic == "obtiznost_minus":
            self.index_obtiznosti = (self.index_obtiznosti - 1) % len(self.OBTIZNOSTI)
        elif klic == "rozliseni_plus":
            self.index_rozliseni = (self.index_rozliseni + 1) % len(MOZNOSTI_ROZLISENI)
        elif klic == "rozliseni_minus":
            self.index_rozliseni = (self.index_rozliseni - 1) % len(MOZNOSTI_ROZLISENI)

    def _uloz(self):
        """
        Uloží aktuálně zvolené hodnoty do veřejných atributů.

        Tyto atributy čte main.py po kliknutí na Uložit
        (self.obtiznost a self.rozliseni).
        """
        self.obtiznost = self.OBTIZNOSTI[self.index_obtiznosti]
        self.rozliseni = MOZNOSTI_ROZLISENI[self.index_rozliseni]

    # ------------------------------------------------------------------ #

    def draw(self):
        """Vykreslení celé obrazovky nastavení."""
        self.screen.fill((18, 18, 28))

        # Tmavý zaoblený panel jako pozadí nastavení
        panel = pygame.Rect(60, 110, WIDTH - 120, HEIGHT - 200)
        pygame.draw.rect(self.screen, (28, 28, 44), panel, border_radius=18)
        pygame.draw.rect(self.screen, (55, 55, 100), panel, 2, border_radius=18)

        # Nadpis stránky
        n = self.font_nadpis.render("Nastavení", True, BILA)
        self.screen.blit(n, (WIDTH // 2 - n.get_width() // 2, 45))

        # Řádky nastavení
        self._draw_obtiznost()
        self._draw_sipkovy_radek("rozliseni", "Rozlišení",
            f"{MOZNOSTI_ROZLISENI[self.index_rozliseni][0]} × {MOZNOSTI_ROZLISENI[self.index_rozliseni][1]}")

        # Info o pevném FPS
        fps_info = self.font_maly.render("FPS: 60 (pevně nastaveno)", True, (80, 80, 110))
        self.screen.blit(fps_info, (self._X_LABEL, self._RADKY["rozliseni"] + 55))

        # Tlačítka Uložit a Zpět
        self._draw_tlacitka()

    def _draw_label(self, y, text):
        """
        Vykreslí šedý popisek řádku vlevo.

        Args:
            y (int):    Y souřadnice středu řádku
            text (str): Text popisku
        """
        t = self.font_label.render(text, True, (165, 165, 195))
        self.screen.blit(t, (self._X_LABEL, y - t.get_height() // 2))

    def _draw_oddelovac(self, y, offset=30):
        """
        Vykreslí vodorovnou oddělovací čáru pod řádkem.

        Args:
            y (int):      Y souřadnice řádku
            offset (int): Posun čáry pod střed řádku
        """
        pygame.draw.line(self.screen, (45, 45, 70),
                         (80, y + offset), (WIDTH - 80, y + offset), 1)

    def _draw_sipkovy_radek(self, klic, label, hodnota_str):
        """
        Vykreslí řádek s šipkami (< hodnota >) pro výběr rozlišení.

        Args:
            klic (str):        Klíč v self._sipky (např. 'rozliseni')
            label (str):       Popisek vlevo
            hodnota_str (str): Aktuálně zvolená hodnota jako text
        """
        y  = self._RADKY[klic]
        cx = self._X_CTL
        myska = get_pos()
        self._draw_label(y, label)

        # Šipky < a >
        for smer in ("minus", "plus"):
            rect  = self._sipky[f"{klic}_{smer}"]
            sym   = "<" if smer == "minus" else ">"
            hover = rect.collidepoint(myska)
            pygame.draw.rect(self.screen, (70, 70, 120) if hover else (42, 42, 80),
                             rect, border_radius=6)
            pygame.draw.rect(self.screen, (100, 100, 160), rect, 1, border_radius=6)
            s = self.font_hodnota.render(sym, True, BILA)
            self.screen.blit(s, (rect.centerx - s.get_width() // 2,
                                 rect.centery - s.get_height() // 2))

        # Hodnota uprostřed šipek
        val = self.font_hodnota.render(hodnota_str, True, ZLUTA)
        self.screen.blit(val, (cx - val.get_width() // 2, y - val.get_height() // 2))
        self._draw_oddelovac(y)

    def _draw_obtiznost(self):
        """
        Vykreslí řádek obtížnosti se šipkami a barevným odznakem.

        Odznaky mají barvy dle BARVY_OBTIZNOSTI a pod nimi je popis intervalu.
        """
        y  = self._RADKY["obtiznost"]
        cx = self._X_CTL
        myska = get_pos()
        self._draw_label(y, "Obtížnost")

        # Šipky < a >
        for smer in ("minus", "plus"):
            rect  = self._sipky[f"obtiznost_{smer}"]
            sym   = "<" if smer == "minus" else ">"
            hover = rect.collidepoint(myska)
            pygame.draw.rect(self.screen, (70, 70, 120) if hover else (42, 42, 80),
                             rect, border_radius=6)
            pygame.draw.rect(self.screen, (100, 100, 160), rect, 1, border_radius=6)
            s = self.font_hodnota.render(sym, True, BILA)
            self.screen.blit(s, (rect.centerx - s.get_width() // 2,
                                 rect.centery - s.get_height() // 2))

        # Barevný odznak s názvem obtížnosti
        nazev = self.OBTIZNOSTI[self.index_obtiznosti]
        barva = BARVY_OBTIZNOSTI[nazev]
        badge = pygame.Rect(cx - 80, y - 20, 160, 40)
        pygame.draw.rect(self.screen, barva, badge, border_radius=10)
        val = self.font_hodnota.render(nazev, True, BILA)
        self.screen.blit(val, (badge.centerx - val.get_width() // 2,
                               badge.centery - val.get_height() // 2))

        # Popis intervalu generování událostí
        popis = self.font_maly.render(POPIS_OBTIZNOSTI[nazev], True, (130, 130, 155))
        self.screen.blit(popis, (cx - popis.get_width() // 2, y + 26))
        self._draw_oddelovac(y, offset=44)

    def _draw_tlacitka(self):
        """
        Vykreslí tlačítka Uložit (vpravo dole) a Zpět (vlevo dole).

        Obě tlačítka mají hover efekt a odlišnou barevnou schémata.
        """
        myska = get_pos()

        # Tlačítko Uložit — zelené
        hover_u = self._tl_ulozit.collidepoint(myska)
        pygame.draw.rect(self.screen, (28, 110, 55) if hover_u else (18, 80, 38),
                         self._tl_ulozit, border_radius=10)
        pygame.draw.rect(self.screen, (55, 190, 95), self._tl_ulozit, 2, border_radius=10)
        tu = self.font_label.render("Uložit  >", True, BILA)
        self.screen.blit(tu, (self._tl_ulozit.centerx - tu.get_width() // 2,
                              self._tl_ulozit.centery - tu.get_height() // 2))

        # Tlačítko Zpět — červené
        hover_z = self._tl_zpet.collidepoint(myska)
        pygame.draw.rect(self.screen, (100, 30, 30) if hover_z else (70, 18, 18),
                         self._tl_zpet, border_radius=10)
        pygame.draw.rect(self.screen, (190, 55, 55), self._tl_zpet, 2, border_radius=10)
        tz = self.font_label.render("<  Zpět", True, BILA)
        self.screen.blit(tz, (self._tl_zpet.centerx - tz.get_width() // 2,
                              self._tl_zpet.centery - tz.get_height() // 2))
