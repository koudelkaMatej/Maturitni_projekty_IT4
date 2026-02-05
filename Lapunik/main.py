import pygame

from menu import Menu
from game import Game
from settings import *


def main():

    pygame.init()

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Goblin Invasion")

    running = True

    while running:

        menu = Menu(screen)
        username = menu.run()

        # Zavření z menu
        if username is None:
            running = False
            break

        game = Game(screen, username)
        result = game.run()

        # Pokud hra řekne, že končíme
        if result == "EXIT":
            running = False


    pygame.quit()


if __name__ == "__main__":
    main()
