import pygame
import math

class Jednotka:
    def __init__(self, jmeno, pozice, rychlost_vec, barva=(255,255,255)):
        self.jmeno = jmeno
        self.pozice = list(pozice)
        self.rychlost_vec = rychlost_vec
        self.barva = barva
        self.volna = True
        self.cil = None
        self.speed = 2

    def jede_na(self, cil_pozice):
        self.cil = cil_pozice
        self.volna = False

    def update(self):
        if self.cil:
            dx = self.cil[0] - self.pozice[0]
            dy = self.cil[1] - self.pozice[1]
            vzd = math.hypot(dx, dy)
            if vzd < 3:
                self.cil = None
                self.volna = True
            else:
                self.pozice[0] += self.speed * dx / vzd
                self.pozice[1] += self.speed * dy / vzd

    def draw(self, screen):
        pygame.draw.rect(screen, self.barva, (*self.pozice, 30, 20))
        if not self.volna:
            pygame.draw.circle(screen, (255, 255, 0), (int(self.pozice[0] + 15), int(self.pozice[1]) - 5), 5)

    def je_kliknuta(self, pozice):
        rect = pygame.Rect(*self.pozice, 30, 20)
        return rect.collidepoint(pozice)
