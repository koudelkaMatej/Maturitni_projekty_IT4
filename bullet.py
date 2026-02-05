import pygame
from settings import *

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, direction=1, image_loader=None, is_player_bullet=True):
        super().__init__()
        self.image_loader = image_loader
        self.is_player_bullet = is_player_bullet
        self.direction = direction
        
        # Vytvoříme základní sprite
        if is_player_bullet:
            self.original_image = self.create_arrow_sprite()
        else:
            self.original_image = self.create_spear_sprite()
            
        # Aplikujeme rotaci podle směru
        if direction == -1:  # Střela letí dolů
            self.image = pygame.transform.rotate(self.original_image, 180)
        else:  # Střela letí nahoru
            self.image = self.original_image
            
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.centery = y
        self.speed = BULLET_SPEED * direction
        self.damage = 1
        
    def create_arrow_sprite(self):
        """Vytvoří šíp orientovaný špičkou nahoru"""
        surface = pygame.Surface((8, 16), pygame.SRCALPHA)  # Použijeme průhlednost
        
        # Tělo šípu - svisle
        pygame.draw.line(surface, BROWN, (4, 4), (4, 12), 3)
        
        # Hrot šípu - nahoru
        hrot_points = [
            (4, 0),    # Špička
            (1, 4),    # Levý základ
            (7, 4)     # Pravý základ
        ]
        pygame.draw.polygon(surface, GRAY, hrot_points)
        
        # Peří - dole
        pygame.draw.line(surface, WHITE, (4, 12), (1, 15), 2)
        pygame.draw.line(surface, WHITE, (4, 12), (7, 15), 2)
        
        return surface
        
    def create_spear_sprite(self):
        """Vytvoří oštěp orientovaný špičkou nahoru"""
        surface = pygame.Surface((6, 18), pygame.SRCALPHA)  # Použijeme průhlednost
        
        # Tělo oštěpu - svisle
        pygame.draw.line(surface, BROWN, (3, 2), (3, 16), 3)
        
        # Hrot oštěpu - nahoru
        hrot_points = [
            (3, 0),    # Špička
            (1, 3),    # Levý základ
            (5, 3)     # Pravý základ
        ]
        pygame.draw.polygon(surface, GRAY, hrot_points)
        
        return surface
        
    def update(self):
        """Aktualizuje pozici střely"""
        self.rect.y -= self.speed
        
        # Smazat pokud vyjde z obrazovky
        if self.rect.bottom < 0 or self.rect.top > SCREEN_HEIGHT:
            self.kill()