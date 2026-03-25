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
        
        if self.rect.collidepoint(pos):
            pygame.draw.rect(screen, BUTTON_HOVER_COL, self.rect) # barva tlačítka při najetí
            if pygame.mouse.get_pressed()[0] == 1 and not self.clicked:
                self.clicked = True
                action = True # označení kliknutí
        else:
            pygame.draw.rect(screen, BUTTON_COL, self.rect) # základní barva tlačítka
            
        if pygame.mouse.get_pressed()[0] == 0:
            self.clicked = False # reset kliknutí, aby to nebralo jeden stisk víckrát
            
        pygame.draw.rect(screen, OUTLINE_COL, self.rect, 2) # vykreslení obrysu
        text_img = self.font.render(self.text, True, BUTTON_TEXT_COL)
        text_rect = text_img.get_rect(center=self.rect.center) # vycentrování textu na střed tlačítka
        screen.blit(text_img, text_rect)
        
        return action

class PauseMenu():
    def __init__(self, font):
        start_y = SCREEN_HEIGHT // 2 - 50 # výpočet výšky pro první tlačítko
        center_x = SCREEN_WIDTH // 2 - BUTTON_WIDTH // 2 # výpočet středu pro tlačítka
        
        self.btn_resume = Button(center_x, start_y, BUTTON_WIDTH, BUTTON_HEIGHT, "POKRACUJ", font)
        self.btn_quit = Button(center_x, start_y + 80, BUTTON_WIDTH, BUTTON_HEIGHT, "ZPET DO MENU", font)
        
        self.overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA) # vytvoření průhledné vrstvy
        self.overlay.fill((0, 0, 0, 150)) # nastavení černé barvy s průhledností

    def draw(self, screen):
        screen.blit(self.overlay, (0, 0)) # ztmavení scény pod menu
        
        if self.btn_resume.draw(screen): return "resume" # pokračování ve hře
        if self.btn_quit.draw(screen): return "quit" # návrat do menu
            
        return None