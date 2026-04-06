"""
menu.py - Hlavní menu hry
Autor: [tvoje jméno]

Zobrazuje úvodní obrazovku se 5 tlačítky:
  Hrát → spustí novou hru
  Žebříček → zobrazí online žebříček
  Nastavení → otevře nastavení (obtížnost, rozlišení)
  Tutoriál → zobrazí průvodce hrou
  Konec → ukončí aplikaci
"""

import pygame
from classes.mys import get_pos
from config import *


class Menu:
    """
    Hlavní menu hry s pěti tlačítky a hover efektem.

    handle_event() vrací název akce odpovídající kliknutému tlačítku.
    """

    def __init__(self, screen):
        """
        Inicializace menu.

        Args:
            screen: Pygame surface pro vykreslování (game_surface z main.py)
        """
        self.screen     = screen
        self.font       = pygame.font.Font(None, 72)
        self.mensi_font = pygame.font.Font(None, 48)

        # Obdélníky tlačítek — všechna zarovnaná na střed, rozložená svisle
        self.tlacitka = {
            "hrat":       pygame.Rect(WIDTH // 2 - 120, 220, 240, 60),
            "scoreboard": pygame.Rect(WIDTH // 2 - 120, 300, 240, 60),
            "nastaveni":  pygame.Rect(WIDTH // 2 - 120, 380, 240, 60),
            "tutorial":   pygame.Rect(WIDTH // 2 - 120, 460, 240, 60),
            "konec":      pygame.Rect(WIDTH // 2 - 120, 540, 240, 60),
        }

        # Popisky tlačítek
        self.popisky = {
            "hrat":       "Hrát",
            "scoreboard": "Žebříček",
            "nastaveni":  "Nastavení",
            "tutorial":   "Tutoriál",
            "konec":      "Konec",
        }

        # Barvy tlačítek — každá akce má svou barvu
        self.barvy = {
            "hrat":       ZELENA,
            "scoreboard": (180, 130, 30),
            "nastaveni":  MODRA,
            "tutorial":   (100, 60, 180),
            "konec":      CERVENA,
        }

    def handle_event(self, udalost):
        """
        Zpracování kliknutí myší na tlačítka.

        Args:
            udalost: Pygame event objekt

        Returns:
            str: Název akce ('hrat' | 'nastaveni' | 'tutorial' | 'scoreboard' | 'konec')
            None: Žádná akce
        """
        if udalost.type == pygame.MOUSEBUTTONDOWN and udalost.button == 1:
            poz = get_pos()
            for jmeno, rect in self.tlacitka.items():
                if rect.collidepoint(poz):
                    return jmeno
        return None

    def draw(self):
        """
        Vykreslení menu na obrazovku.

        Tlačítka se zesvětlí při najetí myší (hover efekt).
        """
        # Vymaž obrazovku — menu je první vrstva
        self.screen.fill(SEDA)

        # Nadpis a podnadpis vycentrované nahoře
        nadpis       = self.font.render("Simulátor IZS", True, BILA)
        podnadpis_font = pygame.font.Font(None, 32)
        podnadpis    = podnadpis_font.render("City Rescue Simulator", True, ZLUTA)
        self.screen.blit(nadpis,    (WIDTH // 2 - nadpis.get_width()    // 2, 100))
        self.screen.blit(podnadpis, (WIDTH // 2 - podnadpis.get_width() // 2, 170))

        # Vykreslení tlačítek s hover efektem
        myska = get_pos()
        for jmeno, rect in self.tlacitka.items():
            barva_zaklad = self.barvy[jmeno]
            # Hover: zesvětlení o 40 bodů při najetí myší
            if rect.collidepoint(myska):
                barva = tuple(min(255, c + 40) for c in barva_zaklad)
            else:
                barva = barva_zaklad

            pygame.draw.rect(self.screen, barva, rect, border_radius=8)
            pygame.draw.rect(self.screen, BILA,  rect, 2, border_radius=8)  # bílý rámeček

            # Popisek vycentrovaný uvnitř tlačítka
            text = self.mensi_font.render(self.popisky[jmeno], True, BILA)
            self.screen.blit(text, (
                rect.centerx - text.get_width()  // 2,
                rect.centery - text.get_height() // 2
            ))

        # Verze aplikace v pravém dolním rohu
        ver_font = pygame.font.Font(None, 24)
        ver = ver_font.render("v1.0 | SPS Kladno", True, (100, 100, 100))
        self.screen.blit(ver, (WIDTH - ver.get_width() - 10, HEIGHT - 30))
