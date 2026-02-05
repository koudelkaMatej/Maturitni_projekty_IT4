import pygame
import sys
import random
import mysql.connector
from mysql.connector import Error
from datetime import datetime

# Inicializace Pygame
pygame.init()

# Konstanty
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
coins = 0
customers = None
spawn_timer = 0
beer_amount = 60
wine_amount = 60
drink_amount = 60
beer_max = 10
wine_max = 10
drink_max = 10
stress_level = 0
stress_max = 100
game_over = False
player_name = ""
selected_customer = None  # Pro vybraného zákazníka
customer_positions = []  # Pro sledování obsazených pozic zákazníků


DB_CONFIG = {
    'host': 'dbs.spskladno.cz',
    'user': 'student19',
    'password': 'spsnet',  
    'database': 'vyuka19', 
    'port': 3306
}

# Barvy
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
LIGHT_GRAY = (230, 230, 230)
GREEN = (0, 200, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
BLUE = (0, 120, 255)
BEER_COLOR = (255, 206, 0)
WINE_COLOR = (128, 0, 64)
DRINK_COLOR = (255, 140, 0)
STRESS_COLOR = (150, 50, 150)
GOLD = (255, 215, 0)
SILVER = (192, 192, 192)
BRONZE = (205, 127, 50)
SELECTED_COLOR = (100, 200, 255, 150)  # Průhledná modrá pro výběr

# Nastavení obrazovky
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Ježkův bar - Databázová verze")
clock = pygame.time.Clock()

# Načtení pozadí
try:
    background = pygame.image.load("wall.png")
    background = pygame.transform.scale(background, (SCREEN_WIDTH, SCREEN_HEIGHT))
except:
    background = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    background.fill((100, 100, 100))

# Načtení obrázku titulku
try:
    title_image = pygame.image.load("title.png")
    title_image = pygame.transform.scale(title_image, (650, 270))  
except:
    title_image = None

# Načtení obrázků zákazníků
customer_images = []
for i in range(1, 4):
    try:
        img = pygame.image.load(f"customer{i}.png")
        img = pygame.transform.scale(img, (215, 160))  # velikost zákazníka
        customer_images.append(img)
    except:
        # Fallback na barevný čtverec pokud obrázek neexistuje
        img = pygame.Surface((150, 150))
        if i == 1:
            img.fill((150, 150, 150))  # Šedá
        elif i == 2:
            img.fill((200, 150, 150))  # Růžová
        elif i == 3:
            img.fill((150, 200, 150))  # Zelená
        customer_images.append(img)

# Fonty
font = pygame.font.SysFont('Arial', 40)
small_font = pygame.font.SysFont('Arial', 30)
tiny_font = pygame.font.SysFont('Arial', 20)

# Hlasitost
volume = 0.5
pygame.mixer.init()
pygame.mixer.music.set_volume(volume)

# Fullscreen stav
fullscreen = False

class InputBox:
    def __init__(self, x, y, w, h, text=''):
        self.rect = pygame.Rect(x, y, w, h)
        self.color = BLACK
        self.text = text
        self.txt_surface = small_font.render(text, True, self.color)
        self.active = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.active = not self.active
            else:
                self.active = False
            self.color = BLUE if self.active else BLACK
        
        if event.type == pygame.KEYDOWN:
            if self.active:
                if event.key == pygame.K_RETURN:
                    return self.text
                elif event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    if len(self.text) < 20:  # Omezení délky jména
                        self.text += event.unicode
                self.txt_surface = small_font.render(self.text, True, self.color)
        return None

    def update(self):
        width = max(200, self.txt_surface.get_width()+10)
        self.rect.w = width

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect, 2)
        screen.blit(self.txt_surface, (self.rect.x+5, self.rect.y+5))

class Button:
    def __init__(self, x, y, width, height, text, action=None, color=GRAY):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.action = action
        self.is_hovered = False
        self.base_color = color
        self.hover_color = (min(color[0] + 30, 255), min(color[1] + 30, 255), min(color[2] + 30, 255))
        self.disabled_color = (color[0]//2, color[1]//2, color[2]//2)
        self.enabled = True

    def draw(self, surface):
        if not self.enabled:
            color = self.disabled_color
        elif self.is_hovered:
            color = self.hover_color
        else:
            color = self.base_color
        
        pygame.draw.rect(surface, color, self.rect)
        pygame.draw.rect(surface, BLACK, self.rect, 2)
        
        text_surf = small_font.render(self.text, True, BLACK)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def check_hover(self, pos):
        self.is_hovered = self.rect.collidepoint(pos)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos) and self.enabled:
                if self.action:
                    return self.action
        return None

