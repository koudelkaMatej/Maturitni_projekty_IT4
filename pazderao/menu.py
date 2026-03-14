import pygame
from settings import *

class Button():
    def __init__(self, x, y, width, height, text, font):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = font
        self.clicked = False # Zabraňuje vícenásobnému kliknutí při držení myši

    def draw(self, screen):
        action = False
        pos = pygame.mouse.get_pos()
        
        # Hover efekt (najetí myší)
        if self.rect.collidepoint(pos):
            pygame.draw.rect(screen, BUTTON_HOVER_COL, self.rect)
            # Detekce kliknutí
            if pygame.mouse.get_pressed()[0] == 1 and not self.clicked:
                self.clicked = True
                action = True
        else:
            pygame.draw.rect(screen, BUTTON_COL, self.rect)
            
        # Reset kliknutí, když uživatel pustí tlačítko
        if pygame.mouse.get_pressed()[0] == 0:
            self.clicked = False
            
        pygame.draw.rect(screen, OUTLINE_COL, self.rect, 2)
        
        # Vykreslení textu
        text_img = self.font.render(self.text, True, BUTTON_TEXT_COL)
        text_rect = text_img.get_rect(center=self.rect.center)
        screen.blit(text_img, text_rect)
        
        return action

class PauseMenu():
    def __init__(self, font):
        # Nastavíme tlačítka přesně doprostřed obrazovky
        start_y = SCREEN_HEIGHT // 2 - 100
        center_x = SCREEN_WIDTH // 2 - BUTTON_WIDTH // 2
        
        self.btn_resume = Button(center_x, start_y, BUTTON_WIDTH, BUTTON_HEIGHT, "POKRACUJ", font)
        self.btn_table = Button(center_x, start_y + 80, BUTTON_WIDTH, BUTTON_HEIGHT, "TABULKA", font)
        self.btn_quit = Button(center_x, start_y + 160, BUTTON_WIDTH, BUTTON_HEIGHT, "ZPET DO MENU", font)
        
        # Poloprůhledné pozadí (černá s 150 alfa kanálem)
        self.overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        self.overlay.fill((0, 0, 0, 150))

    def draw(self, screen):
        # Vykreslí ztmavení přes celou hru
        screen.blit(self.overlay, (0, 0))
        
        # Vykreslí tlačítka a hlídá kliknutí
        if self.btn_resume.draw(screen):
            return "resume"
        if self.btn_table.draw(screen):
            return "table"
        if self.btn_quit.draw(screen):
            return "quit"
            
        return None