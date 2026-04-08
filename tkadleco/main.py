"""
main.py - Hlavní spouštěcí soubor hry City Rescue Simulator
Autor: [tvoje jméno]

Řešení rozlišení:
  Hra se vždy renderuje do fixní surface (GAME_W × GAME_H = 1000×700).
  Ta se pak pomocí pygame.transform.smoothscale() natáhne na aktuální
  velikost okna se zachováním poměru stran (letterbox/pillarbox).
  Díky tomu všechny souřadnice v kódu (WIDTH, HEIGHT z config.py)
  zůstávají stále stejné a obsah se automaticky přizpůsobí oknu.

Stavový automat:
  STAV_MENU → STAV_HRA / STAV_NASTAVENI / STAV_TUTORIAL / STAV_SCOREBOARD
  Každý stav má svůj objekt (menu, hra, ...) který dostane game_surface.
"""

import pygame 
from config import *
from classes import mys
from classes.menu import Menu
from classes.spravce_hry import SpravceHry
from classes.nastaveni import Nastaveni
from classes.tutorial import Tutorial
from classes.scoreboard import Scoreboard

pygame.init()  # Inicializace Pygame — musí být před vytvořením fontů a Surface

# Fixní rozměr herní plochy — všechny třídy kreslí na tuto surface
GAME_W, GAME_H = WIDTH, HEIGHT   # 1000 × 700 z config.py

# Skutečné okno — může mít jiné rozlišení než GAME_W × GAME_H
okno_res = MOZNOSTI_ROZLISENI[INDEX_ROZLISENI]
window   = pygame.display.set_mode(okno_res, pygame.RESIZABLE)
pygame.display.set_caption("Simulátor IZS")
clock = pygame.time.Clock()

# Fixní surface — veškeré vykreslování probíhá sem, pak se natáhne na okno
game_surface = pygame.Surface((GAME_W, GAME_H))

# Stavy
STAV_MENU       = 0
STAV_HRA        = 1
STAV_NASTAVENI  = 2
STAV_TUTORIAL   = 3
STAV_SCOREBOARD = 4

stav = STAV_MENU

# Nastaveni
obtiznost    = "Střední"
aktualni_res = okno_res

# Herní objekty — všechny dostanou game_surface (ne okno)
menu              = Menu(game_surface)
nastaveni_screen  = Nastaveni(game_surface)
tutorial_screen   = Tutorial(game_surface)
scoreboard_screen = Scoreboard(game_surface)
hra               = SpravceHry(game_surface, obtiznost)


def prepni_rozliseni(nova_res):
    """
    Změní velikost okna. game_surface zůstává stejná,
    jen se jinak natáhne. Nevyžaduje znovu vytvořit herní objekty.

    Args:
        nova_res (tuple): (šířka, výška) nového okna
    """
    global window, aktualni_res
    window       = pygame.display.set_mode(nova_res, pygame.RESIZABLE)
    aktualni_res = nova_res


def scale_a_zobraz():
    """
    Natáhne game_surface na velikost aktuálního okna a zobrazí.

    Zachovává poměr stran (letterbox) — kolem může být černý okraj.
    Používá smoothscale pro kvalitnější výsledek při zvětšení.
    """
    ww, wh = window.get_size()
    gw, gh = GAME_W, GAME_H

    # Největší možný scale se zachováním poměru stran
    scale = min(ww / gw, wh / gh)
    sw    = int(gw * scale)
    sh    = int(gh * scale)
    ox    = (ww - sw) // 2   # vodorovný offset pro centrování
    oy    = (wh - sh) // 2   # svislý offset pro centrování

    window.fill((0, 0, 0))   # černý letterbox okraj
    scaled = pygame.transform.smoothscale(game_surface, (sw, sh))
    window.blit(scaled, (ox, oy))