class HoldButton(Button):
    """Tlačítko, které vyžaduje držení po určitou dobu"""
    def __init__(self, x, y, width, height, text, action=None, color=GRAY, hold_time=1.0):
        super().__init__(x, y, width, height, text, action, color)
        self.hold_time = hold_time  # Čas v sekundách
        self.press_start_time = None
        self.is_pressed = False
    
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos) and self.enabled:
                self.press_start_time = pygame.time.get_ticks()
                self.is_pressed = True
        elif event.type == pygame.MOUSEBUTTONUP:
            self.is_pressed = False
            self.press_start_time = None
        return None
    
    def check_hold_complete(self):
        """Vrátí True pokud bylo tlačítko drženo dostatečně dlouho"""
        if self.is_pressed and self.press_start_time is not None:
            elapsed = (pygame.time.get_ticks() - self.press_start_time) / 1000.0
            if elapsed >= self.hold_time:
                self.press_start_time = None
                self.is_pressed = False
                return True
        return False
    
    def get_hold_progress(self):
        """Vrátí pokrok držení (0.0 až 1.0)"""
        if self.is_pressed and self.press_start_time is not None:
            elapsed = (pygame.time.get_ticks() - self.press_start_time) / 1000.0
            return min(1.0, elapsed / self.hold_time)
        return 0.0
    
    def draw(self, surface):
        # Vykresli normální tlačítko
        if not self.enabled:
            color = self.disabled_color
        elif self.is_hovered:
            color = self.hover_color
        else:
            color = self.base_color
        
        pygame.draw.rect(surface, color, self.rect)
        
        # Vykresli progress bar 
        if self.is_pressed:
            progress = self.get_hold_progress()
            progress_width = self.rect.width * progress
            pygame.draw.rect(surface, GREEN, (self.rect.x, self.rect.y + self.rect.height - 4, progress_width, 4))
        
        pygame.draw.rect(surface, BLACK, self.rect, 2)
        
        text_surf = small_font.render(self.text, True, BLACK)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

class Slider:
    def __init__(self, x, y, width, min_val=0.0, max_val=1.0, start_val=0.5):
        self.rect = pygame.Rect(x, y, width, 10)
        self.min_val = min_val
        self.max_val = max_val
        self.value = start_val
        self.handle_x = x + width * ((start_val - min_val) / (max_val - min_val))
        self.dragging = False

    def draw(self, surface):
        pygame.draw.rect(surface, GRAY, self.rect)
        handle_rect = pygame.Rect(self.handle_x - 8, self.rect.centery - 8, 16, 16)
        pygame.draw.circle(surface, GREEN if self.dragging else BLACK, handle_rect.center, 8)
        vol_text = small_font.render(f"Hlasitost: {int(self.value * 100)}%", True, BLACK)
        surface.blit(vol_text, (self.rect.x, self.rect.y - 40))

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if abs(event.pos[0] - self.handle_x) < 15 and abs(event.pos[1] - self.rect.centery) < 15:
                self.dragging = True
        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            self.handle_x = max(self.rect.x, min(event.pos[0], self.rect.x + self.rect.width))
            self.value = self.min_val + (self.max_val - self.min_val) * ((self.handle_x - self.rect.x) / self.rect.width)
            pygame.mixer.music.set_volume(self.value)

class Customer:
    def __init__(self, x, y):
        self.drink_type = random.randint(0, 2)  # 0=pivo, 1=víno, 2=drink
        self.image = customer_images[self.drink_type]
        self.rect = self.image.get_rect(center=(x, y))
        self.served = False
        self.arrival_time = pygame.time.get_ticks()
        self.selected = False

    def draw(self, surface):
        if not self.served:
            surface.blit(self.image, self.rect)
            # Označení vybraného zákazníka
            if self.selected:
                highlight = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
                highlight.fill((100, 200, 255, 100))
                surface.blit(highlight, self.rect)

    def handle_click(self, pos):
        global selected_customer
        if not self.served and self.rect.collidepoint(pos):
            # Zruš výběr předchozího zákazníka
            if selected_customer:
                selected_customer.selected = False
            # Vyber tohoto zákazníka
            self.selected = True
            selected_customer = self
            return True
        return False

    def serve(self):
        global coins, beer_amount, wine_amount, drink_amount, stress_level, selected_customer
        if self.served:
            return False
        
        drink_available = False
        if self.drink_type == 0 and beer_amount > 0:
            beer_amount -= 1
            drink_available = True
        elif self.drink_type == 1 and wine_amount > 0:
            wine_amount -= 1
            drink_available = True
        elif self.drink_type == 2 and drink_amount > 0:
            drink_amount -= 1
            drink_available = True
        
        if drink_available:
            self.served = True
            self.selected = False
            selected_customer = None
            coins += 15
            stress_level = max(0, stress_level - 20)
            return True
        else:
            # Nemáme nápoj - zvýšíme stres
            stress_level = min(stress_max, stress_level + 1)
            return False

