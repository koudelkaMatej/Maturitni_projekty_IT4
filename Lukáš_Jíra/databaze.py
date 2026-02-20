import sqlite3
import os
from datetime import datetime


ADRESAR = os.path.dirname(os.path.abspath(__file__))
SOUBOR = os.path.join(ADRESAR, "skore.db")


def vytvorit_tabulku():
    conn = sqlite3.connect(SOUBOR)
    cursor = conn.cursor()
   
    # Tabulka pro skóre
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS vysledky (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            jmeno TEXT,
            body INTEGER,
            datum TEXT
        )
    """)
   
    # NOVÉ: Tabulka pro uživatele (jmeno musí být UNIQUE = nesmí se opakovat)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS uzivatele (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            jmeno TEXT UNIQUE,
            heslo TEXT
        )
    """)
    conn.commit()
    conn.close()


# --- NOVÉ FUNKCE PRO ÚČTY ---
def registrace(jmeno, heslo):
    """Zkusí vytvořit uživatele. Pokud jméno existuje, vrátí False."""
    conn = sqlite3.connect(SOUBOR)
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO uzivatele (jmeno, heslo) VALUES (?, ?)", (jmeno, heslo))
        conn.commit()
        uspech = True
    except sqlite3.IntegrityError:
        # IntegrityError nastane, když se poruší pravidlo UNIQUE (jméno už v databázi je)
        uspech = False
   
    conn.close()
    return uspech


def prihlaseni(jmeno, heslo):
    """Zkontroluje, jestli jméno a heslo sedí."""
    conn = sqlite3.connect(SOUBOR)
    cursor = conn.cursor()
   
    cursor.execute("SELECT * FROM uzivatele WHERE jmeno = ? AND heslo = ?", (jmeno, heslo))
    uzivatel = cursor.fetchone() # Zkusí najít jeden řádek
   
    conn.close()
   
    if uzivatel is not None:
        return True # Našli jsme ho
    else:
        return False # Špatné jméno nebo heslo


# --- STARÉ FUNKCE PRO SKÓRE ---
def pridat_vysledek(jmeno, body):
    conn = sqlite3.connect(SOUBOR)
    cursor = conn.cursor()
    cas = datetime.now().strftime("%d.%m.%Y %H:%M")
    cursor.execute("INSERT INTO vysledky (jmeno, body, datum) VALUES (?, ?, ?)", (jmeno, body, cas))
    conn.commit()
    conn.close()


def ziskej_data():
    conn = sqlite3.connect(SOUBOR)
    cursor = conn.cursor()
    cursor.execute("SELECT jmeno, body, datum FROM vysledky ORDER BY body DESC")
    data = cursor.fetchall()
    conn.close()
    return data


