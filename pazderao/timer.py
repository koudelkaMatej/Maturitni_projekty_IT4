import pygame
import os

class GameTimer:
    def __init__(self):
        self.start_ticks = 0
        self.accumulated_time = 0
        self.is_paused = False
        self.is_running = False
        self.saved = False # Zabraňuje vícenásobnému uložení stejného času

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

    def get_time_string(self):
        current_total = self.accumulated_time
        if self.is_running and not self.is_paused:
            current_total += pygame.time.get_ticks() - self.start_ticks

        if current_total == 0:
            return "00:00.0"

        tenths = (current_total // 100) % 10
        seconds = (current_total // 1000) % 60
        minutes = (current_total // 60000)

        return f"{minutes:02d}:{seconds:02d}.{tenths}"

    def draw(self, screen, font, color, x, y):
        time_str = self.get_time_string()
        img = font.render(time_str, True, color)
        screen.blit(img, (x, y))

    # --- NOVÁ CHYTRÁ FUNKCE PRO UKLÁDÁNÍ ---
    def save_time(self, filename, level):
        if not self.saved and self.accumulated_time > 0:
            # Převedeme číslo levelu (1, 2, 3) na text
            level_names = {1: "LEHKÁ", 2: "STŘEDNÍ", 3: "TĚŽKÁ"}
            current_level = level_names.get(level, "NEZNÁMÁ")
            new_time = self.get_time_string()

            # Datová struktura pro rozřazení
            data = {"LEHKÁ": [], "STŘEDNÍ": [], "TĚŽKÁ": []}
            current_section = None

            # 1. Pokusíme se načíst existující časy ze souboru
            try:
                with open(filename, "r", encoding="utf-8") as file:
                    for line in file:
                        line = line.strip()
                        if not line: continue
                        if line in ["LEHKÁ:", "STŘEDNÍ:", "TĚŽKÁ:"]:
                            current_section = line.replace(":", "")
                        elif current_section and line.startswith("Vítězný čas:"):
                            data[current_section].append(line)
            except FileNotFoundError:
                pass # Pokud soubor neexistuje, nic se neděje, vytvoříme nový

            # 2. Přidáme nový čas hráče do správné sekce
            if current_level in data:
                data[current_level].append(f"Vítězný čas: {new_time}")

            # 3. Zapíšeme zformátované a SEŘAZENÉ časy zpět
            with open(filename, "w", encoding="utf-8") as file:
                for sec in ["LEHKÁ", "STŘEDNÍ", "TĚŽKÁ"]:
                    file.write(f"{sec}:\n")
                    # Seřazení funguje abecedně, což u formátu 00:00.0 řadí od nejrychlejšího!
                    for t in sorted(data[sec]):
                        file.write(f"{t}\n")
                    file.write("\n") # Odřádkování pro přehlednost mezi sekcemi

            self.saved = True