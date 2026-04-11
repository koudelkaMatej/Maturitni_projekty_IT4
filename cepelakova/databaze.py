import sqlite3

DB_PATH = "flappy.db"

def get_db():
    """Vrátí připojení k databázi s řádky jako slovníky."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Vytvoří tabulky, pokud ještě neexistují (volá se při startu)."""
    conn = get_db()
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT DEFAULT 'user'
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS scores (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        score INTEGER NOT NULL,
        difficulty TEXT NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS achievements (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        description TEXT,
        icon TEXT
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS user_achievements (
        user_id INTEGER NOT NULL,
        achievement_id INTEGER NOT NULL,
        earned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
        FOREIGN KEY (achievement_id) REFERENCES achievements(id) ON DELETE CASCADE,
        PRIMARY KEY (user_id, achievement_id)
    )
    """)
    conn.commit()
    conn.close()

def register_user(username, password, role='user'):
    """Zaregistruje nového uživatele. Vrací True/False."""
    conn = get_db()
    c = conn.cursor()
    try:
        c.execute(
            "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
            (username, password, role)
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def get_user_by_username(username):
    """Vrátí uživatele podle jména."""
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = c.fetchone()
    conn.close()
    return user

def get_user_by_id(user_id):
    """Vrátí uživatele podle ID."""
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user = c.fetchone()
    conn.close()
    return user

def save_score(user_id, score, difficulty):
    """Uloží skóre pro přihlášeného uživatele."""
    conn = get_db()
    c = conn.cursor()
    c.execute(
        "INSERT INTO scores (user_id, score, difficulty) VALUES (?, ?, ?)",
        (user_id, score, difficulty)
    )
    conn.commit()
    conn.close()

def get_all_scores():
    """Vrátí všechny skóre i s uživatelskými jmény, seřazené podle skóre."""
    conn = get_db()
    c = conn.cursor()
    c.execute("""
        SELECT scores.id, users.username, scores.score, scores.difficulty
        FROM scores
        JOIN users ON scores.user_id = users.id
        ORDER BY scores.score DESC
    """)
    scores = c.fetchall()
    conn.close()
    return scores

def delete_score(score_id):
    """Smaže skóre podle ID (pouze pro admina)."""
    conn = get_db()
    c = conn.cursor()
    c.execute("DELETE FROM scores WHERE id = ?", (score_id,))
    conn.commit()
    conn.close()

def save_score_by_username(username, score, difficulty):
    """Uloží skóre podle uživatelského jména (vyhledá ID)."""
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT id FROM users WHERE username = ?", (username,))
    user = c.fetchone()
    if user:
        c.execute(
            "INSERT INTO scores (user_id, score, difficulty) VALUES (?, ?, ?)",
            (user["id"], score, difficulty)
        )
        conn.commit()
    conn.close()

def get_all_achievements():
    """Vrátí seznam všech dostupných úspěchů."""
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM achievements ORDER BY id")
    res = c.fetchall()
    conn.close()
    return res

def get_user_achievements(user_id):
    """Vrátí úspěchy, které uživatel získal."""
    conn = get_db()
    c = conn.cursor()
    c.execute("""
        SELECT a.* 
        FROM achievements a
        JOIN user_achievements ua ON a.id = ua.achievement_id
        WHERE ua.user_id = ?
        ORDER BY a.id
    """, (user_id,))
    res = c.fetchall()
    conn.close()
    return res

def award_achievement(user_id, achievement_name):
    """
    Pokusí se přiřadit uživateli úspěch podle jména.
    Vrací True, pokud byl úspěch přidán, jinak False (už ho má, nebo neexistuje).
    """
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT id FROM achievements WHERE name = ?", (achievement_name,))
    ach = c.fetchone()
    if not ach:
        conn.close()
        return False
    try:
        c.execute(
            "INSERT INTO user_achievements (user_id, achievement_id) VALUES (?, ?)",
            (user_id, ach['id'])
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False  # už má
    finally:
        conn.close()


def get_scores_by_difficulty(difficulty=None):
    """
    Vrátí skóre (i s uživatelským jménem) filtrované podle obtížnosti.
    Pokud difficulty není zadána (None), vrátí vše.
    """
    conn = get_db()
    c = conn.cursor()
    
    if difficulty:
        c.execute("""
            SELECT scores.id, users.username, scores.score, scores.difficulty
            FROM scores
            JOIN users ON scores.user_id = users.id
            WHERE scores.difficulty = ?
            ORDER BY scores.score DESC
        """, (difficulty,))
    else:
        c.execute("""
            SELECT scores.id, users.username, scores.score, scores.difficulty
            FROM scores
            JOIN users ON scores.user_id = users.id
            ORDER BY scores.score DESC
        """)
    
    scores = c.fetchall()
    conn.close()
    return scores

def get_user_stats():
    """
    Vrátí pro každého uživatele: username, počet her, průměrné skóre, max skóre.
    Používá COALESCE, aby uživatelé bez skóre měli 0 místo NULL.
    """
    conn = get_db()
    c = conn.cursor()
    c.execute("""
        SELECT 
            users.username,
            COUNT(scores.id) AS games_played,
            COALESCE(AVG(scores.score), 0) AS avg_score,
            COALESCE(MAX(scores.score), 0) AS max_score
        FROM users
        LEFT JOIN scores ON users.id = scores.user_id
        GROUP BY users.id
        ORDER BY avg_score DESC
    """)
    stats = c.fetchall()
    conn.close()
    return stats

def get_all_users():
    """Vrátí seznam všech uživatelů (pro admina)."""
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT id, username, role FROM users ORDER BY id")
    users = c.fetchall()
    conn.close()
    return users

def delete_user(user_id):
    """Smaže uživatele podle ID (pouze pro admina). CASCADE smaže i skóre a achievements."""
    conn = get_db()
    c = conn.cursor()
    c.execute("DELETE FROM users WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()

def change_password(user_id, new_password):
    """Změní heslo uživatele."""
    conn = get_db()
    c = conn.cursor()
    c.execute("UPDATE users SET password = ? WHERE id = ?", (new_password, user_id))
    conn.commit()
    conn.close()