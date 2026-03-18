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
        pos = pygame.mouse.get_pos() # kde je myš
        
        # barva tlačítka při najetí a klikání
        if self.rect.collidepoint(pos):
            pygame.draw.rect(screen, BUTTON_HOVER_COL, self.rect)
            if pygame.mouse.get_pressed()[0] == 1 and not self.clicked:
                self.clicked = True
                action = True
        else:
            pygame.draw.rect(screen, BUTTON_COL, self.rect)
            
        # reset aby nešlo klikat pořád dokola
        if pygame.mouse.get_pressed()[0] == 0:
            self.clicked = False
            
        # vykreslení textu na střed
        pygame.draw.rect(screen, OUTLINE_COL, self.rect, 2)
        text_img = self.font.render(self.text, True, BUTTON_TEXT_COL)
        text_rect = text_img.get_rect(center=self.rect.center)
        screen.blit(text_img, text_rect)
        
        return action

class PauseMenu():
    def __init__(self, font):
        # pozice tlačítek v pauze
        start_y = SCREEN_HEIGHT // 2 - 50
        center_x = SCREEN_WIDTH // 2 - BUTTON_WIDTH // 2
        
        # tlačítka pro pauzu
        self.btn_resume = Button(center_x, start_y, BUTTON_WIDTH, BUTTON_HEIGHT, "POKRACUJ", font)
        self.btn_quit = Button(center_x, start_y + 80, BUTTON_WIDTH, BUTTON_HEIGHT, "ZPET DO MENU", font)
        
        # černej poloprůhlednej flek přes hru
        self.overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        self.overlay.fill((0, 0, 0, 150))

    def draw(self, screen):
        screen.blit(self.overlay, (0, 0)) # ztmavení pozadí
        
        # co se stane po kliknutí
        if self.btn_resume.draw(screen):
            return "resume"
        
        if self.btn_quit.draw(screen):
            return "quit"
            
        return None