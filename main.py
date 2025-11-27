import pygame
import sys
import random

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
beer_max = 60
stress_level = 0
stress_max = 100
game_over = False

# Barvy
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
LIGHT_GRAY = (230, 230, 230)
GREEN = (0, 200, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
BEER_COLOR = (200, 180, 50)
STRESS_COLOR = (150, 50, 150)

# Nastavení obrazovky
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Ježkův bar :)")
clock = pygame.time.Clock()

# Načtení pozadí
try:
    background = pygame.image.load("wall.png")
    background = pygame.transform.scale(background, (SCREEN_WIDTH, SCREEN_HEIGHT))
except:
    background = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    background.fill((100, 100, 100))

# Načtení obrázku zákazníka
try:
    customer_img = pygame.image.load("customer.png")
    customer_img = pygame.transform.scale(customer_img, (200, 200)) 
except:
    customer_img = pygame.Surface((200, 200))
    customer_img.fill((150, 150, 150))

# Fonty
font = pygame.font.SysFont('Arial', 40)
small_font = pygame.font.SysFont('Arial', 30)

# Hlasitost
volume = 0.5
pygame.mixer.init()
pygame.mixer.music.set_volume(volume)

# Fullscreen stav
fullscreen = False

class Button:
    def __init__(self, x, y, width, height, text, action=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.action = action
        self.is_hovered = False

    def draw(self, surface):
        color = LIGHT_GRAY if self.is_hovered else GRAY
        pygame.draw.rect(surface, color, self.rect)
        pygame.draw.rect(surface, BLACK, self.rect, 2)
        
        text_surf = small_font.render(self.text, True, BLACK)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def check_hover(self, pos):
        self.is_hovered = self.rect.collidepoint(pos)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                if self.action:
                    return self.action
        return None

class Slider:
    def __init__(self, x, y, width, min_val=0.0, max_val=1.0, start_val=0.5):
        self.rect = pygame.Rect(x, y, width, 10)
        self.min_val = min_val
        self.max_val = max_val
        self.value = start_val
        self.handle_x = x + width * ((start_val - min_val) / (max_val - min_val))
        self.dragging = False

    def draw(self, surface):
        # Čára slideru
        pygame.draw.rect(surface, GRAY, self.rect)
        # Kolečka posuvníku
        handle_rect = pygame.Rect(self.handle_x - 8, self.rect.centery - 8, 16, 16)
        pygame.draw.circle(surface, GREEN if self.dragging else BLACK, handle_rect.center, 8)
        # Text hlasitosti
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
        self.image = customer_img
        self.rect = self.image.get_rect(center=(x, y))
        self.served = False
        self.arrival_time = pygame.time.get_ticks()

    def draw(self, surface):
        if not self.served:
            surface.blit(self.image, self.rect)

    def handle_click(self, pos):
        global coins, beer_amount, stress_level
        if not self.served and self.rect.collidepoint(pos) and beer_amount > 0:
            self.served = True
            coins += 15
            beer_amount -= 1
            # Snížení stresu při obsloužení zákazníka
            stress_level = max(0, stress_level - 10)

def settings_scene():
    global fullscreen, screen

    back_button = Button(300, 500, 200, 50, "Zpět do menu", "main_menu")
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
    global game_over
    game_over = False  # Reset game over stavu
    
    buttons = [
        Button(300, 150, 200, 50, "hrát", "game"),
        Button(300, 250, 200, 50, "nastavení", "settings"),
        Button(300, 350, 200, 50, "skóre", "score"),
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

        # === vykreslení pozadí ===
        screen.blit(background, (0, 0))

        # Nápis a tlačítka
        title = font.render("ježkův bar", True, WHITE)
        screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 50))
        
        for button in buttons:
            button.draw(screen)
        
        pygame.display.flip()
        clock.tick(FPS)

