import pygame
from config import *
from classes.menu import Menu
from classes.spravce_hry import SpravceHry
from classes.nastaveni import Nastaveni
from classes.tutorial import Tutorial

pygame.init()
pygame.mixer.init()

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Simulátor IZS")
clock = pygame.time.Clock()

STAV_MENU = 0
STAV_HRA = 1
STAV_NASTAVENI = 2
STAV_TUTORIAL = 3

stav = STAV_MENU

menu = Menu(screen)
nastaveni_screen = Nastaveni(screen)
tutorial_screen = Tutorial(screen)

obtiznost = "Střední"
hra = SpravceHry(screen, obtiznost)

bezi = True
while bezi:
    for udalost in pygame.event.get():
        if udalost.type == pygame.QUIT:
            bezi = False

        if stav == STAV_MENU:
            vysledek = menu.handle_event(udalost)
            if vysledek == "hrat":
                hra = SpravceHry(screen, obtiznost)
                stav = STAV_HRA
            elif vysledek == "nastaveni":
                stav = STAV_NASTAVENI
            elif vysledek == "tutorial":
                stav = STAV_TUTORIAL
            elif vysledek == "konec":
                bezi = False

        elif stav == STAV_HRA:
            vysledek = hra.handle_event(udalost)
            if vysledek == "menu":
                stav = STAV_MENU
            elif vysledek == "restart":
                hra = SpravceHry(screen, obtiznost)

        elif stav == STAV_NASTAVENI:
            vysledek = nastaveni_screen.handle_event(udalost)
            if vysledek == "menu":
                obtiznost = nastaveni_screen.obtiznost
                stav = STAV_MENU

        elif stav == STAV_TUTORIAL:
            vysledek = tutorial_screen.handle_event(udalost)
            if vysledek == "menu":
                stav = STAV_MENU

    if stav == STAV_MENU:
        menu.draw()
    elif stav == STAV_HRA:
        hra.update()
        hra.draw()
    elif stav == STAV_NASTAVENI:
        nastaveni_screen.draw()
    elif stav == STAV_TUTORIAL:
        tutorial_screen.draw()

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
