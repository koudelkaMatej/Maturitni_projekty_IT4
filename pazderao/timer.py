import pygame
import os

class GameTimer:
    def __init__(self):
        self.start_ticks = 0 #počáteční tiky pro měření
        self.accumulated_time = 0 #nasbíraný čas v milisekundách
        self.is_paused = False #stav pauzy
        self.is_running = False #příznak, jestli timer běží
        self.saved = False #pojistka proti vícenásobnému uložení

    def start(self):
        self.start_ticks = pygame.time.get_ticks() #uložení startovního času
        self.accumulated_time = 0 #resetování času
        self.is_running = True #spuštění timeru
        self.is_paused = False #vypnutí pauzy
        self.saved = False #resetování stavu uložení

    def pause(self):
        if self.is_running and not self.is_paused:
            self.accumulated_time += pygame.time.get_ticks() - self.start_ticks #přičtení času před pauzou
            self.is_paused = True #aktivace pauzy

    def resume(self):
        if self.is_running and self.is_paused:
            self.start_ticks = pygame.time.get_ticks() #nový startovní bod po pauze
            self.is_paused = False #vypnutí pauzy

    def stop(self):
        if self.is_running:
            if not self.is_paused:
                self.accumulated_time += pygame.time.get_ticks() - self.start_ticks #konečný dopočet času
            self.is_running = False #zastavení timeru
            self.is_paused = False #vypnutí pauzy

    def get_time_string(self):
        current_total = self.accumulated_time #základ z nasbíraného času
        if self.is_running and not self.is_paused:
            current_total += pygame.time.get_ticks() - self.start_ticks #přičtení aktuálního běhu

        if current_total == 0:
            return "00:00:000"

        milliseconds = current_total % 1000 #výpočet milisekund
        seconds = (current_total // 1000) % 60 #výpočet sekund
        minutes = (current_total // 60000) #výpočet minut

        return f"{minutes:02d}:{seconds:02d}:{milliseconds:03d}" #formátování na text

    def draw(self, screen, font, color, x, y):
        time_str = self.get_time_string() #získání textu času
        img = font.render(time_str, True, color) #vytvoření obrázku textu
        screen.blit(img, (x, y)) #vykreslení na zadané souřadnice

    def save_time(self, filename, level, player_name):
        if not self.saved and self.accumulated_time > 0: #uložení jen při splnění podmínek
            level_names = {1: "LEHKÁ", 2: "STŘEDNÍ", 3: "TĚŽKÁ"} #převod čísel na text
            current_level = level_names.get(level, "NEZNÁMÁ") #získání názvu úrovně
            new_time = self.get_time_string() #získání finálního času

            data = {"LEHKÁ": [], "STŘEDNÍ": [], "TĚŽKÁ": []} #příprava struktury pro data
            current_section = None #pomocná proměnná pro čtení sekcí

            if os.path.exists(filename):
                try:
                    with open(filename, "r", encoding="utf-8") as file:
                        for line in file:
                            line = line.strip()
                            if not line: continue
                            
                            if line in ["LEHKÁ:", "STŘEDNÍ:", "TĚŽKÁ:"]: #detekce sekce v souboru
                                current_section = line.replace(":", "")
                                continue
                            
                            if current_section and ", " in line: #přidání řádku do správné sekce
                                data[current_section].append(line)
                except Exception as e:
                    print(f"chyba při čtení: {e}")

            if current_level in data: #přidání nového výsledku
                formatted_name = player_name.capitalize() #formátování jména
                data[current_level].append(f"{formatted_name}, {new_time}")

            try:
                with open(filename, "w", encoding="utf-8") as file:
                    for sec in ["LEHKÁ", "STŘEDNÍ", "TĚŽKÁ"]: #zápis všech sekcí
                        file.write(f"{sec}:\n")
                        
                        sorted_list = sorted(data[sec], key=lambda x: x.split(", ")[1]) #řazení podle času
                        
                        for radek in sorted_list: #zápis jednotlivých řádků
                            file.write(f"{radek}\n")
                        file.write("\n") #mezera pro přehlednost
                
                self.saved = True #označení jako uloženo
            except Exception as e:
                print(f"chyba při zápisu: {e}")