def connect_to_database():
    """Vytvoření připojení k databázi"""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        if connection.is_connected():
            return connection
    except Error as e:
        print(f"Chyba připojení k databázi: {e}")
        return None

def create_table():
    """Vytvoření tabulek pro skóre a achievmenty pokud neexistují"""
    connection = connect_to_database()
    if connection:
        try:
            cursor = connection.cursor()
            # Tabulka skóre
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS scores (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    player_name VARCHAR(50) NOT NULL,
                    score INT NOT NULL,
                    game_date DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Tabulka achievementů
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS achievements (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    description TEXT NOT NULL,
                    required_score INT NOT NULL,
                    color VARCHAR(20) DEFAULT 'GRAY'
                )
            """)
            
            # Vazební tabulka M:N mezi hráči a achievementy
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS player_achievements (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    player_name VARCHAR(50) NOT NULL,
                    achievement_id INT NOT NULL,
                    achieved_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (achievement_id) REFERENCES achievements(id)
                )
            """)
            
            # Vložení výchozích achievementů, pokud tabulka je prázdná
            cursor.execute("SELECT COUNT(*) FROM achievements")
            if cursor.fetchone()[0] == 0:
                default_achievements = [
                    ("Prvních 100", "Dosáhněte 100 bodů", 100, "BRONZE"),
                    ("500 bodů", "Dosáhněte 500 bodů", 500, "SILVER"),
                    ("Tisícovka", "Dosáhněte 1000 bodů", 1000, "GOLD"),
                    ("Mistr barmana", "Dosáhněte 5000 bodů", 5000, "GOLD"),
                    ("Legendární barman", "Dosáhněte 10000 bodů", 10000, "GOLD"),
                    ("Začátečník", "Dosáhněte 50 bodů", 50, "GRAY"),
                    ("Průměrný hráč", "Dosáhněte 250 bodů", 250, "BRONZE"),
                    ("Zkušený barman", "Dosáhněte 2000 bodů", 2000, "SILVER")
                ]
                
                insert_query = "INSERT INTO achievements (name, description, required_score, color) VALUES (%s, %s, %s, %s)"
                cursor.executemany(insert_query, default_achievements)
            
            connection.commit()
            cursor.close()
        except Error as e:
            print(f"Chyba při vytváření tabulek: {e}")
        finally:
            if connection.is_connected():
                connection.close()

def save_score_to_db(name, score):
    """Uložení skóre do databáze a kontrola achievementů"""
    connection = connect_to_database()
    if connection:
        try:
            cursor = connection.cursor()
            # Uložení skóre
            sql = "INSERT INTO scores (player_name, score) VALUES (%s, %s)"
            values = (name[:50], score)
            cursor.execute(sql, values)
            
            # Kontrola a udělení achievementů
            check_and_grant_achievements(name, score, cursor)
            
            connection.commit()
            cursor.close()
            return True
        except Error as e:
            print(f"Chyba při ukládání skóre: {e}")
            return False
        finally:
            if connection.is_connected():
                connection.close()
    return False

def check_and_grant_achievements(player_name, score, cursor):
    """Kontroluje a uděluje achievementy podle dosaženého skóre"""
    # Najdi achievementy, které hráč ještě nemá a jejichž požadavek splňuje
    query = """
        SELECT a.id, a.name 
        FROM achievements a 
        WHERE a.required_score <= %s 
        AND a.id NOT IN (
            SELECT pa.achievement_id 
            FROM player_achievements pa 
            WHERE pa.player_name = %s
        )
    """
    cursor.execute(query, (score, player_name))
    new_achievements = cursor.fetchall()
    
    # Uděl nové achievementy
    for achievement_id, achievement_name in new_achievements:
        insert_query = "INSERT INTO player_achievements (player_name, achievement_id) VALUES (%s, %s)"
        cursor.execute(insert_query, (player_name, achievement_id))
        print(f"Hráč {player_name} získal achievement: {achievement_name}")

