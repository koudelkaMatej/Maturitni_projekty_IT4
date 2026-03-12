import pygame

class GameTimer:
    def __init__(self):
        self.start_ticks = 0
        self.elapsed_time = 0
        self.is_running = False
        self.saved = False # Zabraňuje vícenásobnému uložení stejného času

    def start(self):
        self.start_ticks = pygame.time.get_ticks()
        self.is_running = True
        self.saved = False

    def stop(self):
        if self.is_running:
            self.elapsed_time = pygame.time.get_ticks() - self.start_ticks
            self.is_running = False

    def get_time_string(self):
        # Pokud timer ještě nebyl spuštěn (is_running je False a elapsed_time je 0)
        if not self.is_running and self.elapsed_time == 0:
            return "00:00.0"
            
        if self.is_running:
            current_time = pygame.time.get_ticks() - self.start_ticks
        else:
            current_time = self.elapsed_time

        tenths = (current_time // 100) % 10
        seconds = (current_time // 1000) % 60
        minutes = (current_time // 60000)

        return f"{minutes:02d}:{seconds:02d}.{tenths}"

    def draw(self, screen, font, color, x, y):
        time_str = self.get_time_string()
        img = font.render(time_str, True, color)
        screen.blit(img, (x, y))

    def save_time(self, filename):
        if not self.saved and self.elapsed_time > 0:
            with open(filename, "a", encoding="utf-8") as file:
                # Ukládáme jen čistý čas vítěze
                file.write(f"Vítězný čas: {self.get_time_string()}\n")
            self.saved = True