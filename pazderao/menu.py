import pygame
from settings import *

class Button():
    def __init__(self, x, y, width, height, text, font):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = font
        self.clicked = False 

    def draw(self, screen):
        action = False
        pos = pygame.mouse.get_pos() # zjištění pozice myši
        
        # logika hover efektu a kliknutí
        if self.rect.collidepoint(pos):
            pygame.draw.rect(screen, BUTTON_HOVER_COL, self.rect) # (settings.py)
            if pygame.mouse.get_pressed()[0] == 1 and not self.clicked:
                self.clicked = True
                action = True
        else:
            pygame.draw.rect(screen, BUTTON_COL, self.rect) # (settings.py)
            
        # reset kliknutí po uvolnění tlačítka
        if pygame.mouse.get_pressed()[0] == 0:
            self.clicked = False
            
        # vykreslení obrysu a textu tlačítka
        pygame.draw.rect(screen, OUTLINE_COL, self.rect, 2) # (settings.py)
        text_img = self.font.render(self.text, True, BUTTON_TEXT_COL) # (settings.py)
        text_rect = text_img.get_rect(center=self.rect.center)
        screen.blit(text_img, text_rect)
        
        return action

class PauseMenu():
    def __init__(self, font):
        # výpočet pozic pro vycentrování tlačítek
        start_y = SCREEN_HEIGHT // 2 - 50 # (settings.py)
        center_x = SCREEN_WIDTH // 2 - BUTTON_WIDTH // 2 # (settings.py)
        
        # vytvoření instancí tlačítek pro pauzu
        self.btn_resume = Button(center_x, start_y, BUTTON_WIDTH, BUTTON_HEIGHT, "POKRACUJ", font) # (settings.py)
        self.btn_quit = Button(center_x, start_y + 80, BUTTON_WIDTH, BUTTON_HEIGHT, "ZPET DO MENU", font) # (settings.py)
        
        # vytvoření poloprůhledného pozadí (overlay)
        self.overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA) # (settings.py)
        self.overlay.fill((0, 0, 0, 150))

    def draw(self, screen):
        screen.blit(self.overlay, (0, 0)) # ztmavení scény při pauze
        
        # kontrola interakce s tlačítky
        if self.btn_resume.draw(screen):
            return "resume"
        
        if self.btn_quit.draw(screen):
            return "quit"
            
        return None