def game_over_scene():
    back_button = Button(300, 400, 200, 50, "Hlavní menu", "main_menu")
    retry_button = Button(300, 300, 200, 50, "Hrát znovu", "game")
    
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
            
            result = back_button.handle_event(event)
            if result:
                return result
                
            result = retry_button.handle_event(event)
            if result:
                return result

        screen.fill(WHITE)
        title = font.render("GAME OVER", True, RED)
        screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 100))
        
        score_text = small_font.render(f"Konečné skóre: {coins}", True, BLACK)
        screen.blit(score_text, (SCREEN_WIDTH//2 - score_text.get_width()//2, 180))
        
        reason_text = small_font.render("Příliš mnoho stresu!", True, BLACK)
        screen.blit(reason_text, (SCREEN_WIDTH//2 - reason_text.get_width()//2, 220))
        
        retry_button.draw(screen)
        back_button.draw(screen)
        
        pygame.display.flip()
        clock.tick(FPS)

def game_scene():
    global customers, spawn_timer, beer_amount, coins, stress_level, game_over

    # Inicializace hry - reset stavu při každém vstupu do hry
    customers = []
    spawn_timer = pygame.time.get_ticks()
    beer_amount = beer_max
    coins = 0
    stress_level = 0
    game_over = False

    back_button = Button(300, 500, 200, 50, "Zpět do menu", "main_menu")
    new_keg_button = Button(20, 550, 150, 40, "Nový sud", "new_keg")

    while True:
        if game_over:
            return "game_over"

        mouse_pos = pygame.mouse.get_pos()
        current_state = None

        for event in pygame.event.get():
            # ESC pro návrat
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return "main_menu"

            # Klikání na zákazníky
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for c in customers[:]:  # Použijeme kopii seznamu, abychom mohli měnit původní
                    c.handle_click(event.pos)
                    # Odstranění obsloužených zákazníků
                    if c.served:
                        customers.remove(c)

            # Nový sud
            result = new_keg_button.handle_event(event)
            if result == "new_keg":
                beer_amount = beer_max

            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # Zpět tlačítko
            if event.type == pygame.MOUSEMOTION:
                back_button.check_hover(mouse_pos)

            result = back_button.handle_event(event)
            if result:
                return result

        # === LOGIKA HRY ===
        # Auto-spawn zákazníků každou 1 sekundu
        current_time = pygame.time.get_ticks()
        if current_time - spawn_timer >= 1000 and beer_amount > 0:  
            new_x = random.randint(100, 700)
            customers.append(Customer(new_x, 250))
            spawn_timer = current_time

        # Výpočet stresu - více zákazníků = více stresu
        customer_count = len(customers)
        stress_increase = customer_count * 2  # Každý zákazník přidá 2% stresu za frame
        
        # Starší zákazníci přidávají více stresu
        current_time = pygame.time.get_ticks()
        for customer in customers:
            time_waiting = (current_time - customer.arrival_time) / 1000  # v sekundách
            if time_waiting > 5:  # Po 5 sekundách čekání přidávají více stresu
                stress_increase += 1
        
        stress_level = min(stress_max, stress_level + stress_increase * 0.1)
        
        # Kontrola konce hry
        if stress_level >= stress_max:
            game_over = True

        # Omezení počtu zákazníků (pro výkon)
        if len(customers) > 10:
            customers = customers[-10:]

        # === VYKRESLENÍ ===
        screen.fill(WHITE)

        # Beer bar
        pygame.draw.rect(screen, BLACK, (20, 20, 200, 30), 2)
        fill_width = max(0, int((beer_amount / beer_max) * 198))
        pygame.draw.rect(screen, BEER_COLOR, (21, 21, fill_width, 28))

        beer_text = small_font.render(f"Pivo: {beer_amount}/{beer_max}", True, BLACK)
        screen.blit(beer_text, (230, 20))

        # Stress bar
        pygame.draw.rect(screen, BLACK, (20, 60, 200, 30), 2)
        stress_fill_width = max(0, int((stress_level / stress_max) * 198))
        
        # Barva stresu se mění podle úrovně
        stress_color = STRESS_COLOR
        if stress_level > 70:
            stress_color = RED
        elif stress_level > 40:
            stress_color = YELLOW
            
        pygame.draw.rect(screen, stress_color, (21, 61, stress_fill_width, 28))

        stress_text = small_font.render(f"Stres: {int(stress_level)}%", True, BLACK)
        screen.blit(stress_text, (230, 60))

        # Tlačítko nový sud
        new_keg_button.draw(screen)

        # Vykreslení zákazníků
        for c in customers:
            c.draw(screen)

        # Informace o zákaznících
        customer_text = small_font.render(f"Zákazníci: {len(customers)}", True, BLACK)
        screen.blit(customer_text, (400, 60))

        # Coins
        coins_text = small_font.render(f"Coins: {coins}", True, BLACK)
        screen.blit(coins_text, (400, 20))

        # Varování při vysokém stresu
        if stress_level > 70:
            warning_text = small_font.render("!!! VYSOKÝ STRES !!!", True, RED)
            screen.blit(warning_text, (SCREEN_WIDTH//2 - warning_text.get_width()//2, 100))

        # Zpět tlačítko
        back_button.draw(screen)

        pygame.display.flip()
        clock.tick(FPS)

def score_scene():
    back_button = Button(300, 500, 200, 50, "Zpět do menu", "main_menu")
    
    while True:
        mouse_pos = pygame.mouse.get_pos()
        current_state = None
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.MOUSEMOTION:
                back_button.check_hover(mouse_pos)
            
            result = back_button.handle_event(event)
            if result:
                return result

        screen.fill(WHITE)
        title = font.render("Skóre", True, BLACK)
        screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 50))
        
        score_text = small_font.render(f"Nejvyšší skóre: {coins}", True, BLACK)
        screen.blit(score_text, (SCREEN_WIDTH//2 - score_text.get_width()//2, 150))
        
        back_button.draw(screen)
        pygame.display.flip()
        clock.tick(FPS)

def main():
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
        elif current_state == "quit":
            pygame.quit()
            sys.exit()

if __name__ == "__main__":
    main()