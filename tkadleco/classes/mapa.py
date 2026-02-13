import pygame
from config import *

class Mapa:
    def __init__(self):
        # Zde můžeš později načíst detailní mapu nebo dlaždice
        pass

    def draw(self, screen):
        # Jednoduché zobrazení hrací plochy (obdélník)
        pygame.draw.rect(screen, (70, 70, 70), (50, 50, WIDTH - 100, HEIGHT - 150))
