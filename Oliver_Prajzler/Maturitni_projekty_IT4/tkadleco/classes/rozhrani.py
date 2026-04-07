import pygame
from config import *

class Rozhrani:
    def __init__(self):
        self.font = pygame.font.Font(None, 36)

    def draw(self, screen, pocet_udalosti, skore):
        pygame.draw.rect(screen, SEDA, (20, 20, 250, 40))
        pygame.draw.rect(screen, SEDA, (20, 60, 200, 40))
        pygame.draw.rect(screen, SEDA, (WIDTH - 200, 20, 180, 40))

        text1 = self.font.render(f"Aktivní události: {pocet_udalosti}", True, BILA)
        text2 = self.font.render(f"Skóre: {skore}", True, ZLUTA)
        screen.blit(text1, (20, 20))
        screen.blit(text2, (20, 60))
        esc = self.font.render("ESC = menu", True, BILA)
        screen.blit(esc, (WIDTH - 200, 20))