def prepocti_mys():
    """
    Přepočítá pozici myši z prostoru okna do prostoru game_surface.

    Pygame vrací souřadnice v prostoru okna. Tato funkce je převede
    na souřadnice herní plochy (1000×700) s ohledem na scale a offset.

    Returns:
        tuple: (x, y) oříznuté na rozsah [0, GAME_W-1] × [0, GAME_H-1]
    """
    mx, my = pygame.mouse.get_pos()
    ww, wh = window.get_size()
    scale  = min(ww / GAME_W, wh / GAME_H)
    sw     = int(GAME_W * scale)
    sh     = int(GAME_H * scale)
    ox     = (ww - sw) // 2
    oy     = (wh - sh) // 2
    gx     = int((mx - ox) / scale)
    gy     = int((my - oy) / scale)
    # Ořízni na hranice herní plochy
    return (
        max(0, min(GAME_W - 1, gx)),
        max(0, min(GAME_H - 1, gy))
    )


class MysEvent:
    """
    Obaluje pygame event a nahrazuje pozici myši přepočítanou
    do souřadnic game_surface.

    Důvod: pygame.MOUSEBUTTONDOWN a spol. obsahují pozici v prostoru okna.
    Obalením události sem zajistíme, že všechny třídy dostanou
    správné souřadnice bez dalšího přepočítávání.
    """
    def __init__(self, original, nova_pos):
        """
        Args:
            original:  Původní pygame Event objekt
            nova_pos:  Přepočítaná pozice (x, y) v herním prostoru
        """
        self._orig   = original
        self.type    = original.type
        self.button  = getattr(original, "button",  None)
        self.pos     = nova_pos   # přepsaná pozice!
        self.key     = getattr(original, "key",     None)
        self.unicode = getattr(original, "unicode", "")
        self.rel     = getattr(original, "rel",     (0, 0))


bezi = True
while bezi:
    for udalost in pygame.event.get():
        if udalost.type == pygame.QUIT:
            bezi = False
            continue

        # Prepocti pozici mysi pro vsechny mouse eventy
        if udalost.type in (pygame.MOUSEBUTTONDOWN,
                            pygame.MOUSEBUTTONUP,
                            pygame.MOUSEMOTION):
            udalost = MysEvent(udalost, prepocti_mys())

        if stav == STAV_MENU:
            vysledek = menu.handle_event(udalost)
            if vysledek == "hrat":
                hra   = SpravceHry(game_surface, obtiznost)
                stav  = STAV_HRA
            elif vysledek == "nastaveni":
                stav = STAV_NASTAVENI
            elif vysledek == "tutorial":
                stav = STAV_TUTORIAL
            elif vysledek == "scoreboard":
                scoreboard_screen.nacti_skore()
                stav = STAV_SCOREBOARD
            elif vysledek == "konec":
                bezi = False

        elif stav == STAV_HRA:
            vysledek = hra.handle_event(udalost)
            if vysledek == "menu":
                stav = STAV_MENU
            elif vysledek == "restart":
                hra = SpravceHry(game_surface, obtiznost)

        elif stav == STAV_NASTAVENI:
            vysledek = nastaveni_screen.handle_event(udalost)
            if vysledek == "ulozit":
                obtiznost = nastaveni_screen.obtiznost
                nova_res  = nastaveni_screen.rozliseni
                if nova_res != aktualni_res:
                    prepni_rozliseni(nova_res)
                stav = STAV_MENU
            elif vysledek == "zpet":
                stav = STAV_MENU

        elif stav == STAV_TUTORIAL:
            vysledek = tutorial_screen.handle_event(udalost)
            if vysledek == "menu":
                stav = STAV_MENU

        elif stav == STAV_SCOREBOARD:
            vysledek = scoreboard_screen.handle_event(udalost)
            if vysledek == "menu":
                stav = STAV_MENU

    # Aktualizuj sdilenou pozici mysi (prepoctenou do game_surface souradnic)
    mx, my = prepocti_mys()
    mys.set_pos(mx, my)

    # Render do game_surface
    if stav == STAV_MENU:
        menu.draw()
    elif stav == STAV_HRA:
        hra.update()
        hra.draw()
    elif stav == STAV_NASTAVENI:
        nastaveni_screen.draw()
    elif stav == STAV_TUTORIAL:
        tutorial_screen.draw()
    elif stav == STAV_SCOREBOARD:
        scoreboard_screen.draw()

    # Natahni game_surface na okno a zobraz
    scale_a_zobraz()
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
