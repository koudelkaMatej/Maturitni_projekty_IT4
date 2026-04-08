import pygame
import random
from .udalost import Udalost
from .jednotka import Jednotka
from .mapa import Mapa
from .rozhrani import Rozhrani
from config import *

class SpravceHry:
    def __init__(self, screen, obtiznost="Střední"):
        self.screen = screen
        self.mapa = Mapa()
        self.rozhrani = Rozhrani()
        self.jednotky = [
            Jednotka("Policie", (100, 600), (0, 0), (0, 0, 255)),
            Jednotka("Hasiči", (200, 600), (0, 0), (255, 0, 0)),
            Jednotka("Sanitka", (300, 600), (0, 0), (255, 255, 255))
        ]
        self.udalosti = []
        self.vybrana_jednotka = None
        self.skore = 0

        # Obtížnost
        self.obtiznost = obtiznost
        self.spawn_timer = 0
        self.interval_udalosti = self.ziskej_interval(obtiznost)

        # Čas hry (1 minuta)
        self.start_time = pygame.time.get_ticks()
        self.trvani_hry = 60_000  # 1 minuta v ms
        self.konec_hry = False

        self.highscore = {"Lehká":0, "Střední":0, "Těžká":0}

        try:
            self.sirena = pygame.mixer.Sound("assets/siren.wav")
        except:
            self.sirena = None

        self.font_velky = pygame.font.Font(None, 70)
        self.font_maly = pygame.font.Font(None, 40)

    def ziskej_interval(self, obtiznost):
        if obtiznost == "Lehká":
            return 300
        elif obtiznost == "Střední":
            return 180
        elif obtiznost == "Těžká":
            return 90
        return 180

    def handle_event(self, udalost):
        if udalost.type == pygame.KEYDOWN and udalost.key == pygame.K_ESCAPE:
            return "menu"

        if udalost.type == pygame.MOUSEBUTTONDOWN and udalost.button == 1:
            poz = pygame.mouse.get_pos()

            if self.konec_hry:
                if pygame.Rect(300, 300, 200, 50).collidepoint(poz):
                    return "menu"
                elif pygame.Rect(300, 400, 200, 50).collidepoint(poz):
                    return "restart"

            for j in self.jednotky:
                if j.je_kliknuta(poz):
                    self.vybrana_jednotka = j
                    return

            for u in self.udalosti:
                if u.je_kliknuta(poz):
                    if self.vybrana_jednotka:
                        self.vybrana_jednotka.jede_na(u.pozice)
                        u.prirad_jednotku(self.vybrana_jednotka)
                        if self.sirena:
                            self.sirena.play()
            return

    def update(self):
        if self.konec_hry:
            return

        cas_aktualni = pygame.time.get_ticks()
        if cas_aktualni - self.start_time >= self.trvani_hry:
            self.konec_hry = True
            if self.skore > self.highscore[self.obtiznost]:
                self.highscore[self.obtiznost] = self.skore
            return

        self.spawn_timer += 1
        if self.spawn_timer >= self.interval_udalosti:
            self.spawn_nahodnou_udalost()
            self.spawn_timer = 0

        for u in list(self.udalosti):
            u.update()
            if not u.aktivni:
                self.udalosti.remove(u)
                self.skore += 1

        for j in self.jednotky:
            j.update()

    def draw(self):
        self.mapa.draw(self.screen)

        for u in self.udalosti:
            u.draw(self.screen)

        # Jednotky
        for j in self.jednotky:
            j.draw(self.screen)

        # Rozhraní
        self.rozhrani.draw(self.screen, len(self.udalosti), self.skore)

        # --- Čas a highscore během hry ---
        if not self.konec_hry:
            cas_aktualni = pygame.time.get_ticks()
            zbyle_ms = max(0, self.trvani_hry - (cas_aktualni - self.start_time))
            zbyle_s = zbyle_ms // 1000

            # Překreslení oblasti pro čas a highscore (jen pod text)
            pygame.draw.rect(self.screen, SEDA, (WIDTH-310, 10, 300, 120))

            cas_text = self.font_maly.render(f"Čas: {zbyle_s}s", True, (255,255,255))
            high_text = self.font_maly.render(f"Highscore ({self.obtiznost}): {self.highscore[self.obtiznost]}", True, (255,255,0))

            self.screen.blit(cas_text, (WIDTH - 150, 20))
            self.screen.blit(high_text, (WIDTH - 300, 90))  # highscore posunuté o 50 px dolů

        # --- Overlay pro konec hry ---
        if self.konec_hry:
            overlay = pygame.Surface((WIDTH, HEIGHT))
            overlay.set_alpha(180)
            overlay.fill((0,0,0))
            self.screen.blit(overlay, (0,0))

            text = self.font_velky.render("Konec hry!", True, (255,255,255))
            self.screen.blit(text, (WIDTH//2 - text.get_width()//2, 150))

            skore_text = self.font_maly.render(f"Skóre: {self.skore}", True, (255,255,255))
            self.screen.blit(skore_text, (WIDTH//2 - skore_text.get_width()//2, 220))

            high_text = self.font_maly.render(f"Highscore ({self.obtiznost}): {self.highscore[self.obtiznost]}", True, (255,255,0))
            self.screen.blit(high_text, (WIDTH//2 - high_text.get_width()//2, 260))

            # Tlačítka Menu a Hrát znovu
            pygame.draw.rect(self.screen, (100,200,100), (300,300,200,50))
            pygame.draw.rect(self.screen, (200,100,100), (300,400,200,50))

            menu_text = self.font_maly.render("Menu", True, (0,0,0))
            restart_text = self.font_maly.render("Hrát znovu", True, (0,0,0))

            self.screen.blit(menu_text, (300 + 100 - menu_text.get_width()//2, 300 + 25 - menu_text.get_height()//2))
            self.screen.blit(restart_text, (300 + 100 - restart_text.get_width()//2, 400 + 25 - restart_text.get_height()//2))

    def spawn_nahodnou_udalost(self):
        x = random.randint(100, 900)
        y = random.randint(100, 500)
        typ = random.choice(["požár", "nehoda", "krádež"])
        self.udalosti.append(Udalost(typ, (x, y)))
