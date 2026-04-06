"""
mapa.py - Vykreslení herní mapy města
Autor: [tvoje jméno]

Záměrně abstraktní pohled z ptačí perspektivy — barevné bloky čtvrtí
BEZ silničních pruhů, přechodů a středových čar.
Cílem je jasně ukázat, že jednotky se pohybují volně přes celou plochu,
ne po cestách.
"""

import pygame
import math
from config import *

# --- Barvy čtvrtí (každá čtvrť má svou barvu) ---
# Teplé tóny = obytné/historické; studené = komerční/průmysl; zelené = park
BARVY_CTVRTI = [
    (90,  70,  55),   # Staré Město     — tmavá hněď
    (75,  85,  95),   # Obchodní Zóna  — modrošedá
    (95,  85,  70),   # Rezidenční      — béžovohnědá
    (55, 105,  60),   # Průmysl         — olivová
    (45, 100,  60),   # Park            — tmavě zelená
    (70,  80,  90),   # Centrum         — slate modrá
    (100, 95,  95),   # Nemocnice       — světle šedorůžová
    (65,  75,  70),   # Škola           — šedozelená
    (60,  60,  75),   # Nádraží         — tmavě šedofialová
    (90,  80,  60),   # Trh             — teplá okrová
    (85,  90,  80),   # Obytná          — světle šedozelená
    (55,  60,  70),   # Sklad           — tmavě šedá
]

# Barvy textur uvnitř bloků
BARVA_STROM   = (35, 110, 45)   # tečky stromů v parku
BARVA_BUDOVA  = (0,   0,   0)   # tmavší obdélníky budov
BARVA_VODA    = (40, 100, 160)  # modrá vodní plocha
BARVA_VLNKA   = (60, 130, 190)  # vlnky na vodě

ZAKLADNA_BG   = (22, 22, 28)    # panel základny dole


