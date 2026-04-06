"""
mys.py - Sdílená pozice myši v souřadnicovém systému hry
Autor: [tvoje jméno]

Problém: pygame.mouse.get_pos() vrací souřadnice okna.
Po změně rozlišení (scale) jsou tato čísla jiná než
souřadnice game_surface (1000×700).

Řešení: main.py každý snímek přepočítá pozici myši a
uloží ji sem přes set_pos(). Všechny třídy pak volají
get_pos() z tohoto modulu místo pygame.mouse.get_pos().
"""

# Aktuální přepočítaná pozice myši v souřadnicovém systému hry (1000×700)
_pos = (0, 0)


def set_pos(x, y):
    """
    Nastaví přepočítanou pozici myši.

    Volá se z main.py každý snímek po přepočtu z rozlišení okna
    na souřadnice herní plochy (game_surface).

    Args:
        x (int): X souřadnice v herním prostoru
        y (int): Y souřadnice v herním prostoru
    """
    global _pos
    _pos = (x, y)


def get_pos():
    """
    Vrátí aktuální pozici myši v souřadnicovém systému hry.

    Používej tuto funkci místo pygame.mouse.get_pos()
    ve všech herních třídách — jinak se klikání chová špatně
    při jiném rozlišení okna než 1000×700.

    Returns:
        tuple: (x, y) v souřadnicích herní plochy
    """
    return _pos
