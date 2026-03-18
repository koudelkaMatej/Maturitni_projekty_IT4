import pygame
import os

class GameTimer:
    def __init__(self):
        self.start_ticks = 0 # čas kdy se začalo
        self.accumulated_time = 0 # uloženej čas
        self.is_paused = False # jestli je pauza
        self.is_running = False # jestli běží čas
        self.saved = False # aby se to neuložilo víckrát

    def start(self):
        self.start_ticks = pygame.time.get_ticks() # start stopek
        self.accumulated_time = 0
        self.is_running = True
        self.is_paused = False
        self.saved = False

    def pause(self):
        if self.is_running and not self.is_paused:
            # uložení času do pauzy
            self.accumulated_time += pygame.time.get_ticks() - self.start_ticks
            self.is_paused = True

    def resume(self):
        if self.is_running and self.is_paused:
            self.start_ticks = pygame.time.get_ticks() # pokračování po pauze
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
            return "00:00:000"

        # převod na minuty a sekundy
        milliseconds = current_total % 1000
        seconds = (current_total // 1000) % 60
        minutes = (current_total // 60000)

        return f"{minutes:02d}:{seconds:02d}:{milliseconds:03d}"

    def draw(self, screen, font, color, x, y):
        # nakreslí čas do rohu
        time_str = self.get_time_string()
        img = font.render(time_str, True, color)
        screen.blit(img, (x, y))

    def save_time(self, filename, level, player_name):
        if not self.saved and self.accumulated_time > 0:
            level_names = {1: "LEHKÁ", 2: "STŘEDNÍ", 3: "TĚŽKÁ"}
            current_level = level_names.get(level, "NEZNÁMÁ")
            new_time = self.get_time_string()

            data = {"LEHKÁ": [], "STŘEDNÍ": [], "TĚŽKÁ": []}
            current_section = None

            # načtení starých časů
            if os.path.exists(filename):
                try:
                    with open(filename, "r", encoding="utf-8") as file:
                        for line in file:
                            line = line.strip()
                            if not line: continue
                            if line in ["LEHKÁ:", "STŘEDNÍ:", "TĚŽKÁ:"]:
                                current_section = line.replace(":", "")
                                continue
                            if current_section and ", " in line:
                                data[current_section].append(line)
                except Exception as e:
                    print(f"chyba čtení: {e}")

            # přidání novýho jména a času
            if current_level in data:
                data[current_level].append(f"{player_name.capitalize()}, {new_time}")

            # uložení všech časů a seřazení
            try:
                with open(filename, "w", encoding="utf-8") as file:
                    for sec in ["LEHKÁ", "STŘEDNÍ", "TĚŽKÁ"]:
                        file.write(f"{sec}:\n")
                        # srovná časy od nejlepšího
                        sorted_list = sorted(data[sec], key=lambda x: x.split(", ")[1])
                        for radek in sorted_list:
                            file.write(f"{radek}\n")
                        file.write("\n")
                self.saved = True
            except Exception as e:
                print(f"chyba zápisu: {e}")