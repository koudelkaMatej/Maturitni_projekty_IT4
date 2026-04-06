"""
jednotka.py - Třída záchranářské jednotky
Autor: [tvoje jméno]

Reprezentuje jednu záchranářskou jednotku (Policie, Hasiči, Sanitka).
Jednotka se pohybuje po herní mapě od základny k cíli (události)
a zpět. Obsahuje vizuál základny (klikatelný panel) i samotného auta.
"""

import pygame
import math
from config import BILA, ZLUTA, CERNA


# Vizuální konfigurace každého typu jednotky
KONFIG_JEDNOTEK = {
    "Policie": {
        "barva_telo":     (30,  60,  200),   # modrá karoserie
        "barva_strechy":  (0,   0,   150),   # tmavě modrá střecha
        "barva_svetla":   (0,   120, 255),   # bílá/modrá světla
        "barva_zakladna": (20,  40,  120),   # tmavé pozadí panelu základny
        "zkratka": "POL",
    },
    "Hasiči": {
        "barva_telo":     (200, 30,  30),    # červená karoserie
        "barva_strechy":  (150, 0,   0),     # tmavě červená střecha
        "barva_svetla":   (255, 80,  0),     # oranžová světla
        "barva_zakladna": (100, 20,  20),    # tmavé pozadí panelu
        "zkratka": "HAS",
    },
    "Sanitka": {
        "barva_telo":     (230, 230, 230),   # bílá karoserie
        "barva_strechy":  (180, 180, 180),   # šedá střecha
        "barva_svetla":   (255, 50,  50),    # červená světla
        "barva_zakladna": (110, 110, 110),   # šedé pozadí panelu
        "zkratka": "SAN",
        "barva_text":     (30, 30, 30),      # tmavý text (bílá karoserie)
    },
}

# Rozměry auta (vizuál) a panelu základny (kliková plocha)
AUTO_W,     AUTO_H     = 34, 20   # šířka × výška auta v pixelech
ZAKLADNA_W, ZAKLADNA_H = 90, 80   # šířka × výška klikatelného panelu


