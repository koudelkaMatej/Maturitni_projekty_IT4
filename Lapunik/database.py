# database.py
import mysql.connector
from datetime import datetime
import hashlib

class Database:
    def __init__(self):
        self.connection = None
        self.connect()
        self.create_users_table()
        
    def connect(self):
        """Připojí se k databázi vyuka31"""
        try:
            self.connection = mysql.connector.connect(
                host="dbs.spskladno.cz",
                user="student31",
                password="spsnet",
                database="vyuka31"
            )
            print("✅ Připojeno k databázi vyuka31")
            return True
        except mysql.connector.Error as err:
            print(f"❌ Chyba připojení k databázi: {err}")
            return False
    
    def create_users_table(self):
        """Vytvoří novou tabulku users pro hru"""
        if not self.connection:
            return False
            
        cursor = self.connection.cursor()
        
        try:
            # Nejprve zkontrolujeme, zda tabulka už existuje
            cursor.execute("SHOW TABLES LIKE 'users'")
            if cursor.fetchone():
                print("✅ Tabulka 'users' již existuje")
                cursor.close()
                return True
            
            # Vytvoříme novou tabulku users
            create_table_sql = """
            CREATE TABLE users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                email VARCHAR(100),
                high_score INT DEFAULT 0,
                games_played INT DEFAULT 0,
                total_score BIGINT DEFAULT 0,
                enemies_killed INT DEFAULT 0,
                highest_level INT DEFAULT 0,
                last_played DATETIME,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_username (username),
                INDEX idx_high_score (high_score DESC)
            )
            """
            
            cursor.execute(create_table_sql)
            self.connection.commit()
            print("✅ Tabulka 'users' vytvořena")
            
            # Vytvoříme také tabulku pro jednotlivé herní relace
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS game_sessions (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT,
                score INT NOT NULL,
                level_reached INT NOT NULL,
                enemies_killed INT NOT NULL,
                play_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                game_duration INT,  -- v sekundách
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                INDEX idx_user_date (user_id, play_date DESC)
            )
            """)
            
            self.connection.commit()
            print("✅ Tabulka 'game_sessions' vytvořena")
            return True
            
        except mysql.connector.Error as err:
            print(f"❌ Chyba při vytváření tabulek: {err}")
            return False
        finally:
            cursor.close()
    
    def register_user(self, username, password, email=None):
        """Zaregistruje nového uživatele"""
        if not self.connection:
            return False
            
        cursor = self.connection.cursor()
        
        try:
            # Zkontrolujeme, jestli uživatel už existuje
            cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
            if cursor.fetchone():
                print(f"❌ Uživatel '{username}' již existuje")
                return False
            
            # Hashování hesla
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            
            # Vložíme nového uživatele
            sql = """
                INSERT INTO users (username, password_hash, email)
                VALUES (%s, %s, %s)
            """
            values = (username, password_hash, email)
            cursor.execute(sql, values)
            self.connection.commit()
            
            print(f"✅ Uživatel '{username}' zaregistrován")
            return True
            
        except mysql.connector.Error as err:
            print(f"❌ Chyba při registraci uživatele: {err}")
            return False
        finally:
            cursor.close()
    
    def authenticate_user(self, username, password):
        """Ověří přihlašovací údaje"""
        if not self.connection:
            return False
            
        cursor = self.connection.cursor(dictionary=True)
        
        try:
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            
            sql = """
                SELECT id, username, email, high_score, games_played, highest_level
                FROM users 
                WHERE username = %s AND password_hash = %s
            """
            cursor.execute(sql, (username, password_hash))
            result = cursor.fetchone()
            
            if result:
                print(f"✅ Uživatel '{username}' přihlášen")
                return result
            else:
                print(f"❌ Neplatné přihlašovací údaje pro '{username}'")
                return False
                
        except mysql.connector.Error as err:
            print(f"❌ Chyba při ověřování uživatele: {err}")
            return False
        finally:
            cursor.close()
    
    def save_game_session(self, user_id, score, level_reached, enemies_killed, game_duration=0):
        """Uloží záznam o herní relaci"""
        if not self.connection:
            return False
            
        cursor = self.connection.cursor()
        
        try:
            sql = """
                INSERT INTO game_sessions (user_id, score, level_reached, enemies_killed, game_duration)
                VALUES (%s, %s, %s, %s, %s)
            """
            values = (user_id, score, level_reached, enemies_killed, game_duration)
            cursor.execute(sql, values)
            self.connection.commit()
            
            # Aktualizujeme statistiky v tabulce users
            update_sql = """
                UPDATE users 
                SET games_played = games_played + 1,
                    total_score = total_score + %s,
                    enemies_killed = enemies_killed + %s,
                    highest_level = GREATEST(highest_level, %s),
                    last_played = NOW()
                WHERE id = %s
            """
            cursor.execute(update_sql, (score, enemies_killed, level_reached, user_id))
            
            # Aktualizujeme high score, pokud je vyšší
            cursor.execute("SELECT high_score FROM users WHERE id = %s", (user_id,))
            current_high = cursor.fetchone()[0]
            
            if score > current_high:
                cursor.execute("UPDATE users SET high_score = %s WHERE id = %s", (score, user_id))
                print(f"🎉 Nový high score: {score}!")
            
            self.connection.commit()
            print("✅ Herní relace uložena")
            return True
            
        except mysql.connector.Error as err:
            print(f"❌ Chyba při ukládání herní relace: {err}")
            return False
        finally:
            cursor.close()
    
    def get_top_scores(self, limit=10):
        """Získá TOP X nejlepších skóre"""
        if not self.connection:
            return []
            
        cursor = self.connection.cursor(dictionary=True)
        
        try:
            sql = """
                SELECT username as player_name, 
                       high_score as score, 
                       highest_level as level_reached,
                       last_played as play_date,
                       games_played
                FROM users 
                WHERE high_score > 0
                ORDER BY high_score DESC
                LIMIT %s
            """
            cursor.execute(sql, (limit,))
            results = cursor.fetchall()
            
            # Formátujeme datum
            for result in results:
                if result['play_date']:
                    result['play_date'] = result['play_date'].strftime("%d.%m.%Y %H:%M")
            
            return results
            
        except mysql.connector.Error as err:
            print(f"❌ Chyba při načítání high scores: {err}")
            return []
        finally:
            cursor.close()
    
    def get_user_stats(self, user_id):
        """Získá statistiky konkrétního uživatele"""
        if not self.connection:
            return None
            
        cursor = self.connection.cursor(dictionary=True)
        
        try:
            sql = """
                SELECT u.username, u.high_score, u.games_played, 
                       u.total_score, u.enemies_killed, u.highest_level,
                       u.last_played, u.created_at,
                       COUNT(gs.id) as total_sessions,
                       AVG(gs.score) as avg_score
                FROM users u
                LEFT JOIN game_sessions gs ON u.id = gs.user_id
                WHERE u.id = %s
                GROUP BY u.id
            """
            cursor.execute(sql, (user_id,))
            result = cursor.fetchone()
            
            return result if result else None
            
        except mysql.connector.Error as err:
            print(f"❌ Chyba při načítání statistik: {err}")
            return None
        finally:
            cursor.close()
    
    def get_user_game_history(self, user_id, limit=10):
        """Získá historii her uživatele"""
        if not self.connection:
            return []
            
        cursor = self.connection.cursor(dictionary=True)
        
        try:
            sql = """
                SELECT score, level_reached, enemies_killed, play_date, game_duration
                FROM game_sessions
                WHERE user_id = %s
                ORDER BY play_date DESC
                LIMIT %s
            """
            cursor.execute(sql, (user_id, limit))
            results = cursor.fetchall()
            
            # Formátujeme datum
            for result in results:
                if result['play_date']:
                    result['play_date'] = result['play_date'].strftime("%d.%m.%Y %H:%M")
            
            return results
            
        except mysql.connector.Error as err:
            print(f"❌ Chyba při načítání historie her: {err}")
            return []
        finally:
            cursor.close()
    
    def search_users(self, search_term, limit=20):
        """Vyhledá uživatele podle jména"""
        if not self.connection:
            return []
            
        cursor = self.connection.cursor(dictionary=True)
        
        try:
            sql = """
                SELECT username, high_score, games_played, highest_level
                FROM users
                WHERE username LIKE %s
                ORDER BY high_score DESC
                LIMIT %s
            """
            cursor.execute(sql, (f"%{search_term}%", limit))
            return cursor.fetchall()
            
        except mysql.connector.Error as err:
            print(f"❌ Chyba při vyhledávání uživatelů: {err}")
            return []
        finally:
            cursor.close()
    
    def delete_user(self, user_id):
        """Smaže uživatele (pouze pro administrátory/testování)"""
        if not self.connection:
            return False
            
        cursor = self.connection.cursor()
        
        try:
            sql = "DELETE FROM users WHERE id = %s"
            cursor.execute(sql, (user_id,))
            self.connection.commit()
            
            print(f"✅ Uživatel s ID {user_id} smazán")
            return cursor.rowcount > 0
            
        except mysql.connector.Error as err:
            print(f"❌ Chyba při mazání uživatele: {err}")
            return False
        finally:
            cursor.close()
    
    def close(self):
        """Uzavře spojení s databází"""
        if self.connection:
            self.connection.close()
            print("✅ Spojení s databází uzavřeno")