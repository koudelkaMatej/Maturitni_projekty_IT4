"""
tutorial.py - Interaktivní tutoriál hry
Autor: [tvoje jméno]

Zobrazuje tutoriál rozdělený do 5 stránek s jasnými popisy
herních mechanik, typů událostí a ovládání.

Navigace:
  - Tlačítka Další / Předchozí na obrazovce
  - Klávesy šipky Vpravo/Vlevo nebo D/A
  - ESC nebo Q → zpět do menu
  - Na poslední stránce tlačítko "Hrát!" → přechod na STAV_MENU
"""

import pygame
from classes.mys import get_pos
from config import *


# Obsah tutoriálu — 5 stránek, každá má nadpis, barevné téma a seznam řádků textu
STRANKY = [
    {
        "nadpis": "Vítej v City Rescue Simulator!",
        "barva":  (50, 120, 220),
        "obsah": [
            "Jsi velitel záchranářských složek českého města.",
            "",
            "Tvůj úkol: řídit tři záchranářské jednotky",
            "a rychle reagovat na náhodné události po celém městě.",
            "",
            "Hra trvá 1 minutu. Za každou vyřešenou událost",
            "získáš +1 bod. Pokud událost vyprší bez vyřešení,",
            "přijdeš o 1 bod!",
            "",
            "Poraď se s legendou vpravo dole během hry.",
        ],
    },
    {
        "nadpis": "Tvoje jednotky",
        "barva":  (40, 160, 80),
        "obsah": [
            "Máš k dispozici tři typy záchranářů:",
            "",
            "  POLICIE  (modrá)    — řeší krádeže a přepadení",
            "",
            "  HASIČI   (červená)  — hasí požáry, povodně a výbuchy",
            "",
            "  SANITKA  (bílá)     — ošetřuje nehody a zraněné",
            "",
            "Každá jednotka zvládne POUZE svůj typ události!",
            "Špatná jednotka se vrátí na základnu bez výsledku.",
        ],
    },
    {
        "nadpis": "Jak ovládat jednotky",
        "barva":  (180, 120, 30),
        "obsah": [
            "Ovládání je jednoduché — vše myší:",
            "",
            "  1. Klikni na jednotku na základně dole",
            "     (panel se zvýrazní žlutým rámečkem)",
            "",
            "  2. Klikni na událost na mapě",
            "     (barevný pulzující kruh)",
            "",
            "  3. Jednotka automaticky odjede na místo",
            "",
            "  4. Po vyřešení událost zmizí a získáš +1 bod!",
            "",
            "Stiskni ESC pro návrat do menu.",
        ],
    },
    {
        "nadpis": "Typy událostí",
        "barva":  (200, 50, 50),
        "obsah": [
            "Na mapě se náhodně objeví tyto typy událostí:",
            "",
            "  POŽÁR     (červená)   → pošli HASIČE",
            "  POVODEŇ   (modrá)     → pošli HASIČE",
            "  VÝBUCH    (žlutá)     → pošli HASIČE",
            "",
            "  NEHODA    (oranžová)  → pošli SANITKU",
            "",
            "  KRÁDEŽ    (fialová)   → pošli POLICII",
            "  PŘEPADENÍ (tmavá)     → pošli POLICII",
            "",
            "Časový oblouk kolem události ukazuje zbývající čas.",
            "Červený oblouk = pozor, brzy vyprší a přijdeš o bod!",
        ],
    },
    {
        "nadpis": "Tipy pro vysoké skóre",
        "barva":  (130, 60, 200),
        "obsah": [
            "Chceš se dostat na vrchol žebříčku? Pár tipů:",
            "",
            "  - Sleduj všechny tři jednotky najednou",
            "  - Prioritizuj události s málo zbývajícím časem",
            "  - Špatná jednotka plýtvá časem i pohybem!",
            "  - Nevyřešená událost ti odebere 1 bod — hlídej čas",
            "  - Na těžké obtížnosti přicházejí události každých",
            "    1,5 sekundy — rychlost je klíč",
            "",
            "Po skončení hry zadej jméno a odešli skóre",
            "na online žebříček — porovnej se s ostatními!",
            "",
            "Hodně štěstí, veliteli!",
        ],
    },
]


