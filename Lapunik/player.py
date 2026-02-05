import pygame
from settings import *
from animations import PlayerAnimation  # ZMĚNA: místo player_animations

class Player(pygame.sprite.Sprite):
    def __init__(self, image_loader=None):
        super().__init__()
        self.image_loader = image_loader
        
        # Animace
        self.animation = PlayerAnimation(image_loader)
        self.image = self.animation.get_current_frame()
        
        self.rect = self.image.get_rect()
        self.rect.centerx = SCREEN_WIDTH // 2
        self.rect.bottom = SCREEN_HEIGHT - 20
        self.speed = PLAYER_SPEED
        self.health = PLAYER_HEALTH
        
        # Střelba
        self.last_shot = pygame.time.get_ticks()
        self.shoot_cooldown = PLAYER_SHOOT_COOLDOWN
        self.is_shooting = False
        
        # Stav pohybu
        self.moving_left = False
        self.moving_right = False
        
        # Nezranitelnost
        self.invulnerable = False
        self.invulnerable_timer = 0
        
    def update(self):
        """Aktualizuje pozici a animaci hráče"""
        keys = pygame.key.get_pressed()
        
        # Reset pohybových stavů
        self.moving_left = False
        self.moving_right = False
        
        # Pohyb doleva/doprava
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.rect.x -= self.speed
            self.moving_left = True
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.rect.x += self.speed
            self.moving_right = True
            
        # Drž hráče na obrazovce
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
            
        # Aktualizace animace
        self.animation.update(
            moving_left=self.moving_left,
            moving_right=self.moving_right,
            shooting=self.is_shooting
        )
        
        # Získání aktuálního snímku
        self.image = self.animation.get_current_frame()
        
        # Reset střelby pokud animace skončila
        if self.is_shooting and self.animation.is_shoot_animation_finished():
            self.is_shooting = False
            
        # Aktualizace nezranitelnosti
        if self.invulnerable:
            now = pygame.time.get_ticks()
            if now - self.invulnerable_timer > 1000:
                self.invulnerable = False
                
        # Blikání při nezranitelnosti
        if self.invulnerable:
            if pygame.time.get_ticks() % 200 < 100:
                self.image.set_alpha(128)
            else:
                self.image.set_alpha(255)
        else:
            self.image.set_alpha(255)
            
    def shoot(self):
        """Vrátí True pokud může střílet a spustí animaci střelby"""
        now = pygame.time.get_ticks()
        if now - self.last_shot > self.shoot_cooldown and not self.is_shooting:
            self.last_shot = now
            self.is_shooting = True
            self.animation.set_animation('shoot')
            return True
        return False
        
    def take_damage(self, damage=10):
        """Udělí poškození hráči, pokud není nezranitelný"""
        if not self.invulnerable:
            self.health -= damage
            self.invulnerable = True
            self.invulnerable_timer = pygame.time.get_ticks()
            return True
        return False
        
    def heal(self, amount=25):
        """Vyléčí hráče"""
        self.health = min(PLAYER_HEALTH, self.health + amount)