from Example.db import get_db

def vytvorit_databazi():
    db = get_db()
    cursor = db.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INT AUTO_INCREMENT PRIMARY KEY,
        username VARCHAR(50) NOT NULL UNIQUE,
        password VARCHAR(255) NOT NULL,
        coins INT NOT NULL DEFAULT 0,
        created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS matches (
        id INT AUTO_INCREMENT PRIMARY KEY,
        user_id INT NOT NULL,
        result ENUM('WIN','LOSE') NOT NULL,
        waves_reached INT NOT NULL,
        kills INT NOT NULL,
        reward_coins INT NOT NULL,
        played_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS towers_unlocked (
        id INT AUTO_INCREMENT PRIMARY KEY,
        user_id INT NOT NULL,
        tower_name VARCHAR(50) NOT NULL,
        unlocked_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS purchases (
        id INT AUTO_INCREMENT PRIMARY KEY,
        user_id INT NOT NULL,
        item_name VARCHAR(50) NOT NULL,
        price INT NOT NULL,
        purchased_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )
    """)

    db.commit()
    cursor.close()
    db.close()
    print("✅ Databáze připravena")


def smazat_databazi():
    db = get_db()
    cursor = db.cursor()

    cursor.execute("DROP TABLE IF EXISTS purchases")
    cursor.execute("DROP TABLE IF EXISTS towers_unlocked")
    cursor.execute("DROP TABLE IF EXISTS matches")
    cursor.execute("DROP TABLE IF EXISTS users")

    db.commit()
    cursor.close()
    db.close()
    print("🗑️ Databáze kompletně smazána")


x = input("Chcete vytvořit (v) nebo smazat (s) databázi? ").strip().lower()

if x == "v":
    vytvorit_databazi()
elif x == "s":
    smazat_databazi()
else:
    print("Neplatná volba.")