def get_top_scores(limit=10):
    """Získání nejlepších skóre z databáze"""
    connection = connect_to_database()
    if connection:
        try:
            cursor = connection.cursor()
            cursor.execute(f"SELECT player_name, score, game_date FROM scores ORDER BY score DESC LIMIT {limit}")
            scores = cursor.fetchall()
            cursor.close()
            return scores
        except Error as e:
            print(f"Chyba při načítání skóre: {e}")
            return []
        finally:
            if connection.is_connected():
                connection.close()
    return []

def get_player_achievements(player_name):
    """Získání achievementů konkrétního hráče"""
    connection = connect_to_database()
    if connection:
        try:
            cursor = connection.cursor()
            query = """
                SELECT a.name, a.description, a.required_score, a.color, pa.achieved_date
                FROM achievements a
                JOIN player_achievements pa ON a.id = pa.achievement_id
                WHERE pa.player_name = %s
                ORDER BY a.required_score DESC
            """
            cursor.execute(query, (player_name,))
            achievements = cursor.fetchall()
            cursor.close()
            return achievements
        except Error as e:
            print(f"Chyba při načítání achievementů: {e}")
            return []
        finally:
            if connection.is_connected():
                connection.close()
    return []

def get_all_achievements():
    """Získání všech možných achievementů s informací, zda je hráč má"""
    connection = connect_to_database()
    if connection:
        try:
            cursor = connection.cursor()
            query = """
                SELECT a.id, a.name, a.description, a.required_score, a.color,
                    CASE WHEN pa.player_name IS NOT NULL THEN TRUE ELSE FALSE END as unlocked
                FROM achievements a
                LEFT JOIN player_achievements pa ON a.id = pa.achievement_id AND pa.player_name = %s
                ORDER BY a.required_score ASC
            """
            cursor.execute(query, (player_name,))
            achievements = cursor.fetchall()
            cursor.close()
            return achievements
        except Error as e:
            print(f"Chyba při načítání všech achievementů: {e}")
            return []
        finally:
            if connection.is_connected():
                connection.close()
    return []

def save_name_scene():
    """Scéna pro zadání jména po game over"""
    global player_name
    input_box = InputBox(300, 200, 200, 40, player_name)
    save_button = Button(300, 300, 200, 50, "Uložit skóre", "save_score")
    skip_button = Button(300, 370, 200, 50, "Přeskočit", "score")
    
    while True:
        mouse_pos = pygame.mouse.get_pos()
        current_state = None
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return "score"
            
            # Zpracování input boxu
            result = input_box.handle_event(event)
            if result is not None:
                player_name = result
            
            # Tlačítka
            if event.type == pygame.MOUSEMOTION:
                save_button.check_hover(mouse_pos)
                skip_button.check_hover(mouse_pos)
            
            result = save_button.handle_event(event)
            if result == "save_score":
                if input_box.text.strip():
                    player_name = input_box.text.strip()
                    save_score_to_db(player_name, coins)
                return "score"
            
            result = skip_button.handle_event(event)
            if result == "score":
                return "score"
        
        # Vykreslení
        screen.fill(WHITE)
        title = font.render("Zadejte své jméno", True, BLACK)
        screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 100))
        
        info_text = small_font.render(f"Vaše skóre: {coins}", True, BLACK)
        screen.blit(info_text, (SCREEN_WIDTH//2 - info_text.get_width()//2, 150))
        
        input_box.draw(screen)
        save_button.draw(screen)
        skip_button.draw(screen)
        
        pygame.display.flip()
        clock.tick(FPS)

def settings_scene():
    global fullscreen, screen

    back_button = Button(300, 500, 200, 50, "Menu", "main_menu")
    fullscreen_button = Button(300, 400, 200, 50, "Přepnout fullscreen", "toggle_fullscreen")
    slider = Slider(250, 300, 300, 0.0, 1.0, pygame.mixer.music.get_volume())

    while True:
        mouse_pos = pygame.mouse.get_pos()
        current_state = None
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        
            if event.type == pygame.MOUSEMOTION:
                back_button.check_hover(mouse_pos)
                fullscreen_button.check_hover(mouse_pos)

            result = back_button.handle_event(event)
            if result:
                current_state = result

            result = fullscreen_button.handle_event(event)
            if result == "toggle_fullscreen":
                fullscreen = not fullscreen
                if fullscreen:
                    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
                else:
                    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
            
            slider.handle_event(event)

        if current_state:
            return current_state

        screen.fill(WHITE)
        title = font.render("Nastavení", True, BLACK)
        screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 50))

        slider.draw(screen)
        fullscreen_button.draw(screen)
        back_button.draw(screen)

        pygame.display.flip()
        clock.tick(FPS)

