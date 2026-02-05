import pygame
import random
from settings import *

class Animation:
    def __init__(self, image_loader, enemy_type):
        self.image_loader = image_loader
        self.enemy_type = enemy_type
        self.frames = []
        self.current_frame = 0
        self.animation_speed = 0.3
        self.last_update = pygame.time.get_ticks()
        self.load_animation_frames()
        
    def load_animation_frames(self):
        """Načte 2 snímky animace chůze"""
        frame_count = 2
        
        for i in range(frame_count):
            if self.enemy_type == "mega_goblin":
                frame_name = f'mega_goblin_{i+1}.png'
            else:
                frame_name = f'goblin_{self.enemy_type}_{i+1}.png'
                
            frame = self.image_loader.get_image(frame_name)
            if frame:
                self.frames.append(frame)
            else:
                print(f"❌ CHYBA: Nelze načíst {frame_name}")
                # Přidáme prázdný surface
                empty_surface = pygame.Surface(self.get_size_by_type(), pygame.SRCALPHA)
                self.frames.append(empty_surface)
    
    def get_size_by_type(self):
        sizes = {"basic": (45, 50), "strong": (45, 45), "mega_goblin": (50, 40)}
        return sizes.get(self.enemy_type, (45, 50))
    
    def update(self):
        """Aktualizuje aktuální snímek animace"""
        now = pygame.time.get_ticks()
        if now - self.last_update > self.animation_speed * 1000:
            self.last_update = now
            self.current_frame = (self.current_frame + 1) % len(self.frames)
    
    def get_current_frame(self):
        """Vrátí aktuální snímek animace"""
        if self.frames:
            return self.frames[self.current_frame]
        return None


class PlayerAnimation:
    def __init__(self, image_loader):
        self.image_loader = image_loader
        self.frames = {
            'idle': [],
            'walk_left': [],
            'walk_right': [],
            'shoot': []
        }
        self.current_animation = 'idle'
        self.current_frame = 0
        self.animation_speeds = {
            'idle': 0.8,
            'walk_left': 0.2,
            'walk_right': 0.2,
            'shoot': 0.15
        }
        self.last_update = pygame.time.get_ticks()
        self.facing_direction = 1
        self.load_animations()
        
    def load_animations(self):
        """Načte animace pro hráče"""
        # Idle - 2 snímky
        self.load_frames('idle', 2)
        # Chůze doleva - 2 snímky
        self.load_frames('walk_left', 2)
        # Chůze doprava - 2 snímky
        self.load_frames('walk_right', 2)
        # Střelba - 2 snímky
        self.load_frames('shoot', 2)
        
    def load_frames(self, animation_name, frame_count):
        """Načte obrázky - ŽÁDNÝ FALLBACK"""
        for i in range(frame_count):
            frame_name = f'player_{animation_name}_{i+1}.png'
            frame = self.image_loader.get_image(frame_name)
            
            if frame:
                self.frames[animation_name].append(frame)
            else:
                print(f"❌ CHYBA: Nelze načíst {frame_name}")
                # Přidáme prázdný surface
                empty_surface = pygame.Surface((50, 70), pygame.SRCALPHA)
                self.frames[animation_name].append(empty_surface)
    
    def set_animation(self, animation_name):
        """Nastaví aktuální animaci"""
        if animation_name != self.current_animation:
            self.current_animation = animation_name
            self.current_frame = 0
            self.last_update = pygame.time.get_ticks()
    
    def set_facing_direction(self, direction):
        """Nastaví směr, kterým hráč čelí"""
        self.facing_direction = direction
    
    def update(self, moving_left=False, moving_right=False, shooting=False):
        """Aktualizuje animaci na základě akcí hráče"""
        now = pygame.time.get_ticks()
        
        # Určení správné animace
        if shooting:
            self.set_animation('shoot')
        elif moving_left:
            self.set_animation('walk_left')
            self.set_facing_direction(-1)
        elif moving_right:
            self.set_animation('walk_right') 
            self.set_facing_direction(1)
        else:
            self.set_animation('idle')
        
        # Aktualizace framu s různou rychlostí pro různé animace
        current_speed = self.animation_speeds[self.current_animation]
        if now - self.last_update > current_speed * 1000:
            self.last_update = now
            current_frames = self.frames[self.current_animation]
            if current_frames:
                self.current_frame = (self.current_frame + 1) % len(current_frames)
    
    def get_current_frame(self):
        """Vrátí aktuální snímek animace"""
        current_frames = self.frames[self.current_animation]
        if current_frames:
            return current_frames[self.current_frame]
        return None
    
    def is_shoot_animation_finished(self):
        """Vrátí True pokud animace střelby skončila"""
        if self.current_animation == 'shoot':
            current_frames = self.frames['shoot']
            return self.current_frame >= len(current_frames) - 1
        return True


class DeathAnimation:
    def __init__(self, x, y):
        self.particles = []
        self.x = x
        self.y = y
        self.create_particles()
        self.lifetime = 500
        self.created_time = pygame.time.get_ticks()
        
    def create_particles(self):
        """Vytvoří částice pro explozi"""
        for _ in range(15):
            particle = {
                'x': self.x,
                'y': self.y,
                'dx': random.uniform(-3, 3),
                'dy': random.uniform(-3, 3),
                'size': random.randint(2, 6),
                'color': random.choice([RED, ORANGE, YELLOW])
            }
            self.particles.append(particle)
    
    def update(self):
        """Aktualizuje částice"""
        for particle in self.particles:
            particle['x'] += particle['dx']
            particle['y'] += particle['dy']
            particle['dy'] += 0.1
    
    def draw(self, screen):
        """Vykreslí částice"""
        for particle in self.particles:
            pygame.draw.circle(
                screen, 
                particle['color'],
                (int(particle['x']), int(particle['y'])),
                particle['size']
            )
    
    def is_finished(self):
        """Vrátí True pokud animace skončila"""
        return pygame.time.get_ticks() - self.created_time > self.lifetime