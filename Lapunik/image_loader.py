import pygame
import os
from settings import *

class ImageLoader:
    def __init__(self):
        self.images = {}
        self.load_images()
        
    def load_images(self):
        """Načte všechny obrázky z assets složky"""
        try:
            if not os.path.exists('assets/images'):
                print("❌ CHYBA: Složka 'assets/images' neexistuje!")
                os.makedirs('assets/images', exist_ok=True)
                print("✅ Vytvořena složka assets/images")
                return
                
            print("Načítám obrázky z assets...")
            
            # POZADÍ - MENU (zkusíme všechny možné formáty)
            menu_background_paths = [
                'assets/images/menu_background.jpg',
                'assets/images/menu_background.png',
                'assets/images/menu_background.bmp',
                'assets/images/background.jpg',
                'assets/images/background.png'
            ]
            self.images['menu_background'] = self.load_background_image(menu_background_paths, "menu pozadí")
            
            # POZADÍ - LEVEL 1
            level1_paths = [
                'assets/images/level_1.png',
                'assets/images/level_1.jpg'
            ]
            self.images['level_1'] = self.load_background_image(level1_paths, "level 1 pozadí")
            
            # HRÁČ - lučištník
            player_paths = [
                'assets/images/archer.png',
                'assets/images/player.png'
            ]
            self.images['archer'] = self.load_first_available(player_paths, "hráče", alpha=True)
            
            # ŠÍP - pro hráče
            arrow_paths = [
                'assets/images/arrow.png'
            ]
            self.images['arrow'] = self.load_first_available(arrow_paths, "šíp", alpha=True)
            
            # OŠTĚP - pro gobliny
            spear_paths = [
                'assets/images/spear.png'
            ]
            self.images['spear'] = self.load_first_available(spear_paths, "oštěp", alpha=True)
            
            # GOBLINI
            self.load_goblin_animations()
            
            # HRÁČ - animace
            self.load_player_animations()
            
            print("✅ Všechny obrázky úspěšně načteny!")
            
        except Exception as e:
            print(f"❌ CHYBA při načítání obrázků: {e}")
            self.create_fallback_images()
    
    def load_background_image(self, paths, description):
        """Speciální načítání pro pozadí"""
        for path in paths:
            print(f"🔍 Kontroluji pozadí: {path}")
            print(f"📁 Soubor existuje: {os.path.exists(path)}")
            if os.path.exists(path):
                try:
                    # Načti obrázek
                    image = pygame.image.load(path)
                    print(f"📏 Velikost {description}: {image.get_size()}")
                    
                    # Konvertuj pro lepší výkon
                    image = image.convert()
                    print(f"✅ Načteno {description}: {os.path.basename(path)}")
                    return image
                except pygame.error as e:
                    print(f"❌ Chyba při načítání {path}: {e}")
        
        print(f"❌ CHYBA: Nenalezen žádný soubor pro {description}, vytvářím fallback")
        return self.create_fallback_background()
    
    def create_fallback_background(self):
        """Vytvoří fallback pozadí"""
        fallback = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        # Vytvoř hezký gradient
        for y in range(SCREEN_HEIGHT):
            # Tmavě zelený gradient
            green = 50 + int(100 * y / SCREEN_HEIGHT)
            blue = 30 + int(50 * y / SCREEN_HEIGHT)
            color = (0, green, blue)
            pygame.draw.line(fallback, color, (0, y), (SCREEN_WIDTH, y))
        
        # Přidej nějaké detaily
        for x in range(100, SCREEN_WIDTH, 200):
            # Stromy
            pygame.draw.rect(fallback, BROWN, (x, SCREEN_HEIGHT - 150, 25, 120))
            pygame.draw.circle(fallback, FOREST_GREEN, (x + 12, SCREEN_HEIGHT - 160), 45)
        
        print("✅ Vytvořeno fallback pozadí")
        return fallback.convert()
    
    def create_fallback_images(self):
        """Vytvoří fallback obrázky pokud se nic nenačte"""
        print("🔄 Vytvářím fallback obrázky...")
        self.images['menu_background'] = self.create_fallback_background()
        self.images['level_1'] = self.create_fallback_background()
    
    def load_goblin_animations(self):
        """Načte 2 animační snímky pro gobliny"""
        enemy_types = ['basic', 'strong', 'mega_goblin']
        
        for enemy_type in enemy_types:
            frames_loaded = 0
            for i in range(1, 3):
                if enemy_type == "mega_goblin":
                    frame_name = f'mega_goblin_{i}.png'
                else:
                    frame_name = f'goblin_{enemy_type}_{i}.png'
                    
                frame_path = f'assets/images/goblins/{frame_name}'
                
                if os.path.exists(frame_path):
                    try:
                        self.images[frame_name] = pygame.image.load(frame_path).convert_alpha()
                        frames_loaded += 1
                        print(f"✓ Načten {enemy_type} frame {i}")
                    except pygame.error as e:
                        print(f"✗ Chyba při načítání {frame_path}: {e}")
                        self.create_fallback_goblin(frame_name, enemy_type)
                else:
                    print(f"❌ CHYBA: Soubor neexistuje: {frame_path}")
                    self.create_fallback_goblin(frame_name, enemy_type)
                    frames_loaded += 1
            
            print(f"✓ {enemy_type}: {frames_loaded}/2 snímků načteno")
    
    def create_fallback_goblin(self, frame_name, enemy_type):
        """Vytvoří fallback goblina"""
        colors = {'basic': GREEN, 'strong': ORANGE, 'mega_goblin': RED}
        color = colors.get(enemy_type, GREEN)
        
        surface = pygame.Surface((45, 50), pygame.SRCALPHA)
        # Tělo
        pygame.draw.ellipse(surface, color, (5, 10, 35, 30))
        # Hlava
        pygame.draw.circle(surface, color, (22, 15), 10)
        # Oči
        pygame.draw.circle(surface, WHITE, (18, 13), 3)
        pygame.draw.circle(surface, WHITE, (26, 13), 3)
        
        self.images[frame_name] = surface
        print(f"✅ Vytvořen fallback {frame_name}")
    
    def load_player_animations(self):
        """Načte animace pro hráče"""
        print("Načítám animace hráče...")
        
        animation_types = ['idle', 'walk_left', 'walk_right', 'shoot']
        frame_counts = {'idle': 2, 'walk_left': 2, 'walk_right': 2, 'shoot': 2}
        
        for anim_type in animation_types:
            frames_loaded = 0
            for i in range(1, frame_counts[anim_type] + 1):
                frame_name = f'player_{anim_type}_{i}.png'
                frame_path = f'assets/images/player/{frame_name}'
                
                if os.path.exists(frame_path):
                    try:
                        self.images[frame_name] = pygame.image.load(frame_path).convert_alpha()
                        frames_loaded += 1
                        print(f"✓ Načten {anim_type} frame {i}")
                    except pygame.error as e:
                        print(f"✗ Chyba při načítání {frame_path}: {e}")
                        self.create_fallback_player(frame_name, anim_type)
                else:
                    print(f"❌ CHYBA: Soubor neexistuje: {frame_path}")
                    self.create_fallback_player(frame_name, anim_type)
                    frames_loaded += 1
            
            print(f"✓ {anim_type}: {frames_loaded}/{frame_counts[anim_type]} snímků")
    
    def create_fallback_player(self, frame_name, anim_type):
        """Vytvoří fallback hráče"""
        surface = pygame.Surface((50, 70), pygame.SRCALPHA)
        
        # Tělo - různé pozice podle animace
        if 'walk_left' in anim_type:
            # Nakloněný doleva
            pygame.draw.ellipse(surface, BLUE, (15, 20, 20, 40))
            pygame.draw.circle(surface, BLUE, (25, 15), 12)
        elif 'walk_right' in anim_type:
            # Nakloněný doprava
            pygame.draw.ellipse(surface, BLUE, (15, 20, 20, 40))
            pygame.draw.circle(surface, BLUE, (25, 15), 12)
        elif 'shoot' in anim_type:
            # Střelecká pozice
            pygame.draw.ellipse(surface, BLUE, (15, 20, 20, 40))
            pygame.draw.circle(surface, BLUE, (25, 15), 12)
            # Luk
            pygame.draw.arc(surface, BROWN, (30, 20, 20, 15), 0, 3.14, 3)
        else:
            # Idle - rovně
            pygame.draw.ellipse(surface, BLUE, (15, 20, 20, 40))
            pygame.draw.circle(surface, BLUE, (25, 15), 12)
        
        self.images[frame_name] = surface
        print(f"✅ Vytvořen fallback {frame_name}")
    
    def load_first_available(self, paths, description, alpha=False):
        """Načte první dostupný soubor ze seznamu"""
        for path in paths:
            if os.path.exists(path):
                try:
                    if alpha:
                        image = pygame.image.load(path).convert_alpha()
                    else:
                        image = pygame.image.load(path).convert()
                    print(f"✅ Načten {description}: {os.path.basename(path)}")
                    return image
                except pygame.error as e:
                    print(f"❌ Chyba při načítání {path}: {e}")
        
        print(f"❌ CHYBA: Nenalezen žádný soubor pro {description}")
        return None
        
    def get_image(self, name):
        """Vrátí obrázek podle názvu"""
        image = self.images.get(name, None)
        if image is None:
            print(f"⚠️ Obrázek '{name}' nebyl nalezen v image loaderu")
        return image
    
    def get_level_background(self, level_number):
        """Vrátí pozadí pro daný level"""
        level_name = f'level_{level_number}'
        background = self.images.get(level_name)
        if background is None:
            print(f"⚠️ Pozadí pro level {level_number} nebylo nalezeno, používám menu pozadí")
            background = self.images.get('menu_background')
        return background
    
    def get_menu_background(self):
        """Vrátí pozadí pro menu"""
        background = self.images.get('menu_background')
        if background is None:
            print("⚠️ Menu pozadí nebylo nalezeno, vytvářím fallback")
            background = self.create_fallback_background()
            self.images['menu_background'] = background
        return background