def main_menu():
    global game_over, player_name, selected_customer, customer_positions
    game_over = False
    player_name = ""
    selected_customer = None
    customer_positions = []  # Reset pozic při nové hře
    
    buttons = [
        Button(300, 300, 200, 50, "Hrát", "game"),
        Button(300, 350, 200, 50, "Nastavení", "settings"),
        Button(300, 400, 200, 50, "Žebříček", "score"),
        Button(300, 450, 200, 50, "Konec", "quit")
    ]
    
    while True:
        mouse_pos = pygame.mouse.get_pos()
        current_state = None
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            for button in buttons:
                if event.type == pygame.MOUSEMOTION:
                    button.check_hover(mouse_pos)
                result = button.handle_event(event)
                if result:
                    current_state = result

        if current_state:
            return current_state
        screen.blit(background, (0, 0))

        # Zobraz title.png místo textu
        if title_image:
            title_rect = title_image.get_rect(center=(SCREEN_WIDTH//2, 150))
            screen.blit(title_image, title_rect)
        else:
            # Fallback na text pokud obrázek chybí
            title = font.render("Ježkův bar", True, WHITE)
            screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 50))
        
        for button in buttons:
            button.draw(screen)
        
        pygame.display.flip()
        clock.tick(FPS)

def game_over_scene():
    back_button = Button(300, 520, 200, 50, "Menu", "main_menu")
    retry_button = Button(300, 460, 200, 50, "Hrát znovu", "game")
    save_score_button = Button(300, 400, 200, 50, "Uložit skóre", "save_name")
    
    while True:
        mouse_pos = pygame.mouse.get_pos()
        current_state = None
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.MOUSEMOTION:
                back_button.check_hover(mouse_pos)
                retry_button.check_hover(mouse_pos)
                save_score_button.check_hover(mouse_pos)
            
            result = back_button.handle_event(event)
            if result:
                return result
                
            result = retry_button.handle_event(event)
            if result:
                return result
            
            result = save_score_button.handle_event(event)
            if result == "save_name":
                return "save_name"

        screen.fill(WHITE)
        title = font.render("GAME OVER", True, RED)
        screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 100))
        
        score_text = small_font.render(f"Skóre: {coins}", True, BLACK)
        screen.blit(score_text, (SCREEN_WIDTH//2 - score_text.get_width()//2, 180))
        
        reason_text = small_font.render("Příliš mnoho stresu!", True, BLACK)
        screen.blit(reason_text, (SCREEN_WIDTH//2 - reason_text.get_width()//2, 220))
        
        # Zobraz nově získané achievementy
        if player_name:
            achievements = get_player_achievements(player_name)
            if achievements:
                recent_achievements = [a for a in achievements if a[4]]  # Filtruj podle data
                if recent_achievements:
                    achievement_text = small_font.render("Nové achievementy:", True, GREEN)
                    screen.blit(achievement_text, (SCREEN_WIDTH//2 - achievement_text.get_width()//2, 260))
                    
                    for i, (name, desc, req_score, color, date) in enumerate(recent_achievements[:3]):
                        ach_text = tiny_font.render(f"- {name} ({req_score} bodů)", True, 
                                                  GOLD if color == "GOLD" else 
                                                  SILVER if color == "SILVER" else 
                                                  BRONZE if color == "BRONZE" else GRAY)
                        screen.blit(ach_text, (SCREEN_WIDTH//2 - ach_text.get_width()//2, 300 + i*25))
        
        save_score_button.draw(screen)
        retry_button.draw(screen)
        back_button.draw(screen)
        
        pygame.display.flip()
        clock.tick(FPS)

def game_scene():
    global customers, spawn_timer, beer_amount, wine_amount, drink_amount, coins, stress_level, game_over, selected_customer, customer_positions

    customers = []
    customer_positions = []  # Reset pozic zákazníků
    spawn_timer = pygame.time.get_ticks()
    game_start_time = pygame.time.get_ticks()  # Čas začátku hry
    beer_amount = beer_max
    wine_amount = wine_max
    drink_amount = drink_max
    coins = 0
    stress_level = 0
    game_over = False
    selected_customer = None

    # Tlačítka pro nápoje
    beer_button = Button(20, 500, 150, 40, "Pivo", "serve_beer", BEER_COLOR)
    wine_button = Button(190, 500, 150, 40, "Víno", "serve_wine", WINE_COLOR)
    drink_button = Button(360, 500, 150, 40, "Drink", "serve_drink", DRINK_COLOR)
    
    # Tlačítka pro doplnění 
    refill_beer_button = HoldButton(20, 550, 150, 40, "Doplnit pivo", "refill_beer", BEER_COLOR, hold_time=1.0)
    refill_wine_button = HoldButton(190, 550, 150, 40, "Doplnit víno", "refill_wine", WINE_COLOR, hold_time=1.0)
    refill_drink_button = HoldButton(360, 550, 150, 40, "Doplnit drink", "refill_drink", DRINK_COLOR, hold_time=1.0)

    while True:
        if game_over:
            return "game_over"

        mouse_pos = pygame.mouse.get_pos()
        current_state = None

        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return "main_menu"
                elif event.key == pygame.K_1:  # Klávesa 1 pro pivo
                    if selected_customer:
                        if selected_customer.drink_type == 0:
                            selected_customer.serve()
                        else:
                            # Špatný nápoj - zvýší stres
                            stress_level = min(stress_max, stress_level + 20)
                elif event.key == pygame.K_2:  # Klávesa 2 pro víno
                    if selected_customer:
                        if selected_customer.drink_type == 1:
                            selected_customer.serve()
                        else:
                            # Špatný nápoj - zvýší stres
                            stress_level = min(stress_max, stress_level + 20)
                elif event.key == pygame.K_3:  # Klávesa 3 pro drink
                    if selected_customer:
                        if selected_customer.drink_type == 2:
                            selected_customer.serve()
                        else:
                            # Špatný nápoj - zvýší stres
                            stress_level = min(stress_max, stress_level + 20)

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # Zkontroluj kliknutí na zákazníky
                for c in customers[:]:
                    if c.handle_click(event.pos):
                        break
                
                # Zkontroluj kliknutí na servírovací tlačítka
                result = beer_button.handle_event(event)
                if result == "serve_beer" and selected_customer:
                    if selected_customer.drink_type == 0:
                        selected_customer.serve()
                    else:
                        # Špatný nápoj - zvýší stres
                        stress_level = min(stress_max, stress_level + 20)
                
                result = wine_button.handle_event(event)
                if result == "serve_wine" and selected_customer:
                    if selected_customer.drink_type == 1:
                        selected_customer.serve()
                    else:
                        stress_level = min(stress_max, stress_level + 20)
                
                result = drink_button.handle_event(event)
                if result == "serve_drink" and selected_customer:
                    if selected_customer.drink_type == 2:
                        selected_customer.serve()
                    else:
                        stress_level = min(stress_max, stress_level + 20)
            
            # Zpracuj hold tlačítka pro doplnění
            if event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.MOUSEBUTTONUP or event.type == pygame.MOUSEMOTION:
                refill_beer_button.handle_event(event)
                refill_wine_button.handle_event(event)
                refill_drink_button.handle_event(event)

            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        # === LOGIKA HRY ===
        current_time = pygame.time.get_ticks()
        
        # Zvýšená frekvence po 30 sekundách a 90 sekundách
        if (current_time - game_start_time) >= 90000:
            spawn_interval = 800  # Nejrychlejší spawn po 90s
        elif (current_time - game_start_time) >= 30000:
            spawn_interval = 1200  # Střední spawn po 30s
        else:
            spawn_interval = 2000  # Normální spawn na začátku

        # Spawn nového zákazníka
        if current_time - spawn_timer >= spawn_interval and (beer_amount > 0 or wine_amount > 0 or drink_amount > 0) and len(customers) < 5:  
            # Zkusíme najít volnou pozici (max 10 pokusů)
            for attempt in range(10):
                new_x = random.randint(100, 700)
                new_y = 250
                
                # Kontrola překryvu s existujícími zákazníky
                overlap = False
                for pos in customer_positions:
                    if abs(new_x - pos[0]) < 100:  # og -> 200px rozestup mezi zákazníky
                        overlap = True
                        break
                
                if not overlap:
                    customers.append(Customer(new_x, new_y))
                    customer_positions.append((new_x, new_y))
                    spawn_timer = current_time
                    break
        
        # Odstraň obsloužené zákazníky
        for c in customers[:]:
            if c.served:
                # Najdi a odstraň pozici tohoto zákazníka
                for i, pos in enumerate(customer_positions):
                    if pos[0] == c.rect.centerx and pos[1] == c.rect.centery:
                        customer_positions.pop(i)
                        break
                customers.remove(c)

        # Kontrola hold tlačítek pro doplnění
        if refill_beer_button.check_hold_complete():
            beer_amount = beer_max
            coins -= 50
        
        if refill_wine_button.check_hold_complete():
            wine_amount = wine_max
            coins -= 50
        
        if refill_drink_button.check_hold_complete():
            drink_amount = drink_max
            coins -= 50
        
        # Zvyšování stresu
        if len(customers) > 0:
            customer_count = len(customers)
            stress_increase = customer_count * 1  # Méně stresu na zákazníka
            
            current_time = pygame.time.get_ticks()
            for customer in customers:
                time_waiting = (current_time - customer.arrival_time) / 1000
                if time_waiting > 1:
                    stress_increase += 2
                elif time_waiting > 5:
                    stress_increase += 5
            
            stress_level = min(stress_max, stress_level + stress_increase * 0.1)
        
        if stress_level >= stress_max:
            game_over = True

        # Aktualizuj stav tlačítek
        beer_button.enabled = beer_amount > 0
        wine_button.enabled = wine_amount > 0
        drink_button.enabled = drink_amount > 0

        # === VYKRESLENÍ ===
        screen.fill(WHITE)

        # Panely s nápoji
        # Pivo
        pygame.draw.rect(screen, BLACK, (20, 20, 200, 30), 2)
        fill_width = max(0, int((beer_amount / beer_max) * 198))
        pygame.draw.rect(screen, BEER_COLOR, (21, 21, fill_width, 28))
        beer_text = small_font.render(f"Pivo: {beer_amount}/{beer_max}", True, BLACK)
        screen.blit(beer_text, (230, 20))

        # Víno
        pygame.draw.rect(screen, BLACK, (20, 60, 200, 30), 2)
        fill_width = max(0, int((wine_amount / wine_max) * 198))
        pygame.draw.rect(screen, WINE_COLOR, (21, 61, fill_width, 28))
        wine_text = small_font.render(f"Víno: {wine_amount}/{wine_max}", True, BLACK)
        screen.blit(wine_text, (230, 60))

        # Drink
        pygame.draw.rect(screen, BLACK, (20, 100, 200, 30), 2)
        fill_width = max(0, int((drink_amount / drink_max) * 198))
        pygame.draw.rect(screen, DRINK_COLOR, (21, 101, fill_width, 28))
        drink_text = small_font.render(f"Drink: {drink_amount}/{drink_max}", True, BLACK)
        screen.blit(drink_text, (230, 100))

        # Stress bar
        pygame.draw.rect(screen, BLACK, (500, 20, 200, 30), 2)
        stress_fill_width = max(0, int((stress_level / stress_max) * 198))
        
        stress_color = STRESS_COLOR
        if stress_level > 70:
            stress_color = RED
        elif stress_level > 40:
            stress_color = YELLOW
            
        pygame.draw.rect(screen, stress_color, (501, 21, stress_fill_width, 28))

        stress_text = small_font.render(f"Stres: {int(stress_level)}%", True, BLACK)
        screen.blit(stress_text, (670, 60)) #710

        # Tlačítka pro servírování
        beer_button.draw(screen)
        wine_button.draw(screen)
        drink_button.draw(screen)
        
        # Tlačítka pro doplnění
        refill_beer_button.draw(screen)
        refill_wine_button.draw(screen)
        refill_drink_button.draw(screen)

        # Zákazníci
        for c in customers:
            c.draw(screen)      
            # Zobraz čas čekání
            wait_time = (pygame.time.get_ticks() - c.arrival_time) / 1000
            wait_text = tiny_font.render(f"{wait_time:.1f}s", True, RED if wait_time > 5 else BLACK)
            screen.blit(wait_text, (c.rect.centerx - 15, c.rect.bottom + 5))

        # Informace o vybraném zákazníku
        if selected_customer:
            drink_names = ["Pivo", "Víno", "Drink"]
            selected_text = small_font.render(f"Vybraný: Chce {drink_names[selected_customer.drink_type]}", True, BLUE)
            screen.blit(selected_text, (SCREEN_WIDTH//2 - selected_text.get_width()//2, 450))

        customer_text = small_font.render(f"Zákazníci: {len(customers)}", True, BLACK)
        screen.blit(customer_text, (500, 60))

        coins_text = small_font.render(f"Coins: {coins}", True, BLACK)
        screen.blit(coins_text, (500, 100))

        if stress_level > 70:
            warning_text = small_font.render("!!! VYSOKÝ STRES !!!", True, RED)
            screen.blit(warning_text, (SCREEN_WIDTH//2 - warning_text.get_width()//2, 150))


        pygame.display.flip()
        clock.tick(FPS)

def score_scene():
    back_button = Button(300, 550, 200, 50, "Menu", "main_menu")
    refresh_button = Button(300, 500, 200, 50, "Obnovit", "score")
    
    # Načtení skóre z databáze
    top_scores = get_top_scores()
    
    while True:
        mouse_pos = pygame.mouse.get_pos()
        current_state = None
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.MOUSEMOTION:
                back_button.check_hover(mouse_pos)
                refresh_button.check_hover(mouse_pos)
            
            result = back_button.handle_event(event)
            if result:
                return result
            
            result = refresh_button.handle_event(event)
            if result == "score":
                top_scores = get_top_scores()
                return "score"

        screen.fill(WHITE)
        title = font.render("Nejlepší skóre", True, BLACK)
        screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 50))
        
        if not top_scores:
            no_scores = small_font.render("Žádná skóre v databázi", True, RED)
            screen.blit(no_scores, (SCREEN_WIDTH//2 - no_scores.get_width()//2, 150))
        else:
            # Hlavička tabulky
            header_y = 120
            pygame.draw.line(screen, BLACK, (100, header_y), (700, header_y), 2)
            
            headers = ["Pořadí", "Jméno", "Skóre", "Datum"]
            for i, header in enumerate(headers):
                header_text = small_font.render(header, True, BLUE)
                x_pos = 150 + i * 150
                screen.blit(header_text, (x_pos, header_y + 10))
            
            pygame.draw.line(screen, BLACK, (100, header_y + 40), (700, header_y + 40), 2)
            
            # Data
            for idx, (name, score, date) in enumerate(top_scores[:10]):
                y_pos = header_y + 50 + idx * 30
                
                # Pořadí
                rank_text = small_font.render(f"{idx+1}.", True, BLACK)
                screen.blit(rank_text, (150, y_pos))
                
                # Jméno
                name_text = tiny_font.render(str(name)[:15], True, BLACK)
                screen.blit(name_text, (265, y_pos + 5))
                
                # Skóre
                score_text = small_font.render(str(score), True, GREEN if idx == 0 else BLACK)
                screen.blit(score_text, (445, y_pos))
                
                # Datum
                if isinstance(date, datetime):
                    date_str = date.strftime("%d.%m.%Y")
                else:
                    date_str = str(date)
                date_text = tiny_font.render(date_str, True, BLACK)
                screen.blit(date_text, (600, y_pos + 5))
        
        # Aktuální skóre (pokud existuje)
        if coins > 0:
            current_score = small_font.render(f"Vaše poslední skóre: {coins}", True, BLACK)
            screen.blit(current_score, (SCREEN_WIDTH//2 - current_score.get_width()//2, 450))
        
        refresh_button.draw(screen)
        back_button.draw(screen)
        
        pygame.display.flip()
        clock.tick(FPS)


def main():
    # Vytvoření tabulek při spuštění
    create_table()
    
    current_state = "main_menu"
    
    while True:
        if current_state == "main_menu":
            current_state = main_menu()
        elif current_state == "settings":
            current_state = settings_scene()
        elif current_state == "game":
            current_state = game_scene()
        elif current_state == "score":
            current_state = score_scene()
        elif current_state == "game_over":
            current_state = game_over_scene()
        elif current_state == "save_name":
            current_state = save_name_scene()
        elif current_state == "quit":
            pygame.quit()
            sys.exit()

if __name__ == "__main__":
    main()