import pygame
from config import *

class Menu:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.Font(None, 72)
        self.mensi_font = pygame.font.Font(None, 48)
        # Tlačítka: (x, y, šířka, výška)
        self.tlacitka = {
            "hrat": pygame.Rect(WIDTH//2 - 100, 250, 200, 60),
            "nastaveni": pygame.Rect(WIDTH//2 - 100, 350, 200, 60),
            "tutorial": pygame.Rect(400, 450, 200, 60),
            "konec": pygame.Rect(WIDTH//2 - 100, 550, 200, 60)
        }

    def handle_event(self, udalost):
        if udalost.type == pygame.MOUSEBUTTONDOWN and udalost.button == 1:
            poz = pygame.mouse.get_pos()
            for jmeno, rect in self.tlacitka.items():
                if rect.collidepoint(poz):
                    return jmeno
        return None

    

    def draw(self):
        pygame.draw.rect(self.screen, MODRA, self.tlacitka["tutorial"])
        self.screen.blit(self.font.render("TUTORIÁL", True, BILA), (420, 440))
        self.screen.fill(SEDA)
        nadpis = self.font.render("Simulátor IZS", True, BILA)
        self.screen.blit(nadpis, (WIDTH//2 - nadpis.get_width()//2, 150))
        for jmeno, rect in self.tlacitka.items():
            pygame.draw.rect(self.screen, MODRA, rect)
            text = self.mensi_font.render(jmeno.capitalize(), True, BILA)
            self.screen.blit(text, (rect.centerx - text.get_width()//2, rect.centery - text.get_height()//2))
