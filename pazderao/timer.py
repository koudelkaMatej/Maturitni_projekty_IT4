import pygame

class Timer:
    def __init__(self, screen, font_path, size=20):
        self.screen = screen
        # Použijeme malý font lemonmilk
        self.font = pygame.font.Font(font_path, size)
        self.start_ticks = 0
        self.running = False
        self.elapsed_time = 0

    def start(self):
        """Spustí nebo restartuje časovač."""
        self.start_ticks = pygame.time.get_ticks()
        self.running = True

    def stop(self):
        """Zastaví časovač."""
        self.running = False

    def reset(self):
        """Vynuluje časovač."""
        self.start_ticks = pygame.time.get_ticks()
        self.elapsed_time = 0

    def update(self):
        """Aktualizuje uběhlý čas, pokud časovač běží."""
        if self.running:
            # Převod milisekund na sekundy
            self.elapsed_time = (pygame.time.get_ticks() - self.start_ticks) // 1000

    def draw(self):
        """Vykreslí časovač v levém horním rohu."""
        minutes = self.elapsed_time // 60
        seconds = self.elapsed_time % 60
        # Formátování času na 00:00
        time_str = f"TIME: {minutes:02}:{seconds:02}"
        
        timer_surface = self.font.render(time_str, True, (255, 255, 255))
        # Umístění do levého horního rohu (s malým odstupem 10px)
        self.screen.blit(timer_surface, (10, 10))