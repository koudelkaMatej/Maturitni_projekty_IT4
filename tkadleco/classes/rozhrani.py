"""
rozhrani.py - Herní HUD (heads-up display)
Autor: [tvoje jméno]

Zobrazuje herní statistiky překryté přes herní plochu.
Pozadí každý snímek vymaže mapa.draw(), takže zde
není potřeba nic přemazávat.
"""

import pygame
from config import *


class Rozhrani:
    """
    HUD překrytý přes herní plochu.

    Zobrazuje:
      - počet aktuálně aktivních událostí na mapě
      - aktuální skóre hráče
      - nápovědu pro ESC
    """

    def __init__(self):
        """Inicializace fontů HUD."""
        self.font      = pygame.font.Font(None, 36)
        self.font_maly = pygame.font.Font(None, 26)

    def draw(self, screen, pocet_udalosti, skore):
        """
        Vykreslení HUD na obrazovku.

        Args:
            screen:          Pygame surface
            pocet_udalosti:  Počet aktivních událostí na mapě
            skore:           Aktuální skóre hráče
        """
        # Poloprůhledný panel vlevo nahoře
        panel = pygame.Surface((220, 80), pygame.SRCALPHA)
        panel.fill((0, 0, 0, 140))
        screen.blit(panel, (10, 10))

        # Počet aktivních událostí — červeně pokud je jich příliš mnoho
        barva_u = CERVENA if pocet_udalosti > 4 else BILA
        t1 = self.font.render(f"Události: {pocet_udalosti}", True, barva_u)
        screen.blit(t1, (18, 16))

        # Aktuální skóre hráče
        t2 = self.font.render(f"Skóre: {skore}", True, ZLUTA)
        screen.blit(t2, (18, 50))

        # Nápověda pro návrat do menu — vpravo nahoře
        esc = self.font_maly.render("ESC = menu", True, (140, 140, 140))
        screen.blit(esc, (WIDTH - esc.get_width() - 12, 14))
