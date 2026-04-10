#!/usr/bin/env python3
"""
Inicializační skript pro vytvoření databáze a naplnění vzorovými daty.
Lze spustit samostatně pro reset databáze.
"""
import os
import sqlite3
import datetime
import database as db

def init_and_fill():
    # 1. Smažeme starý databázový soubor, pokud existuje
    db_file = db.DB_NAME  # název souboru z modulu database
    if os.path.exists(db_file):
        os.remove(db_file)
        print(f"Smazán starý soubor: {db_file}")

    # 2. Inicializace tabulek (vytvoří nové)
    db.init_db()

    # 3. Připojení k databázi
    conn = db.get_connection()
    c = conn.cursor()

    # 4. Vložení vzorových uživatelů (bez hesel)
    users = [('alice', 0), ('bob', 0), ('carol', 1), ('dave', 0)]
    for username, admin in users:
        c.execute("INSERT OR IGNORE INTO users (username, is_admin) VALUES (?, ?)", (username, admin))

    # 5. Vložení achievementů
    achievements = [
        ('První krok', 'Dokonči první level'),
        ('Sběratel', 'Seber 10 hvězd'),
        ('Nezničitelný', 'Dokonči level bez smrti')
    ]
    for name, desc in achievements:
        c.execute("INSERT OR IGNORE INTO achievements (name, description) VALUES (?, ?)", (name, desc))

    conn.commit()

    # 6. Získání ID uživatelů
    c.execute("SELECT id, username FROM users")
    user_ids = {row[1]: row[0] for row in c.fetchall()}

    # 7. Vložení her a skóre
    games_data = [
        (user_ids['alice'], 1, 3, datetime.datetime.now()),
        (user_ids['alice'], 2, 5, datetime.datetime.now() - datetime.timedelta(days=1)),
        (user_ids['bob'], 1, 2, datetime.datetime.now()),
        (user_ids['bob'], 2, 4, datetime.datetime.now() - datetime.timedelta(days=2)),
        (user_ids['carol'], 3, 7, datetime.datetime.now()),
    ]

    for uid, lvl, stars, start in games_data:
        # Vložení hry
        c.execute("INSERT INTO games (user_id, start_time) VALUES (?, ?)", (uid, start))
        game_id = c.lastrowid

        # Vložení skóre – zde se používá sloupec game_id, který už v tabulce existuje
        c.execute("INSERT INTO scores (game_id, level, stars) VALUES (?, ?, ?)", (game_id, lvl, stars))

        # Aktualizace end_time hry
        c.execute("UPDATE games SET end_time = ? WHERE id = ?", (start + datetime.timedelta(minutes=2), game_id))

    conn.commit()

    # 8. Udělení achievementů
    c.execute("SELECT id FROM achievements WHERE name = 'První krok'")
    ach1 = c.fetchone()[0]
    c.execute("SELECT id FROM achievements WHERE name = 'Sběratel'")
    ach2 = c.fetchone()[0]

    conn.commit()
    conn.close()

    print("Databáze byla inicializována a naplněna vzorovými daty.")
    print("\n--- Ukázkové dotazy ---")
    # Zavolá funkci s ukázkovými dotazy (musí být definována v database.py)
    try:
        db.example_queries()
    except AttributeError:
        print("Funkce example_queries není v database.py definována.")

if __name__ == "__main__":
    init_and_fill()