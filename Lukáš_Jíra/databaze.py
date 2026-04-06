import hashlib
import os
import sqlite3
from datetime import datetime

ADRESAR = os.path.dirname(os.path.abspath(__file__))
SOUBOR = os.path.join(ADRESAR, "skore.db")


def _hash_hesla(heslo):
    return hashlib.sha256(heslo.encode("utf-8")).hexdigest()


def vytvorit_tabulku():
    conn = sqlite3.connect(SOUBOR)
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS uzivatele (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            jmeno TEXT UNIQUE NOT NULL,
            heslo_hash TEXT NOT NULL
        )
        """
    )

    info = cursor.execute("PRAGMA table_info(uzivatele)").fetchall()
    cols = {row[1] for row in info}
    if "heslo_hash" not in cols:
        cursor.execute("ALTER TABLE uzivatele ADD COLUMN heslo_hash TEXT")
        if "heslo" in cols:
            rows = cursor.execute("SELECT id, heslo FROM uzivatele").fetchall()
            for user_id, plain in rows:
                if plain is None:
                    continue
                cursor.execute(
                    "UPDATE uzivatele SET heslo_hash = ? WHERE id = ?",
                    (_hash_hesla(plain), user_id),
                )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS vysledky (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            jmeno TEXT NOT NULL,
            body INTEGER NOT NULL,
            datum TEXT NOT NULL
        )
        """
    )

    conn.commit()
    conn.close()


def registrace(jmeno, heslo):
    if not jmeno or not heslo:
        return False

    conn = sqlite3.connect(SOUBOR)
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO uzivatele (jmeno, heslo_hash) VALUES (?, ?)",
            (jmeno, _hash_hesla(heslo)),
        )
        conn.commit()
        uspech = True
    except sqlite3.IntegrityError:
        uspech = False
    finally:
        conn.close()
    return uspech


def prihlaseni(jmeno, heslo):
    if not jmeno or not heslo:
        return False

    conn = sqlite3.connect(SOUBOR)
    cursor = conn.cursor()
    cursor.execute("SELECT id, heslo_hash FROM uzivatele WHERE jmeno = ?", (jmeno,))
    row = cursor.fetchone()

    if row is None:
        conn.close()
        return False

    user_id, stored_hash = row
    incoming_hash = _hash_hesla(heslo)

    if stored_hash is None:
        old_plain = cursor.execute("SELECT heslo FROM uzivatele WHERE id = ?", (user_id,)).fetchone()
        if old_plain and old_plain[0] == heslo:
            cursor.execute("UPDATE uzivatele SET heslo_hash = ? WHERE id = ?", (incoming_hash, user_id))
            conn.commit()
            conn.close()
            return True
        conn.close()
        return False

    ok = stored_hash == incoming_hash
    conn.close()
    return ok


def pridat_vysledek(jmeno, body):
    if not jmeno:
        return False

    conn = sqlite3.connect(SOUBOR)
    cursor = conn.cursor()
    exists = cursor.execute("SELECT 1 FROM uzivatele WHERE jmeno = ?", (jmeno,)).fetchone()
    if not exists:
        conn.close()
        return False

    cas = datetime.now().strftime("%d.%m.%Y %H:%M")
    cursor.execute(
        "INSERT INTO vysledky (jmeno, body, datum) VALUES (?, ?, ?)",
        (jmeno, int(body), cas),
    )
    conn.commit()
    conn.close()
    return True


def ziskej_data():
    conn = sqlite3.connect(SOUBOR)
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT v.jmeno, v.body, v.datum
        FROM vysledky v
        JOIN (
            SELECT jmeno, MAX(body) AS max_body
            FROM vysledky
            GROUP BY jmeno
        ) m
            ON v.jmeno = m.jmeno
           AND v.body = m.max_body
        WHERE v.id = (
            SELECT MAX(v2.id)
            FROM vysledky v2
            WHERE v2.jmeno = v.jmeno
              AND v2.body = v.body
        )
        ORDER BY v.body DESC, v.jmeno COLLATE NOCASE ASC
        """
    )
    data = cursor.fetchall()
    conn.close()
    return data


def ziskej_uzivatele():
    conn = sqlite3.connect(SOUBOR)
    cursor = conn.cursor()
    cursor.execute("SELECT jmeno FROM uzivatele ORDER BY jmeno COLLATE NOCASE ASC")
    data = [row[0] for row in cursor.fetchall()]
    conn.close()
    return data


def smazat_ucet(jmeno):
    if not jmeno:
        return False

    conn = sqlite3.connect(SOUBOR)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM vysledky WHERE jmeno = ?", (jmeno,))
    cursor.execute("DELETE FROM uzivatele WHERE jmeno = ?", (jmeno,))
    smazano = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return smazano


def vymaz_vysledky():
    conn = sqlite3.connect(SOUBOR)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM vysledky")
    conn.commit()
    conn.close()