class Jednotka:
    """
    Záchranářská jednotka pohybující se po herní mapě.

    Na základně je zobrazena jako velký panel (90×80 px) s názvem a autem.
    Při jízdě je zobrazena pouze jako auto (34×20 px) s blikajícími světly.

    Pohyb:
      - jede_na(pozice) — nastaví cílovou pozici
      - Automaticky se vrátí na základnu po dosažení cíle
      - Rychlost je 3 px/snímek (~180 px/s při 60 FPS)
    """

    def __init__(self, jmeno, pozice, rychlost_vec, barva=(255, 255, 255)):
        """
        Inicializace jednotky.

        Args:
            jmeno (str):       'Policie' | 'Hasiči' | 'Sanitka'
            pozice (tuple):    Střed základny (x, y)
            rychlost_vec:      Nepoužito (zachováno pro kompatibilitu)
            barva:             Nepoužito (barva se načítá z KONFIG_JEDNOTEK)
        """
        self.jmeno = jmeno
        # Uloží počáteční (domovskou) pozici jako levý horní roh panelu základny
        self.start_pozice = list(pozice)
        self.pozice       = list(pozice)    # aktuální pozice auta
        self.cil          = None            # None = jednotka je na místě / bez úkolu
        self.speed        = 3              # rychlost pohybu v px/snímek

        # Animační časovač pro blikání světel za jízdy
        self._svetlo_timer = 0
        # Zda je jednotka aktuálně vybrána hráčem
        self._vybrana      = False

        # Načti barevnou konfiguraci dle typu jednotky
        konfig             = KONFIG_JEDNOTEK.get(jmeno, KONFIG_JEDNOTEK["Sanitka"])
        self.barva_telo     = konfig["barva_telo"]
        self.barva_strechy  = konfig["barva_strechy"]
        self.barva_svetla   = konfig["barva_svetla"]
        self.barva_zakladna = konfig["barva_zakladna"]
        self.zkratka        = konfig["zkratka"]
        # Barva textu — tmavá pro světlé jednotky (Sanitka), bílá pro ostatní
        self.barva_text     = konfig.get("barva_text", BILA)
        self.barva          = self.barva_telo

        # Fonty inicializovány jednou v konstruktoru (ne každý snímek)
        self._font_zkratka = pygame.font.Font(None, 16)
        self._font_jmeno   = pygame.font.Font(None, 22)

    # ------------------------------------------------------------------ #

    def jede_na(self, cil_pozice):
        """
        Nastaví cílovou pozici, ke které se jednotka vydá.

        Args:
            cil_pozice (tuple): Cílové souřadnice (x, y)
        """
        self.cil = cil_pozice

    def update(self):
        """
        Pohyb jednotky každý snímek.

        Logika:
          - Pokud má cíl → jede k cíli, po dosažení cil = None
          - Pokud nemá cíl → vrací se na základnu (start_pozice)
          - Pohyb je přímočarý (lineární interpolace)
        """
        self._svetlo_timer += 1
        # Cíl pohybu: buď zadaný cíl, nebo domovská základna
        aktualni_cil = self.cil if self.cil else self.start_pozice

        dx         = aktualni_cil[0] - self.pozice[0]
        dy         = aktualni_cil[1] - self.pozice[1]
        vzdalenost = math.hypot(dx, dy)

        if vzdalenost < 5:
            # Dosaženo cíle — zastav a vynuluj cíl (pokud to byl úkol)
            if self.cil:
                self.cil = None
        else:
            # Pohyb směrem k cíli — normalizovaný vektor × rychlost
            self.pozice[0] += self.speed * dx / vzdalenost
            self.pozice[1] += self.speed * dy / vzdalenost

    # ------------------------------------------------------------------ #

    def draw(self, screen):
        """
        Vykreslení jednotky.

        Na základně: velký panel (90×80) s názvem + auto uvnitř.
        Na cestě:    pouze auto (34×20) s blikajícími světly.

        Args:
            screen: Pygame surface
        """
        x, y = int(self.pozice[0]), int(self.pozice[1])

        # Detekce, zda je jednotka na základně (blízko počáteční pozice)
        na_zakladne = (math.hypot(x - self.start_pozice[0],
                                  y - self.start_pozice[1]) < 20)

        if na_zakladne:
            # --- Panel základny ---
            zx    = self.start_pozice[0]
            zy    = self.start_pozice[1]
            panel = pygame.Rect(zx, zy, ZAKLADNA_W, ZAKLADNA_H)

            # Pozadí panelu dle barvy jednotky
            pygame.draw.rect(screen, self.barva_zakladna, panel, border_radius=10)

            # Rámeček — zlatý pokud je vybrána, jinak šedý
            barva_ramecku = ZLUTA if self._vybrana else (80, 80, 80)
            tloustka      = 3    if self._vybrana else 1
            pygame.draw.rect(screen, barva_ramecku, panel, tloustka, border_radius=10)

            # Název jednotky nahoře v panelu
            jmeno_surf = self._font_jmeno.render(self.jmeno, True, self.barva_text)
            screen.blit(jmeno_surf, (
                zx + ZAKLADNA_W // 2 - jmeno_surf.get_width() // 2,
                zy + 6))

            # Nápověda "klikni" dole v panelu (skrytá pokud je vybrána)
            if not self._vybrana:
                hint = self._font_jmeno.render("[ klikni ]", True, (130, 130, 130))
                screen.blit(hint, (
                    zx + ZAKLADNA_W // 2 - hint.get_width() // 2,
                    zy + ZAKLADNA_H - 20))

        # --- Auto ---
        # Na základně: auto vycentrované uvnitř panelu
        # Na cestě:    auto na aktuální pozici
        if na_zakladne:
            ax = self.start_pozice[0] + (ZAKLADNA_W - AUTO_W) // 2
            ay = self.start_pozice[1] + (ZAKLADNA_H - AUTO_H) // 2 + 4
        else:
            ax, ay = x, y

        self._draw_auto(screen, ax, ay)

        # Výběrový rámeček kolem auta při jízdě (mimo základnu)
        if self._vybrana and not na_zakladne:
            pygame.draw.rect(screen, ZLUTA,
                             (ax - 3, ay - 9, AUTO_W + 6, AUTO_H + 12), 2, border_radius=4)

    def _draw_auto(self, screen, ax, ay):
        """
        Vykreslí samotné auto na zadané souřadnice.

        Vizuální prvky:
          - Karoserie (34×20 px)
          - Střecha (menší obdélník nahoře)
          - Blikající světla při jízdě (střídají se každých 20 snímků)
          - Zkratka jednotky na karoserii

        Args:
            screen: Pygame surface
            ax (int): X souřadnice levého horního rohu auta
            ay (int): Y souřadnice levého horního rohu auta
        """
        w, h = AUTO_W, AUTO_H

        # Karoserie — zaoblený obdélník
        pygame.draw.rect(screen, self.barva_telo, (ax, ay, w, h), border_radius=4)

        # Střecha — menší obdélník nad karoserií
        pygame.draw.rect(screen, self.barva_strechy,
                         (ax + 6, ay - 6, w - 12, 8), border_radius=3)

        # Blikající světla — zobrazí se jen pokud jednotka jede
        if self.cil and (self._svetlo_timer // 20) % 2 == 0:
            # Svítí barevná světla
            pygame.draw.circle(screen, self.barva_svetla, (ax + 5,     ay), 4)
            pygame.draw.circle(screen, self.barva_svetla, (ax + w - 5, ay), 4)
        elif self.cil:
            # Zhaslé světla (bílé)
            pygame.draw.circle(screen, BILA, (ax + 5,     ay), 4)
            pygame.draw.circle(screen, BILA, (ax + w - 5, ay), 4)

        # Zkratka jednotky na karoserii (tmavá pro Sanitku, bílá pro ostatní)
        lbl = self._font_zkratka.render(self.zkratka, True, self.barva_text)
        screen.blit(lbl, (ax + w // 2 - lbl.get_width() // 2, ay + 4))

    # ------------------------------------------------------------------ #

    def je_kliknuta(self, pozice):
        """
        Detekce kliknutí na jednotku.

        Na základně se používá velká kliková plocha panelu (90×80 px).
        Na cestě se používá malá plocha auta (34×20 px).

        Args:
            pozice (tuple): Kliknutá pozice (x, y) v herním prostoru

        Returns:
            bool: True pokud klik zasáhl jednotku
        """
        x, y = int(self.pozice[0]), int(self.pozice[1])
        na_zakladne = (math.hypot(x - self.start_pozice[0],
                                  y - self.start_pozice[1]) < 20)
        if na_zakladne:
            # Velká plocha — celý panel základny
            return pygame.Rect(
                self.start_pozice[0], self.start_pozice[1],
                ZAKLADNA_W, ZAKLADNA_H
            ).collidepoint(pozice)
        else:
            # Malá plocha — pouze karoserie auta
            return pygame.Rect(x, y, AUTO_W, AUTO_H).collidepoint(pozice)
