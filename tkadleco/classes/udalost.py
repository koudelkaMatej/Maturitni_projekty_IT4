"""
udalost.py - Třída pro herní události
Autor: [tvoje jméno]

Definuje různé typy záchranářských událostí, které se zobrazují
na herní mapě a musí být vyřešeny hráčem správným typem jednotky.

Logika párování:
  - Správná jednotka dorazí → událost vyřešena (aktivni = False)
  - Špatná jednotka dorazí  → odmítnuta, vrátí se na základnu
  - Časový limit vyprší     → aktivni = False, skóre -1 (řeší SpravceHry)
"""

import pygame
import math
from config import BILA, ZELENA, ZLUTA, CERVENA


# Slovník typů událostí: barva kruhu, požadovaná jednotka, časový limit (snímky @ 60 FPS)
TYPY_UDALOSTI = {
    "požár":     {"barva": (220, 50,  30),  "vyzaduje": "Hasiči",  "cas": 1800},
    "nehoda":    {"barva": (255, 140,  0),  "vyzaduje": "Sanitka", "cas": 2000},
    "krádež":    {"barva": (50,  80,  220), "vyzaduje": "Policie", "cas": 2200},
    "povodeň":   {"barva": (30, 144, 255),  "vyzaduje": "Hasiči",  "cas": 2400},
    "výbuch":    {"barva": (255, 200,   0), "vyzaduje": "Hasiči",  "cas": 1200},
    "přepadení": {"barva": (128,   0, 128), "vyzaduje": "Policie", "cas": 1600},
}


