import pygame

class Udalost:
    def __init__(self, typ, pozice):
        self.typ = typ
        self.pozice = pozice
        self.timer = 0
        self.aktivni = True
        self.prirazena_jednotka = None

    def prirad_jednotku(self, jednotka):
        self.prirazena_jednotka = jednotka

    def update(self):
        if self.prirazena_jednotka and not self.prirazena_jednotka.cil:
            self.aktivni = False

        self.timer += 1
        if self.timer > 2000:
            self.aktivni = False

    def draw(self, screen):
        if self.typ == "požár":
            barva = (255, 0, 0)
        elif self.typ == "krádež":
            barva = (0, 0, 255)
        else:
            barva = (0, 255, 0)
        pygame.draw.circle(screen, barva, self.pozice, 15)

    def je_kliknuta(self, pozice):
        x, y = pozice
        ux, uy = self.pozice
        return (x - ux) ** 2 + (y - uy) ** 2 <= 15 ** 2
