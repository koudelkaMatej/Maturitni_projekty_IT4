import pygame
from config import *

class Tutorial:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.Font(None, 60)
        self.mensi_font = pygame.font.Font(None, 32)
        self.tlacitko_zpet = pygame.Rect(20, 20, 150, 50)

        self.text = [
            "🎮 City Rescue Simulator 🎮",
            "",
            "Cíl hry:",
            "Řiď městské záchranné složky – policii, hasiče a sanitku.",
            "Reaguj rychle na náhodné události, které se objevují na mapě.",
            "Za každou úspěšně vyřešenou událost získáváš body.",
            "",
            "Ovládání:",
            "- Klikni na jednotku, kterou chceš poslat do akce.",
            "- Poté klikni na událost na mapě, kam má jednotka dorazit.",
            "- Když jednotka dorazí, událost se vyřeší a zmizí.",
            "",
            "Hra končí po určitém čase nebo když nezvládneš řešit události včas.",
            "",
            "Hodně štěstí, veliteli!",
        ]

    def handle_event(self, udalost):
        if udalost.type == pygame.MOUSEBUTTONDOWN and udalost.button == 1:
            if self.tlacitko_zpet.collidepoint(udalost.pos):
                return "menu"

    def draw(self):
        self.screen.fill(SEDA)

        nadpis = self.font.render("TUTORIÁL", True, BILA)
        self.screen.blit(nadpis, (WIDTH//2 - nadpis.get_width()//2, 50))

        y = 150
        for radek in self.text:
            barva = ZLUTA if "🎮" in radek else BILA
            text_surface = self.mensi_font.render(radek, True, barva)
            self.screen.blit(text_surface, (80, y))
            y += 40

        pygame.draw.rect(self.screen, MODRA, self.tlacitko_zpet)
        self.screen.blit(self.mensi_font.render("Zpět", True, BILA), (45, 30))