class Udalost:
    """
    Reprezentuje záchranářskou událost na mapě.

    Každý typ události vyžaduje konkrétní typ záchranářské jednotky.
    Pokud dorazí špatná jednotka, událost se nevyřeší a jednotka
    se automaticky vrátí zpět na základnu.

    Atributy:
        typ (str):                  Typ události (klíč v TYPY_UDALOSTI)
        pozice (tuple):             Souřadnice (x, y) na mapě
        aktivni (bool):             Zda je událost stále aktivní
        vyzadovana_jednotka (str):  Typ jednotky nutný pro vyřešení
        prirazena_jednotka:         Jednotka jedoucí k události (nebo None)
    """

    def __init__(self, typ, pozice):
        """
        Inicializace události.

        Args:
            typ (str):      Typ události (klíč v TYPY_UDALOSTI)
            pozice (tuple): Pozice (x, y) na mapě
        """
        self.typ    = typ
        self.pozice = pozice
        self.timer  = 0         # počítadlo snímků od vzniku události
        self.aktivni = True
        self.prirazena_jednotka = None

        # Časovač varování při špatné jednotce (počet snímků zobrazení nápisu)
        self.spatna_jednotka_timer = 0

        # Načti vlastnosti z konfigurace (barva, požadovaná jednotka, limit)
        vlastnosti            = TYPY_UDALOSTI.get(typ, TYPY_UDALOSTI["nehoda"])
        self.barva            = vlastnosti["barva"]
        self.vyzadovana_jednotka = vlastnosti["vyzaduje"]
        self.casovy_limit     = vlastnosti["cas"]

        # Animační proměnná pro pulzující halo
        self._puls      = 0
        # Font se inicializuje lazily při prvním vykreslení
        self._font_label = None

    def prirad_jednotku(self, jednotka):
        """
        Přiřadí jednotku jedoucí na tuto událost.

        Args:
            jednotka: Objekt Jednotka
        """
        self.prirazena_jednotka = jednotka

    def update(self):
        """
        Aktualizace stavu události každý snímek.

        Logika párování:
          - Jednotka dorazila (cil == None) a je správného typu → vyřešeno
          - Jednotka dorazila a je špatného typu → odmítnutí, vrátí se domů
          - Timer překročil limit → automaticky deaktivováno (timeout)
        """
        # Zkontroluj, zda přiřazená jednotka dorazila (cil = None znamená dojeto)
        if self.prirazena_jednotka and not self.prirazena_jednotka.cil:
            if self.prirazena_jednotka.jmeno == self.vyzadovana_jednotka:
                # Správná jednotka — událost vyřešena
                self.aktivni = False
            else:
                # Špatná jednotka — odmítni ji, vrátí se na základnu sama
                self.prirazena_jednotka = None
                self.spatna_jednotka_timer = 90  # zobraz varování 1.5 sekundy

        # Posuň animační fázi pulzujícího halo
        self.timer += 1
        self._puls = (self._puls + 0.08) % (2 * math.pi)

        # Odpočítávej varování špatné jednotky
        if self.spatna_jednotka_timer > 0:
            self.spatna_jednotka_timer -= 1

        # Timeout — událost vyprší po překročení časového limitu
        if self.timer > self.casovy_limit:
            self.aktivni = False

    def draw(self, screen):
        """
        Vykreslení události s animací a ukazatelem zbývajícího času.

        Vizuální prvky:
          - Pulzující barevné halo (animace)
          - Barevný kruh s bílým rámečkem
          - Oblouk znázorňující zbývající čas (zelená → žlutá → červená)
          - Název typu a zkratka požadované jednotky
          - Žlutá tečka pokud k události jede jednotka
          - Červené varování při špatné jednotce

        Args:
            screen: Pygame surface
        """
        x, y = self.pozice

        # Pulzující barevné halo kolem události
        r    = int(18 + 5 * math.sin(self._puls))
        halo = pygame.Surface((r * 2 + 2, r * 2 + 2), pygame.SRCALPHA)
        pygame.draw.circle(halo, (*self.barva, 70), (r + 1, r + 1), r)
        screen.blit(halo, (x - r - 1, y - r - 1))

        # Hlavní barevný kruh s bílým ohraničením
        pygame.draw.circle(screen, self.barva, (x, y), 15)
        pygame.draw.circle(screen, BILA,       (x, y), 15, 2)

        # Časový oblouk — barva se mění dle zbývajícího procenta času
        zbyvajici = max(0.0, 1.0 - self.timer / self.casovy_limit)
        if zbyvajici > 0:
            barva_casu = ZELENA if zbyvajici > 0.5 else (ZLUTA if zbyvajici > 0.25 else CERVENA)
            start_a    = math.radians(90 - zbyvajici * 360)
            end_a      = math.radians(90)
            pygame.draw.arc(screen, barva_casu,
                            pygame.Rect(x - 19, y - 19, 38, 38),
                            min(start_a, end_a), max(start_a, end_a), 3)

        # Lazy inicializace fontu (jednou za celý běh)
        if self._font_label is None:
            self._font_label = pygame.font.Font(None, 19)

        # Název typu události pod kruhem
        nazev = self._font_label.render(self.typ.upper(), True, BILA)
        screen.blit(nazev, (x - nazev.get_width() // 2, y + 18))

        # Zkratka požadované jednotky (zkráceno na 3 znaky)
        zkr  = self.vyzadovana_jednotka[:3].upper()
        jlab = self._font_label.render(f"→ {zkr}", True, ZLUTA)
        screen.blit(jlab, (x - jlab.get_width() // 2, y + 32))

        # Žlutá tečka vpravo nahoře = jednotka je na cestě
        if self.prirazena_jednotka:
            pygame.draw.circle(screen, ZLUTA, (x + 13, y - 13), 5)

        # Červené varování při přijetí špatné jednotky
        if self.spatna_jednotka_timer > 0:
            alfa  = min(255, self.spatna_jednotka_timer * 3)
            wf    = pygame.font.Font(None, 22)
            warn  = wf.render("ŠPATNÁ JEDNOTKA!", True, CERVENA)
            ws    = pygame.Surface(warn.get_size(), pygame.SRCALPHA)
            ws.blit(warn, (0, 0))
            ws.set_alpha(alfa)
            screen.blit(ws, (x - warn.get_width() // 2, y - 42))

    def je_kliknuta(self, pozice):
        """
        Zjistí, zda bylo kliknuto na tuto událost.

        Detekce probíhá pomocí kruhu o poloměru 15 px.

        Args:
            pozice (tuple): Kliknutá pozice (x, y)

        Returns:
            bool: True pokud klik zasáhl oblast události
        """
        px, py = pozice
        ux, uy = self.pozice
        return (px - ux) ** 2 + (py - uy) ** 2 <= 15 ** 2
