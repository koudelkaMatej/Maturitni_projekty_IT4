import pygame
import math

class Jednotka:
    def __init__(self, jmeno, pozice, rychlost_vec, barva=(255,255,255)):
        self.jmeno = jmeno
        self.start_pozice = list(pozice) # Zapamatovat domov
        self.pozice = list(pozice)
        self.barva = barva
        self.cil = None
        self.speed = 3 # Zrychlíme pro lepší testování

    def jede_na(self, cil_pozice):
        self.cil = cil_pozice

    def update(self):
        # Pokud nemá cíl (akci), jede domů
        aktualni_cil = self.cil if self.cil else self.start_pozice
        
        dx = aktualni_cil[0] - self.pozice[0]
        dy = aktualni_cil[1] - self.pozice[1]
        vzdalenost = math.hypot(dx, dy)

        if vzdalenost < 5:
            # Dorazil k cíli
            if self.cil: 
                self.cil = None # Mise splněna, v příštím cyklu pojede domů
        else:
            # Pohyb
            self.pozice[0] += self.speed * dx / vzdalenost
            self.pozice[1] += self.speed * dy / vzdalenost

    def draw(self, screen):
        pygame.draw.rect(screen, self.barva, (*self.pozice, 30, 20))
        # Indikace mise (žlutá tečka)
        if self.cil:
            pygame.draw.circle(screen, (255, 255, 0), (int(self.pozice[0]+15), int(self.pozice[1]-5)), 4)

    def je_kliknuta(self, pozice):
        return pygame.Rect(*self.pozice, 30, 20).collidepoint(pozice)