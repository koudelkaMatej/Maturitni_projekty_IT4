# database.py – Komunikace se vzdálenou databází a ověřování uživatelů
# Zajišťuje připojení přes mysql.connector, ukládání hashe hesel (bezpečnost) a aktualizaci skóre.
import mysql.connector
import hashlib

class Database:

    def __init__(self):
        """
        Inicializuje databázové připojení a ihned zajistí potřebnou strukturu tabulky.
        Pokud spojení (např. kvůli absenci internetu) selže, hra pokračuje v offline režimu.
        """
        self.connection = None
        try:
            self.connection = mysql.connector.connect(
                host="dbs.spskladno.cz",
                user="student31",
                password="spsnet",
                database="vyuka31"
            )
            self._ensure_password_column()
            print("DB OK")
        except:
            print("DB ERROR")

    def _ensure_password_column(self):
        """
        Zkontroluje a případně doplní sloupec 'password_hash' do stávající tabulky uživatelů.
        Slouží jako bezpečnostní pojistka pro starší databázová schémata bez podpory hesel.
        """
        if not self.connection: return
        cursor = self.connection.cursor()
        try:
            cursor.execute(
                "ALTER TABLE users ADD COLUMN password_hash VARCHAR(64) DEFAULT '' NOT NULL"
            )
            self.connection.commit()
        except:
            pass  # Sloupec už existuje – v pořádku
        finally:
            cursor.close()

    def _hash(self, password):
        """
        Jednosměrně zahashuje předané heslo algoritmem SHA-256. 
        V databázi nesmí být nikdy uloženo heslo v čisté textové podobě (plain text).
        """
        return hashlib.sha256(password.encode()).hexdigest()

    def close(self):
        if self.connection:
            self.connection.close()

    def register_user(self, username, password):
        """
        Zaregistruje nového uživatele vložením záznamu do databáze. 
        Místo surového hesla použije metodou _hash vypočítaný hash a zkusí vložit data.
        Vrací True v případě úspěchu. Vrací False v případě selhání (např. jméno už existuje).
        """
        if not self.connection:
            return False
        cursor = self.connection.cursor()
        try:
            cursor.execute(
                "INSERT INTO users (username, password_hash) VALUES (%s, %s)",
                (username, self._hash(password))
            )
            self.connection.commit()
            return True
        except:
            return False  # Duplicitní username (UNIQUE constraint)
        finally:
            cursor.close()

    def login_user(self, username, password):
        """
        Zajišťuje přihlášení uživatele dotažením hashe a porovnáním s hashem zadaného hesla.
        Pokud řádek existuje a hash hesla sedí, metoda vrátí slovník s herními daty uživatele.
        Pokud ne, vrací None.
        """
        if not self.connection:
            return None
        cursor = self.connection.cursor(dictionary=True)
        try:
            cursor.execute(
                "SELECT id, username, highscore, password_hash FROM users WHERE username = %s",
                (username,)
            )
            row = cursor.fetchone()
            if row and row["password_hash"] == self._hash(password):
                return {
                    "id": row["id"],
                    "username": row["username"],
                    "highscore": row["highscore"] or 0
                }
            return None
        except:
            return None
        finally:
            cursor.close()

    def get_user(self, username):
        """
        Získá data hráče pouze na základě jeho jména bez ověření hesel.
        Používá se pro vnitřní logiku hry či záchranné operace, případně generuje 
        prázdná data, pokud se připojení zcela nezdaří.
        """
        if not self.connection:
            return {"username": username, "id": None, "highscore": 0}
        cursor = self.connection.cursor(dictionary=True)
        try:
            cursor.execute("SELECT id, username, highscore FROM users WHERE username = %s", (username,))
            res = cursor.fetchone()
            if res:
                return {"id": res["id"], "username": res["username"], "highscore": res["highscore"] or 0}
        except:
            pass
        finally:
            cursor.close()
        return {"username": username, "id": None, "highscore": 0}

    def save_score(self, user_id, new_score):
        """
        Uloží nové skóre do tabulky uživatele. 
        Pro minimalizaci výpočetní logiky v Pythonu je přímo využit databázový 
        funkční operátor GREATEST, který rovnou uloží to matematicky nejvyšší skóre.
        """
        if not self.connection or not user_id: return
        cursor = self.connection.cursor()
        try:
            cursor.execute(
                "UPDATE users SET highscore = GREATEST(highscore, %s) WHERE id = %s",
                (new_score, user_id)
            )
            self.connection.commit()
        except:
            pass
        finally:
            cursor.close()