import pygame
import os

class GameTimer:
    def __init__(self):
        self.start_ticks = 0 # čas spuštění v milisekundách
        self.accumulated_time = 0 # celkový čas před pauzou
        self.is_paused = False # indikátor pozastavení
        self.is_running = False # indikátor chodu stopek
        self.saved = False # pojistka proti duplicitnímu uložení

    def start(self):
        self.start_ticks = pygame.time.get_ticks() # začátek měření
        self.accumulated_time = 0 # vynulování času
        self.is_running = True # spuštění
        self.is_paused = False
        self.saved = False

    def pause(self):
        if self.is_running and not self.is_paused:
            # přičtení aktuálního úseku k celkovému času
            self.accumulated_time += pygame.time.get_ticks() - self.start_ticks
            self.is_paused = True # aktivace pauzy

    def resume(self):
        if self.is_running and self.is_paused:
            self.start_ticks = pygame.time.get_ticks() # nový startovní bod
            self.is_paused = False

    def stop(self):
        if self.is_running:
            if not self.is_paused:
                self.accumulated_time += pygame.time.get_ticks() - self.start_ticks
            self.is_running = False # konečné zastavení
            self.is_paused = False

    def get_time_string(self):
        current_total = self.accumulated_time
        if self.is_running and not self.is_paused:
            current_total += pygame.time.get_ticks() - self.start_ticks

        if current_total == 0:
            return "00:00:000"

        # převod milisekund na čitelný formát
        milliseconds = current_total % 1000
        seconds = (current_total // 1000) % 60
        minutes = (current_total // 60000)

        return f"{minutes:02d}:{seconds:02d}:{milliseconds:03d}"

    def draw(self, screen, font, color, x, y):
        # vykreslení času na obrazovku hry
        time_str = self.get_time_string()
        img = font.render(time_str, True, color)
        screen.blit(img, (x, y))

    def save_time(self, filename, level, player_name):
        # (settings.py) filename se bere z cesty pro data
        if not self.saved and self.accumulated_time > 0:
            level_names = {1: "LEHKÁ", 2: "STŘEDNÍ", 3: "TĚŽKÁ"}
            current_level = level_names.get(level, "NEZNÁMÁ")
            new_time = self.get_time_string()

            data = {"LEHKÁ": [], "STŘEDNÍ": [], "TĚŽKÁ": []}
            current_section = None

            # načtení stávajících výsledků ze souboru
            if os.path.exists(filename):
                try:
                    with open(filename, "r", encoding="utf-8") as file:
                        for line in file:
                            line = line.strip()
                            if not line: continue
                            
                            # kontrola sekce podle obtížnosti
                            if line in ["LEHKÁ:", "STŘEDNÍ:", "TĚŽKÁ:"]:
                                current_section = line.replace(":", "")
                                continue
                            
                            if current_section and ", " in line:
                                data[current_section].append(line)
                except Exception as e:
                    print(f"Chyba čtení DB: {e}")

            # přidání nového času hráče
            if current_level in data:
                formatted_name = player_name.capitalize()
                data[current_level].append(f"{formatted_name}, {new_time}")

            # zápis všech dat zpět do souboru
            try:
                with open(filename, "w", encoding="utf-8") as file:
                    for sec in ["LEHKÁ", "STŘEDNÍ", "TĚŽKÁ"]:
                        file.write(f"{sec}:\n")
                        
                        # seřazení od nejlepšího času (podle milisekund v textu)
                        sorted_list = sorted(data[sec], key=lambda x: x.split(", ")[1])
                        
                        for radek in sorted_list:
                            file.write(f"{radek}\n")
                        file.write("\n")
                
                self.saved = True # označení úspěšného uložení
            except Exception as e:
                print(f"Chyba zápisu DB: {e}")