class Mapa:
    """
    Abstraktní pohled z ptačí perspektivy na město.

    Mapa je rozdělena na 12 barevně odlišených čtvrtí (3 × 4 mřížka).
    Žádné silniční pruhy ani přechody — jednotky se pohybují volně.
    """

    # Tenká mezera mezi bloky (vypadá jako úzká ulička, NE jako silnice)
    MEZERA = 6

    def __init__(self):
        """Předpočítá rozložení bloků."""
        self._font           = pygame.font.Font(None, 18)
        self._herni_plocha_h = HEIGHT - 130  # základna zabírá spodních 130 px

        # Mřížka: 4 sloupce × 3 řádky = 12 bloků
        self._sloupce = 4
        self._radky   = 3

        self._bloky   = self._vypocti_bloky()

    def _vypocti_bloky(self):
        """
        Rozdělí herní plochu na rovnoměrné bloky s mezerami.

        Returns:
            list[dict]: Každý blok má 'rect', 'barva', 'nazev', 'typ'
        """
        nazvy = [
            "Staré Město",  "Obchodní Zóna", "Rezidenční", "Průmysl",
            "Park",         "Centrum",        "Nemocnice",  "Škola",
            "Nádraží",      "Trh",            "Obytná",     "Sklad",
        ]
        typy = [
            "budovy", "budovy", "budovy", "budovy",
            "park",   "budovy", "nemocnice", "budovy",
            "budovy", "trh",    "budovy",  "sklad",
        ]
        # Index 4 = Park, Index 6 = Nemocnice (bude mít vodní plochu)

        W     = WIDTH
        H     = self._herni_plocha_h
        M     = self.MEZERA
        slou  = self._sloupce
        rad   = self._radky

        # Šířka a výška každého bloku (rovnoměrné dělení s mezerami)
        bw = (W - M * (slou + 1)) // slou
        bh = (H - M * (rad  + 1)) // rad

        bloky = []
        for r in range(rad):
            for s in range(slou):
                idx  = r * slou + s
                x    = M + s * (bw + M)
                y    = M + r * (bh + M)
                bloky.append({
                    "rect":  pygame.Rect(x, y, bw, bh),
                    "barva": BARVY_CTVRTI[idx % len(BARVY_CTVRTI)],
                    "nazev": nazvy[idx],
                    "typ":   typy[idx],
                })
        return bloky

    def draw(self, screen):
        """
        Vykreslení mapy.

        Pořadí:
          1. Tmavé pozadí (mezery mezi bloky)
          2. Barevné bloky čtvrtí s interními texturami
          3. Jemné vnitřní ohraničení bloků
          4. Popisky čtvrtí
          5. Spodní panel základny

        Args:
            screen: Pygame surface
        """
        # 1. Tmavé pozadí — mezery mezi bloky vypadají jako úzké uličky
        screen.fill(ZAKLADNA_BG)

        for blok in self._bloky:
            r    = blok["rect"]
            barva = blok["barva"]
            typ  = blok["typ"]

            # 2. Základní barevná výplň bloku
            pygame.draw.rect(screen, barva, r, border_radius=4)

            # 3. Textury uvnitř bloků dle typu čtvrti
            self._kresli_texturu(screen, r, barva, typ)

            # 4. Jemný světlejší vnitřní rám — dává blokům hloubku
            svetlejsi = tuple(min(255, c + 20) for c in barva)
            pygame.draw.rect(screen, svetlejsi, r, 1, border_radius=4)

        # 5. Popisky čtvrtí — centrované v každém bloku
        for blok in self._bloky:
            r = blok["rect"]
            t = self._font.render(blok["nazev"], True, (220, 220, 200))
            # Stín textu pro čitelnost
            ts = self._font.render(blok["nazev"], True, (0, 0, 0))
            tx = r.centerx - t.get_width() // 2
            ty = r.bottom  - t.get_height() - 6
            screen.blit(ts, (tx + 1, ty + 1))
            screen.blit(t,  (tx, ty))

        # 6. Spodní panel základny jednotek
        pygame.draw.rect(screen, (22, 22, 28),
                         pygame.Rect(0, self._herni_plocha_h, WIDTH, 130))
        pygame.draw.line(screen, (55, 55, 75),
                         (0, self._herni_plocha_h), (WIDTH, self._herni_plocha_h), 2)

        zakladna_font = pygame.font.Font(None, 24)
        zt = zakladna_font.render("Z Á K L A D N A", True, (65, 65, 80))
        screen.blit(zt, (WIDTH // 2 - zt.get_width() // 2, self._herni_plocha_h + 8))

    def _kresli_texturu(self, screen, r, barva, typ):
        """
        Přidá vizuální texturu do bloku podle jeho typu.

        Park    → zelené tečky stromů
        Trh     → malé tečky (stánky)
        Nemocnice/ostatní → tmavší obdélníky budov
        Sklad   → velké jednoduché obdélníky

        Args:
            screen: Pygame surface
            r:      pygame.Rect bloku
            barva:  základní barva bloku
            typ:    typ čtvrti ('park', 'trh', 'nemocnice', 'budovy', 'sklad')
        """
        tmavsi = tuple(max(0, c - 18) for c in barva)

        if typ == "park":
            # Stromy — zelené kruhy nepravidelně rozložené
            for tx in range(r.x + 14, r.right  - 10, 20):
                for ty in range(r.y + 14, r.bottom - 18, 20):
                    pygame.draw.circle(screen, BARVA_STROM, (tx, ty), 6)
                    pygame.draw.circle(screen, (25, 85, 35), (tx, ty), 6, 1)

        elif typ == "trh":
            # Trh — malé tečky jako stánky v mřížce
            for tx in range(r.x + 10, r.right  - 8,  14):
                for ty in range(r.y + 10, r.bottom - 16, 14):
                    pygame.draw.circle(screen, tmavsi, (tx, ty), 3)

        elif typ == "sklad":
            # Sklad — dva velké obdélníky
            pw = r.width  // 2 - 12
            ph = r.height // 2 - 14
            pygame.draw.rect(screen, tmavsi,
                             pygame.Rect(r.x + 8,           r.y + 8,           pw, ph), border_radius=2)
            pygame.draw.rect(screen, tmavsi,
                             pygame.Rect(r.x + pw + 16,     r.y + 8,           pw, ph), border_radius=2)
            pygame.draw.rect(screen, tmavsi,
                             pygame.Rect(r.x + r.width//4,  r.y + ph + 16,
                                         r.width // 2,       r.height // 2 - 16), border_radius=2)

        else:
            # Budovy — mřížka tmavších obdélníků různých velikostí
            bw = max(8,  r.width  // 4 - 4)
            bh = max(10, r.height // 3 - 6)
            for bxi in range(r.x + 6, r.right  - bw - 2, bw + 5):
                for byi in range(r.y + 6, r.bottom - bh - 14, bh + 5):
                    pygame.draw.rect(screen, tmavsi,
                                     pygame.Rect(bxi, byi, bw, bh), border_radius=1)
