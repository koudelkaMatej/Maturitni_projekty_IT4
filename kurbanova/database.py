"""
Modul pro práci s SQLite databází.
Obsahuje funkce pro inicializaci, ukládání a čtení dat.
Všechny funkce jsou ošetřeny proti chybám a vracejí konzistentní výsledky.
"""

import sqlite3
import datetime
import os

DB_NAME = 'player_scores.db'

def get_connection():
    """Vytvoří a vrátí spojení s databází s povolenými cizími klíči."""
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db():
    """
    Vytvoří všechny tabulky, pokud neexistují.
    Volá se při startu hry.
    """
    try:
        conn = get_connection()
        c = conn.cursor()

        # Tabulka uživatelů
        c.execute('''CREATE TABLE IF NOT EXISTS users
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      username TEXT UNIQUE NOT NULL,
                      password_hash TEXT,
                      is_admin INTEGER DEFAULT 0,
                      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')

        # Tabulka her (session)
        c.execute('''CREATE TABLE IF NOT EXISTS games
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      user_id INTEGER NOT NULL,
                      start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                      end_time TIMESTAMP,
                      FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE)''')

        # Tabulka skóre (jedna hra = jeden záznam)
        c.execute('''CREATE TABLE IF NOT EXISTS scores
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      game_id INTEGER UNIQUE NOT NULL,
                      level INTEGER NOT NULL,
                      stars INTEGER NOT NULL,
                      FOREIGN KEY (game_id) REFERENCES games(id) ON DELETE CASCADE)''')

        # Tabulka achievementů
        c.execute('''CREATE TABLE IF NOT EXISTS achievements
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      name TEXT UNIQUE NOT NULL,
                      description TEXT)''')

        # Tabulka pro M:N vztah uživatelů a achievementů
        c.execute('''CREATE TABLE IF NOT EXISTS user_achievements
                     (user_id INTEGER NOT NULL,
                      achievement_id INTEGER NOT NULL,
                      earned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                      PRIMARY KEY (user_id, achievement_id),
                      FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                      FOREIGN KEY (achievement_id) REFERENCES achievements(id) ON DELETE CASCADE)''')

        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Chyba při inicializaci databáze: {e}")

# ----- Uživatelé -----
def add_user(username, password_hash=None, is_admin=0):
    """
    Přidá nového uživatele.

    Args:
        username (str): Jméno uživatele.
        password_hash (str, optional): Hash hesla (pro web).
        is_admin (int): 1 pokud admin, jinak 0.

    Returns:
        int or None: ID nového uživatele nebo None, pokud jméno již existuje nebo došlo k chybě.
    """
    try:
        conn = get_connection()
        c = conn.cursor()
        c.execute("INSERT INTO users (username, password_hash, is_admin) VALUES (?, ?, ?)",
                  (username, password_hash, is_admin))
        user_id = c.lastrowid
        conn.commit()
        conn.close()
        return user_id
    except sqlite3.IntegrityError:
        # Uživatelské jméno již existuje
        return None
    except Exception as e:
        print(f"Chyba při přidávání uživatele: {e}")
        return None

def get_user_by_username(username):
    """
    Vrátí uživatele podle jména.

    Args:
        username (str): Jméno uživatele.

    Returns:
        dict or None: Slovník s údaji uživatele (id, username, password_hash, is_admin) nebo None.
    """
    try:
        conn = get_connection()
        c = conn.cursor()
        c.execute("SELECT id, username, password_hash, is_admin FROM users WHERE username = ?", (username,))
        row = c.fetchone()
        conn.close()
        if row:
            return {'id': row[0], 'username': row[1], 'password_hash': row[2], 'is_admin': row[3]}
        return None
    except Exception as e:
        print(f"Chyba při získávání uživatele: {e}")
        return None

# ----- Hry a skóre -----
def start_game(user_id):
    """
    Zahájí novou hru pro uživatele.

    Args:
        user_id (int): ID uživatele.

    Returns:
        int or None: ID nové hry nebo None při chybě.
    """
    try:
        conn = get_connection()
        c = conn.cursor()
        c.execute("INSERT INTO games (user_id) VALUES (?)", (user_id,))
        game_id = c.lastrowid
        conn.commit()
        conn.close()
        return game_id
    except Exception as e:
        print(f"Chyba při startování hry: {e}")
        return None

def end_game(game_id):
    """
    Ukončí hru (nastaví end_time na aktuální čas).

    Args:
        game_id (int): ID hry.
    """
    try:
        conn = get_connection()
        c = conn.cursor()
        c.execute("UPDATE games SET end_time = ? WHERE id = ?", (datetime.datetime.now(), game_id))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Chyba při ukončování hry: {e}")

def save_score(game_id, level, stars):
    """
    Uloží výsledek hry.

    Args:
        game_id (int): ID hry.
        level (int): Dosažený level.
        stars (int): Počet hvězd.
    """
    try:
        conn = get_connection()
        c = conn.cursor()
        c.execute("INSERT INTO scores (game_id, level, stars) VALUES (?, ?, ?)",
                  (game_id, level, stars))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Chyba při ukládání skóre: {e}")

def get_leaderboard(limit=10):
    """
    Vrátí žebříček nejlepších výsledků.

    Args:
        limit (int): Maximální počet záznamů.

    Returns:
        list of dict: Seznam výsledků, každý s klíči 'username', 'level', 'stars', 'date'.
                     V případě chyby vrací prázdný seznam.
    """
    try:
        conn = get_connection()
        c = conn.cursor()
        c.execute('''
            SELECT users.username, scores.level, scores.stars, games.start_time
            FROM scores
            JOIN games ON scores.game_id = games.id
            JOIN users ON games.user_id = users.id
            ORDER BY scores.stars DESC, scores.level DESC
            LIMIT ?
        ''', (limit,))
        rows = c.fetchall()
        conn.close()
        result = []
        for r in rows:
            # Ošetření, kdyby start_time bylo None (nemělo by nastat)
            date_str = r[3][:10] if r[3] and len(r[3]) >= 10 else "?"
            result.append({'username': r[0], 'level': r[1], 'stars': r[2], 'date': date_str})
        return result
    except Exception as e:
        print(f"Chyba při načítání žebříčku: {e}")
        return []

# ----- Achievementy -----
def add_achievement(name, description):
    """
    Přidá nový achievement.

    Args:
        name (str): Název achievementu.
        description (str): Popis.
    """
    try:
        conn = get_connection()
        c = conn.cursor()
        c.execute("INSERT OR IGNORE INTO achievements (name, description) VALUES (?, ?)", (name, description))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Chyba při přidávání achievementu: {e}")

def award_achievement(user_id, achievement_name):
    """
    Udělí uživateli achievement (pokud ho ještě nemá).

    Args:
        user_id (int): ID uživatele.
        achievement_name (str): Název achievementu.
    """
    try:
        conn = get_connection()
        c = conn.cursor()
        # získáme id achievementu
        c.execute("SELECT id FROM achievements WHERE name = ?", (achievement_name,))
        row = c.fetchone()
        if row:
            ach_id = row[0]
            c.execute("INSERT OR IGNORE INTO user_achievements (user_id, achievement_id) VALUES (?, ?)",
                      (user_id, ach_id))
            conn.commit()
        conn.close()
    except Exception as e:
        print(f"Chyba při udělování achievementu: {e}")

def get_user_achievements(user_id):
    """
    Vrátí seznam achievementů uživatele.

    Args:
        user_id (int): ID uživatele.

    Returns:
        list of dict: Seznam achievementů s názvem, popisem a datem získání.
    """
    try:
        conn = get_connection()
        c = conn.cursor()
        c.execute('''
            SELECT achievements.name, achievements.description, user_achievements.earned_at
            FROM user_achievements
            JOIN achievements ON user_achievements.achievement_id = achievements.id
            WHERE user_achievements.user_id = ?
            ORDER BY user_achievements.earned_at
        ''', (user_id,))
        rows = c.fetchall()
        conn.close()
        return [{'name': r[0], 'description': r[1], 'earned_at': r[2]} for r in rows]
    except Exception as e:
        print(f"Chyba při načítání achievementů: {e}")
        return []