class Tutorial:
    """
    Interaktivní tutoriál zobrazovaný po stránkách.

    Navigace šipkami nebo tlačítky na obrazovce.
    Na poslední stránce tlačítko Hrát! přejde rovnou do menu
    (odkud si hráč může spustit hru).
    """

    def __init__(self, screen):
        """
        Args:
            screen: Pygame surface (game_surface z main.py)
        """
        self.screen  = screen
        self.stranka = 0   # aktuální stránka (0 = první)

        # Fonty pro různé části tutoriálu
        self.font_nadpis = pygame.font.Font(None, 52)
        self.font_text   = pygame.font.Font(None, 30)
        self.font_maly   = pygame.font.Font(None, 24)

        # Tlačítka navigace — sdílené draw i handle_event
        self._tl_dalsi    = pygame.Rect(WIDTH - 220, HEIGHT - 72, 190, 50)
        self._tl_zpet_nav = pygame.Rect(WIDTH // 2 - 95, HEIGHT - 72, 190, 50)
        self._tl_menu     = pygame.Rect(30, HEIGHT - 72, 160, 50)

    def handle_event(self, udalost):
        """
        Zpracování kliknutí a kláves.

        Returns:
            'menu' — návrat do menu (ESC, Q, klik na Menu nebo Hrát! na poslední stránce)
            None   — jinak
        """
        if udalost.type == pygame.KEYDOWN:
            if udalost.key in (pygame.K_ESCAPE, pygame.K_q):
                return "menu"
            # Šipka vpravo / D = další stránka
            if udalost.key in (pygame.K_RIGHT, pygame.K_d):
                self.stranka = min(self.stranka + 1, len(STRANKY) - 1)
            # Šipka vlevo / A = předchozí stránka
            if udalost.key in (pygame.K_LEFT, pygame.K_a):
                self.stranka = max(self.stranka - 1, 0)

        if udalost.type == pygame.MOUSEBUTTONDOWN and udalost.button == 1:
            poz = get_pos()
            # Tlačítko Menu (vlevo dole)
            if self._tl_menu.collidepoint(poz):
                return "menu"
            # Tlačítko Další / Hrát (vpravo dole)
            if self._tl_dalsi.collidepoint(poz):
                if self.stranka < len(STRANKY) - 1:
                    self.stranka += 1
                else:
                    return "menu"   # poslední stránka → menu
            # Tlačítko Předchozí (uprostřed dole)
            if self._tl_zpet_nav.collidepoint(poz):
                if self.stranka > 0:
                    self.stranka -= 1

        return None

    def draw(self):
        """
        Vykreslení aktuální stránky tutoriálu.

        Layout:
          - Barevný pruh nahoře s nadpisem stránky
          - Tečky průběhu (indikátor aktuální stránky)
          - Textový obsah stránky
          - Spodní panel s navigačními tlačítky
        """
        data       = STRANKY[self.stranka]
        barva_tema = data["barva"]   # barva závisí na stránce

        # Tmavé pozadí
        self.screen.fill((16, 16, 24))

        # Barevný pruh nahoře s nadpisem
        pygame.draw.rect(self.screen, barva_tema, (0, 0, WIDTH, 120))
        n = self.font_nadpis.render(data["nadpis"], True, BILA)
        self.screen.blit(n, (WIDTH // 2 - n.get_width() // 2, 38))

        # Číslo stránky vpravo nahoře
        pg = self.font_maly.render(f"{self.stranka + 1} / {len(STRANKY)}", True, BILA)
        self.screen.blit(pg, (WIDTH - pg.get_width() - 20, 10))

        # Tečky průběhu pod nadpisem
        for i in range(len(STRANKY)):
            cx       = WIDTH // 2 - (len(STRANKY) * 22) // 2 + i * 22 + 11
            # Aktivní tečka je bílá a větší
            barva_t  = BILA if i == self.stranka else (80, 80, 100)
            polomer  = 6   if i == self.stranka else 4
            pygame.draw.circle(self.screen, barva_t, (cx, 108), polomer)

        # Textový obsah stránky
        y = 148
        for radek in data["obsah"]:
            if radek == "":
                y += 8    # prázdný řádek = menší mezera
                continue

            # Zvýraznění klíčových slov (typy jednotek a událostí)
            if any(j in radek for j in ("POLICIE", "HASIČI", "SANITKA",
                                         "POŽÁR", "POVODEŇ", "VÝBUCH",
                                         "NEHODA", "KRÁDEŽ", "PŘEPADENÍ")):
                barva_r = ZLUTA   # klíčová slova žlutě
            elif radek.startswith("  "):
                barva_r = (200, 200, 220)   # odsazené řádky světle šedě
            else:
                barva_r = BILA    # normální text bíle

            t = self.font_text.render(radek, True, barva_r)
            self.screen.blit(t, (80, y))
            y += 32

        # Spodní panel s navigačními tlačítky
        pygame.draw.rect(self.screen, (22, 22, 32), (0, HEIGHT - 86, WIDTH, 86))
        pygame.draw.line(self.screen, (50, 50, 80), (0, HEIGHT - 86), (WIDTH, HEIGHT - 86), 1)

        myska = get_pos()

        # Tlačítko Menu (vlevo)
        hm = self._tl_menu.collidepoint(myska)
        pygame.draw.rect(self.screen, (60, 40, 40) if hm else (40, 25, 25),
                         self._tl_menu, border_radius=8)
        pygame.draw.rect(self.screen, (140, 70, 70), self._tl_menu, 1, border_radius=8)
        tm = self.font_maly.render("< Menu", True, BILA)
        self.screen.blit(tm, (self._tl_menu.centerx - tm.get_width() // 2,
                               self._tl_menu.centery - tm.get_height() // 2))

        # Tlačítko Předchozí (uprostřed) — zobrazí se až od 2. stránky
        if self.stranka > 0:
            hz = self._tl_zpet_nav.collidepoint(myska)
            pygame.draw.rect(self.screen, (50, 50, 80) if hz else (35, 35, 60),
                             self._tl_zpet_nav, border_radius=8)
            pygame.draw.rect(self.screen, (90, 90, 140), self._tl_zpet_nav, 1, border_radius=8)
            tz = self.font_maly.render("< Předchozí", True, BILA)
            self.screen.blit(tz, (self._tl_zpet_nav.centerx - tz.get_width() // 2,
                                   self._tl_zpet_nav.centery - tz.get_height() // 2))

        # Tlačítko Další / Hrát (vpravo) — barva odpovídá tématu stránky
        hd      = self._tl_dalsi.collidepoint(myska)
        barva_d = barva_tema if not hd else tuple(min(255, c + 30) for c in barva_tema)
        pygame.draw.rect(self.screen, barva_d, self._tl_dalsi, border_radius=8)
        # Na poslední stránce zobrazí "Hrát!" místo "Další >"
        label_d = "Hrát! >" if self.stranka == len(STRANKY) - 1 else "Další >"
        td = self.font_maly.render(label_d, True, BILA)
        self.screen.blit(td, (self._tl_dalsi.centerx - td.get_width() // 2,
                               self._tl_dalsi.centery - td.get_height() // 2))
