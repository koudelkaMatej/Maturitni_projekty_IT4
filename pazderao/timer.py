import pygame
import mysql.connector
from settings import host, username, password, database

class GameTimer:
    def __init__(self): # základní nastavení timeru při vytvoření
        self.start_ticks = 0
        self.accumulated_time = 0
        self.is_paused = False
        self.is_running = False
        self.saved = False

    def start(self):
        self.start_ticks = pygame.time.get_ticks() # uložení času ze systému při startu
        self.accumulated_time = 0
        self.is_running = True
        self.is_paused = False
        self.saved = False

    def pause(self):
        if self.is_running and not self.is_paused:
            self.accumulated_time += pygame.time.get_ticks() - self.start_ticks # přičtení času do paměti před pauzou
            self.is_paused = True

    def resume(self):
        if self.is_running and self.is_paused:
            self.start_ticks = pygame.time.get_ticks() # znovunastavení času po pauze
            self.is_paused = False

    def stop(self):
        if self.is_running:
            if not self.is_paused:
                self.accumulated_time += pygame.time.get_ticks() - self.start_ticks # konečný výpočet času
            self.is_running = False
            self.is_paused = False

    def reset(self):
        self.start_ticks = 0 # vynulování všech hodnot v timeru
        self.accumulated_time = 0
        self.is_paused = False
        self.is_running = False
        self.saved = False

    def get_time_ms(self):
        if not self.is_running and self.accumulated_time == 0: return 0 # vrátí nulu, když timer neběžel
        total = self.accumulated_time
        if self.is_running and not self.is_paused:
            total += pygame.time.get_ticks() - self.start_ticks # aktuální čas za běhu
        return total

    def get_time_string(self):
        current_total = self.get_time_ms()
        if current_total == 0: return "00:00:000"
        milliseconds = current_total % 1000 # zbytek do milisekund
        seconds = (current_total // 1000) % 60 # výpočet sekund
        minutes = (current_total // 60000) # výpočet minut
        return f"{minutes:02d}:{seconds:02d}:{milliseconds:03d}" # formátování textu času

    def draw(self, screen, font, color, x, y):
        time_str = self.get_time_string()
        img = font.render(time_str, True, color) # příprava obrázku s textem času
        screen.blit(img, (x, y)) # vykreslení času na plochu hry

    def save_time(self, level, p_name):
        if self.saved or self.accumulated_time <= 0: return # aby se stejný čas neukládal pořád dokola

        try:
            conn = mysql.connector.connect(host=host, user=username, password=password, database=database)
            cursor = conn.cursor()

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS pazderao_casy (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(50),
                    level INT,
                    time_str VARCHAR(20),
                    time_ms INT
                )
            """) # vytvoření tabulky pro výsledky, pokud tam ještě není

            sql = "INSERT INTO pazderao_casy (username, level, time_str, time_ms) VALUES (%s, %s, %s, %s)"
            val = (p_name.capitalize(), level, self.get_time_string(), self.get_time_ms()) # příprava dat pro zápis
            cursor.execute(sql, val)
            
            conn.commit() # potvrzení uložení do databáze (bez toho tam nic nebude)
            self.saved = True
        except Exception as e:
            print(f"chyba ukladani db: {e}")
        finally:
            if 'conn' in locals() and conn.is_connected():
                cursor.close()
                conn.close()