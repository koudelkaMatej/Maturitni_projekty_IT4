import pygame
import mysql.connector
from settings import host, username, password, database

class GameTimer:
    def __init__(self):
        self.start_ticks = 0
        self.accumulated_time = 0
        self.is_paused = False
        self.is_running = False
        self.saved = False

    def start(self):
        self.start_ticks = pygame.time.get_ticks()
        self.accumulated_time = 0
        self.is_running = True
        self.is_paused = False
        self.saved = False

    def pause(self):
        if self.is_running and not self.is_paused:
            self.accumulated_time += pygame.time.get_ticks() - self.start_ticks
            self.is_paused = True

    def resume(self):
        if self.is_running and self.is_paused:
            self.start_ticks = pygame.time.get_ticks()
            self.is_paused = False

    def stop(self):
        if self.is_running:
            if not self.is_paused:
                self.accumulated_time += pygame.time.get_ticks() - self.start_ticks
            self.is_running = False
            self.is_paused = False

    def reset(self):
        self.start_ticks = 0
        self.accumulated_time = 0
        self.is_paused = False
        self.is_running = False
        self.saved = False

    def get_time_ms(self):
        # Pokud timer vůbec neběží a není tam uložený čas, vrať 0
        if not self.is_running and self.accumulated_time == 0:
            return 0
        
        total = self.accumulated_time
        if self.is_running and not self.is_paused:
            total += pygame.time.get_ticks() - self.start_ticks
        return total

    def get_time_ms(self):
        # čas v milisekundách kvůli řazení
        total = self.accumulated_time
        if self.is_running and not self.is_paused:
            total += pygame.time.get_ticks() - self.start_ticks
        return total

    def get_time_string(self):
        current_total = self.get_time_ms()
        if current_total == 0: return "00:00:000"
        milliseconds = current_total % 1000
        seconds = (current_total // 1000) % 60
        minutes = (current_total // 60000)
        return f"{minutes:02d}:{seconds:02d}:{milliseconds:03d}"

    def draw(self, screen, font, color, x, y):
        time_str = self.get_time_string()
        img = font.render(time_str, True, color)
        screen.blit(img, (x, y))

    def save_time(self, level, p_name):
        if self.saved or self.accumulated_time <= 0:
            return

        try:
            # připojení k databázi
            conn = mysql.connector.connect(host=host, user=username, password=password, database=database)
            cursor = conn.cursor()

            # moje vlastní tabulka, ať se to neplete s ostatníma
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS pazderao_casy (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(50),
                    level INT,
                    time_str VARCHAR(20),
                    time_ms INT
                )
            """)

            # vložení dat
            sql = "INSERT INTO pazderao_casy (username, level, time_str, time_ms) VALUES (%s, %s, %s, %s)"
            val = (p_name.capitalize(), level, self.get_time_string(), self.get_time_ms())
            cursor.execute(sql, val)
            
            conn.commit()
            self.saved = True
        except Exception as e:
            print(f"chyba ukladani db: {e}")
        finally:
            if 'conn' in locals() and conn.is_connected():
                cursor.close()
                conn.close()