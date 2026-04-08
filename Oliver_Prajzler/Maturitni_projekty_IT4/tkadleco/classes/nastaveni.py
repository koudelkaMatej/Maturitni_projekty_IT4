import pygame
from config import *

class Nastaveni:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.Font(None, 60)
        self.mensi_font = pygame.font.Font(None, 36)

        self.index_mapy = 0
        self.index_rozliseni = INDEX_ROZLISENI
        self.hlasitost = HLASITOST
        self.fps = FPS

        self.obtiznosti = ["Lehká", "Střední", "Těžká"]
        self.aktualni_obtiznost = 1
        self.obtiznost = self.obtiznosti[self.aktualni_obtiznost]

        self.tlacitka = {
            "zpet": pygame.Rect(20, 20, 150, 50),
            "mapa_plus": pygame.Rect(750, 200, 50, 50),
            "mapa_minus": pygame.Rect(575, 200, 50, 50),
            "rozliseni_plus": pygame.Rect(800, 300, 50, 50),
            "rozliseni_minus": pygame.Rect(575, 300, 50, 50),
            "hlasitost_plus": pygame.Rect(750, 400, 50, 50),
            "hlasitost_minus": pygame.Rect(575, 400, 50, 50),
            "fps_plus": pygame.Rect(750, 500, 50, 50),
            "fps_minus": pygame.Rect(575, 500, 50, 50),
            "obtiznost_plus": pygame.Rect(750, 600, 50, 50),
            "obtiznost_minus": pygame.Rect(575, 600, 50, 50),
        }

    def handle_event(self, udalost):
        if udalost.type == pygame.MOUSEBUTTONDOWN and udalost.button == 1:
            poz = pygame.mouse.get_pos()

            if self.tlacitka["zpet"].collidepoint(poz):
                return "menu"

            if self.tlacitka["mapa_plus"].collidepoint(poz):
                self.index_mapy = (self.index_mapy + 1) % 3
            elif self.tlacitka["mapa_minus"].collidepoint(poz):
                self.index_mapy = (self.index_mapy - 1) % 3

            elif self.tlacitka["rozliseni_plus"].collidepoint(poz):
                self.index_rozliseni = (self.index_rozliseni + 1) % len(MOZNOSTI_ROZLISENI)
            elif self.tlacitka["rozliseni_minus"].collidepoint(poz):
                self.index_rozliseni = (self.index_rozliseni - 1) % len(MOZNOSTI_ROZLISENI)

            elif self.tlacitka["hlasitost_plus"].collidepoint(poz):
                self.hlasitost = min(1.0, self.hlasitost + 0.1)
            elif self.tlacitka["hlasitost_minus"].collidepoint(poz):
                self.hlasitost = max(0.0, self.hlasitost - 0.1)

            elif self.tlacitka["fps_plus"].collidepoint(poz):
                self.fps += 5
            elif self.tlacitka["fps_minus"].collidepoint(poz):
                self.fps = max(30, self.fps - 5)

            elif self.tlacitka["obtiznost_plus"].collidepoint(poz):
                self.aktualni_obtiznost = (self.aktualni_obtiznost + 1) % len(self.obtiznosti)
                self.obtiznost = self.obtiznosti[self.aktualni_obtiznost]
            elif self.tlacitka["obtiznost_minus"].collidepoint(poz):
                self.aktualni_obtiznost = (self.aktualni_obtiznost - 1) % len(self.obtiznosti)
                self.obtiznost = self.obtiznosti[self.aktualni_obtiznost]

        return None

    def draw(self):
        self.screen.fill(SEDA)

        nadpis = self.font.render("Nastavení", True, BILA)
        self.screen.blit(nadpis, (WIDTH//2 - nadpis.get_width()//2, 50))

        self.screen.blit(self.mensi_font.render("Mapa:", True, BILA), (50, 200))
        self.screen.blit(self.mensi_font.render(f"Mapa {self.index_mapy+1}", True, BILA), (650, 200))
        pygame.draw.rect(self.screen, MODRA, self.tlacitka["mapa_plus"])
        pygame.draw.rect(self.screen, MODRA, self.tlacitka["mapa_minus"])
        self.screen.blit(self.mensi_font.render("+", True, BILA), (765, 205))
        self.screen.blit(self.mensi_font.render("-", True, BILA), (590, 205))

        self.screen.blit(self.mensi_font.render("Rozlišení:", True, BILA), (50, 300))
        res = MOZNOSTI_ROZLISENI[self.index_rozliseni]
        self.screen.blit(self.mensi_font.render(f"{res[0]}x{res[1]}", True, BILA), (650, 300))
        pygame.draw.rect(self.screen, MODRA, self.tlacitka["rozliseni_plus"])
        pygame.draw.rect(self.screen, MODRA, self.tlacitka["rozliseni_minus"])
        self.screen.blit(self.mensi_font.render("+", True, BILA), (815, 305))
        self.screen.blit(self.mensi_font.render("-", True, BILA), (590, 305))

        self.screen.blit(self.mensi_font.render("Hlasitost:", True, BILA), (50, 400))
        self.screen.blit(self.mensi_font.render(f"{int(self.hlasitost*100)}%", True, BILA), (650, 400))
        pygame.draw.rect(self.screen, MODRA, self.tlacitka["hlasitost_plus"])
        pygame.draw.rect(self.screen, MODRA, self.tlacitka["hlasitost_minus"])
        self.screen.blit(self.mensi_font.render("+", True, BILA), (765, 405))
        self.screen.blit(self.mensi_font.render("-", True, BILA), (590, 405))

        self.screen.blit(self.mensi_font.render("FPS:", True, BILA), (50, 500))
        self.screen.blit(self.mensi_font.render(str(self.fps), True, BILA), (650, 500))
        pygame.draw.rect(self.screen, MODRA, self.tlacitka["fps_plus"])
        pygame.draw.rect(self.screen, MODRA, self.tlacitka["fps_minus"])
        self.screen.blit(self.mensi_font.render("+", True, BILA), (765, 505))
        self.screen.blit(self.mensi_font.render("-", True, BILA), (590, 505))

        # --- OBTÍŽNOST ---
        self.screen.blit(self.mensi_font.render("Obtížnost:", True, BILA), (50, 600))
        self.screen.blit(self.mensi_font.render(self.obtiznosti[self.aktualni_obtiznost], True, BILA), (650, 600))
        pygame.draw.rect(self.screen, MODRA, self.tlacitka["obtiznost_plus"])
        pygame.draw.rect(self.screen, MODRA, self.tlacitka["obtiznost_minus"])
        self.screen.blit(self.mensi_font.render("+", True, BILA), (765, 605))
        self.screen.blit(self.mensi_font.render("-", True, BILA), (590, 605))

        # --- ZPĚT ---
        pygame.draw.rect(self.screen, MODRA, self.tlacitka["zpet"])
        self.screen.blit(self.mensi_font.render("Zpět", True, BILA), (35, 30))
