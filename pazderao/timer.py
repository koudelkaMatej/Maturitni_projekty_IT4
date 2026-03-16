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
            return "00:00:000"

        # Výpočty
        milliseconds = current_total % 1000        
        seconds = (current_total // 1000) % 60    
        minutes = (current_total // 60000)         

        
        return f"{minutes:02d}:{seconds:02d}:{milliseconds:03d}"

    def draw(self, screen, font, color, x, y):
        time_str = self.get_time_string()
        img = font.render(time_str, True, color)
        screen.blit(img, (x, y))


    def save_time(self, filename, level, player_name):
        # Uložíme jen pokud ještě nebylo uloženo a čas je větší než 0
        if not self.saved and self.accumulated_time > 0:
            level_names = {1: "LEHKÁ", 2: "STŘEDNÍ", 3: "TĚŽKÁ"}
            current_level = level_names.get(level, "NEZNÁMÁ")
            new_time = self.get_time_string()

            # 1. Příprava dat (vyčistíme staré "Vítězný čas" záznamy)
            data = {"LEHKÁ": [], "STŘEDNÍ": [], "TĚŽKÁ": []}
            current_section = None

            if os.path.exists(filename):
                try:
                    with open(filename, "r", encoding="utf-8") as file:
                        for line in file:
                            line = line.strip()
                            if not line: continue
                            
                            # Detekce sekce (LEHKÁ:, ...)
                            if line in ["LEHKÁ:", "STŘEDNÍ:", "TĚŽKÁ:"]:
                                current_section = line.replace(":", "")
                                continue
                            
                            # Načteme jen řádky, které obsahují čárku (Jméno, Čas)
                            if current_section and ", " in line:
                                data[current_section].append(line)
                except Exception as e:
                    print(f"Chyba při čtení: {e}")

            # 2. Přidání nového záznamu (Jméno, Čas)
            if current_level in data:
                formatted_name = player_name.capitalize()
                data[current_level].append(f"{formatted_name}, {new_time}")

            # 3. Zápis a správné seřazení
            try:
                with open(filename, "w", encoding="utf-8") as file:
                    for sec in ["LEHKÁ", "STŘEDNÍ", "TĚŽKÁ"]:
                        file.write(f"{sec}:\n")
                        
                        # KLÍČOVÉ ŘAZENÍ: x.split(", ")[1] vezme ten čas za čárkou a řadí podle něj
                        sorted_list = sorted(data[sec], key=lambda x: x.split(", ")[1])
                        
                        for radek in sorted_list:
                            file.write(f"{radek}\n")
                        file.write("\n")
                
                self.saved = True # Označíme jako uloženo
                print(f"Uloženo: {player_name} v čase {new_time}")
            except Exception as e:
                print(f"Chyba při zápisu: {e}")

            # 2. Přidáme nový čas hráče do správné sekce
            if current_level in data:
                data[current_level].append(f"{player_name} - {new_time}")

            # 3. Zapíšeme zformátované a SEŘAZENÉ časy zpět
            with open(filename, "w", encoding="utf-8") as file:
                for sec in ["LEHKÁ", "STŘEDNÍ", "TĚŽKÁ"]:
                    file.write(f"{sec}:\n")
                    # Seřazení funguje abecedně, což u formátu 00:00.0 řadí od nejrychlejšího!
                    for t in sorted(data[sec]):
                        file.write(f"{t}\n")
                    file.write("\n") # Odřádkování pro přehlednost mezi sekcemi

            self.saved = True