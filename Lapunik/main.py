# main.py – Vstupní bod aplikace Pixel Invaders
# Inicializuje Pygame, načte konfiguraci a řídí přechody mezi menu a hrou.

import pygame
import json
import os
from database import Database
from menu import Menu
from game import Game

def load_config():
    """
    Pokusí se načíst uložené nastavení okna (rozlišení a fullscreen) ze souboru config.json.
    Představuje trvalý mechanismus pro ukládání stavu aplikace (I/O operace do lokálního filesystému).
    Vrací slovník s konfigurací, nebo výchozí hodnoty v případě chyby či u prvního spuštění.
    """
    if os.path.exists("config.json"):
        try:
            with open("config.json", "r") as f:
                return json.load(f)
        except: pass
    return {"width": 800, "height": 600, "fullscreen": False}

def main():
    """
    Hlavní vstupní bod aplikace (Entry Point). 
    - Inicializuje grafický subsystém Pygame.
    - Zabezpečuje střídání dvou hlavních instancí: Menu a Samotné hry (Game).
    - Předává jim stejný referenční objekt databáze.
    - Zastřešuje bezpečné ukončení aplikace a cyklu while.
    """
    pygame.init()

    # Načtení nastavení okna z config.json (rozlišení, fullscreen)
    conf = load_config()
    flags = pygame.FULLSCREEN if conf.get("fullscreen") else 0
    w = 0 if conf.get("fullscreen") else conf.get("width", 800)
    h = 0 if conf.get("fullscreen") else conf.get("height", 600)

    screen = pygame.display.set_mode((w, h), flags)
    pygame.display.set_caption("Pixel Invaders")

    db = Database()

    # Reference na aktuální hru – umožňuje funkci "Pokračovat" po návratu do menu
    current_game = None

    while True:
        # Aktuální povrch obrazovky (rozlišení se může měnit v menu)
        screen = pygame.display.get_surface()

        # Funkce "Pokračovat" je dostupná pouze tehdy, pokud existuje rozehraná hra
        has_save = (current_game is not None and not current_game.game_over)

        menu = Menu(screen, db, has_save)
        result = menu.run()
        action = result[0]

        if action == "QUIT" or action is None:
            break

        elif action == "NEW":
            # Spuštění nové hry s přihlášeným uživatelem a zvoleným počátečním levelem
            user_data = result[1]
            start_lvl = result[2]
            screen = pygame.display.get_surface()
            current_game = Game(screen, user_data, db, start_level=start_lvl)
            res = current_game.run()
            if res == "EXIT":
                break

        elif action == "RESUME":
            # Pokračování v rozehrané hře; předáme aktuální povrch pro případ změny rozlišení
            screen = pygame.display.get_surface()
            current_game.screen = screen
            current_game.run()
            # Po návratu do menu bude current_game.game_over == True → tlačítko "Pokračovat" zešedne

    db.close()
    pygame.quit()


if __name__ == "__main__":
    main()
