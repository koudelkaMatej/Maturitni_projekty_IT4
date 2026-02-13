import pygame
from config import *

class Rozhrani:
    def __init__(self):
        self.font = pygame.font.Font(None, 36)

    def draw(self, screen, pocet_udalosti, skore):
        # Překreslíme malé oblasti pozadí, aby starý text zmizel
        pygame.draw.rect(screen, SEDA, (20, 20, 250, 40))  # pro aktivní události
        pygame.draw.rect(screen, SEDA, (20, 60, 200, 40))  # pro skóre
        pygame.draw.rect(screen, SEDA, (WIDTH - 200, 20, 180, 40))  # pro ESC

        # Teď vykreslíme text
        text1 = self.font.render(f"Aktivní události: {pocet_udalosti}", True, BILA)
        text2 = self.font.render(f"Skóre: {skore}", True, ZLUTA)
        screen.blit(text1, (20, 20))
        screen.blit(text2, (20, 60))
        esc = self.font.render("ESC = menu", True, BILA)
        screen.blit(esc, (WIDTH - 200, 20))
