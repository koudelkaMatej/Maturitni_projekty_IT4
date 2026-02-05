import pygame
import random
from settings import *
from animations import Animation, DeathAnimation

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, enemy_type="basic", image_loader=None):
        super().__init__()
        self.enemy_type = enemy_type
        self.image_loader = image_loader
        
        # Animace
        self.animation = Animation(image_loader, enemy_type)
        self.image = self.animation.get_current_frame()
        
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.speed = ENEMY_SPEED
        self.direction = 1
        self.health = self.get_health_by_type()
        self.score_value = self.get_score_by_type()
        
        # Pro death animaci
        self.death_animation = None
        self.is_dying = False
        
    def get_health_by_type(self):
        health_map = {"basic": 1, "strong": 2, "mega_goblin": 5}  # ZMĚNA: boss -> mega_goblin
        return health_map.get(self.enemy_type, 1)
        
    def get_score_by_type(self):
        score_map = {"basic": SCORE_ENEMY_BASIC, "strong": SCORE_ENEMY_STRONG, "mega_goblin": SCORE_ENEMY_BOSS}  # ZMĚNA: boss -> mega_goblin
        return score_map.get(self.enemy_type, SCORE_ENEMY_BASIC)
    
    def update(self):
        if self.is_dying:
            if self.death_animation:
                self.death_animation.update()
                if self.death_animation.is_finished():
                    self.kill()
            return
            
        # Normální pohyb
        self.rect.x += self.speed * self.direction
        
        # Aktualizace animace
        self.animation.update()
        self.image = self.animation.get_current_frame()
        
    def reverse_and_drop(self):
        self.direction *= -1
        self.rect.y += 20
        
    def hit(self):
        """Vrátí True pokud je nepřítel zničen"""
        self.health -= 1
        if self.health <= 0:
            self.start_death_animation()
            return True
        return False
    
    def start_death_animation(self):
        """Spustí animaci smrti"""
        self.is_dying = True
        self.death_animation = DeathAnimation(self.rect.centerx, self.rect.centery)
    
    def draw_death_animation(self, screen):
        """Vykreslí death animaci"""
        if self.death_animation:
            self.death_animation.draw(screen)