# prefer local module import; if running from repo root via `python -m Example.databaze` this also works
try:
    from Example.db import get_db
except ModuleNotFoundError:
    from db import get_db

def vytvorit_databazi():
    db = get_db()
    cursor = db.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(50) NOT NULL UNIQUE,
            password VARCHAR(255) NOT NULL,
            coins INT NOT NULL DEFAULT 0,
            created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS matches (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            result ENUM('WIN','LOSE') NOT NULL,
            waves_reached INT NOT NULL,
            kills INT NOT NULL,
            reward_coins INT NOT NULL,
            difficulty ENUM('easy','normal','hard') NOT NULL DEFAULT 'normal',
            played_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id),
            CHECK (waves_reached >= 0),
            CHECK (kills >= 0),
            CHECK (reward_coins >= 0)
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS towers_unlocked (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            tower_name VARCHAR(50) NOT NULL,
            unlocked_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS purchases (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            item_name VARCHAR(50) NOT NULL,
            price INT NOT NULL,
            purchased_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id),
            CHECK (price >= 0)
        )
        """
    )

    try:
        cursor.execute(
            "ALTER TABLE matches ADD COLUMN difficulty ENUM('easy','normal','hard') NOT NULL DEFAULT 'normal'"
        )
    except Exception:
        pass

    cursor.execute(
        """
        INSERT IGNORE INTO users (username, password)
        VALUES (%s, %s)
        """,
        ("sa", "sa"),
    )

    db.commit()
    cursor.close()
    db.close()

    print("Databaze pripravena + uzivatel 'sa' vytvoren")


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

    print("Databaze kompletne smazana")


def pridat_uzivatele():
    username = input("Zadejte username: ").strip()
    password = input("Zadejte heslo: ").strip()
    coins_text = input("Zadejte pocatecni coiny (Enter = 0): ").strip()

    if username == "" or password == "":
        print("Username i heslo musi byt vyplnene.")
        return

    try:
        coins = int(coins_text) if coins_text else 0
    except ValueError:
        print("Coiny musi byt cele cislo.")
        return

    if coins < 0:
        print("Coiny musi byt 0 nebo vice.")
        return

    db = get_db()
    cursor = db.cursor()

    try:
        cursor.execute(
            "INSERT INTO users (username, password, coins) VALUES (%s, %s, %s)",
            (username, password, coins),
        )
        db.commit()
        print(f"Uzivatel '{username}' byl vytvoren.")
    except Exception as exc:
        db.rollback()
        print(f"Nepodarilo se pridat uzivatele: {exc}")
    finally:
        cursor.close()
        db.close()


akce = input("Chcete vytvorit (v), smazat (s) databazi, nebo pridat uzivatele (u)? ").strip().lower()

if akce == "v":
    vytvorit_databazi()
elif akce == "s":
    smazat_databazi()
elif akce == "u":
    pridat_uzivatele()
else:
    print("Neplatna volba.")
