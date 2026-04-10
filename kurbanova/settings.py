"""
Modul pro správu nastavení hry (hlasitost) pomocí JSON souboru.
"""

import json
import os

SETTINGS_FILE = 'settings.json'
DEFAULT_SETTINGS = {
    'music_volume': 0.5,
    'sfx_volume': 0.5
}

def load_settings():
    """
    Načte nastavení ze souboru. Pokud soubor neexistuje, vytvoří výchozí.

    Returns:
        dict: Slovník s nastavením (music_volume, sfx_volume).
    """
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    else:
        save_settings(DEFAULT_SETTINGS)
        return DEFAULT_SETTINGS.copy()

def save_settings(settings):
    """
    Uloží nastavení do JSON souboru.

    Args:
        settings (dict): Slovník s nastavením.
    """
    with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
        json.dump(settings, f, indent=4)