print("SCORE MANAGER LOADED")

import mysql.connector


class ScoreManager:

    def __init__(self, username):

        self.username = username

        # Připojení k DB
        self.db = mysql.connector.connect(
            host="dbs.spskladno.cz",
            user="student31",
            password="spsnet",
            database="vyuka31"
        )

        self.cursor = self.db.cursor()

        # Vytvoření tabulky (pokud není)
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(50) UNIQUE,
            highscore INT DEFAULT 0
        )
        """)

        self.db.commit()

        # Vytvoření uživatele
        self.cursor.execute(
            "INSERT IGNORE INTO users (username) VALUES (%s)",
            (username,)
        )

        self.db.commit()

        # Načtení skóre
        self.cursor.execute(
            "SELECT highscore FROM users WHERE username = %s",
            (username,)
        )

        result = self.cursor.fetchone()

        if result:
            self.high_score = result[0]
        else:
            self.high_score = 0

        self.current_score = 0

    # --------------------------------

    def add_score(self, points):

        self.current_score += points

        if self.current_score > self.high_score:

            self.high_score = self.current_score

            self.cursor.execute(
                """
                UPDATE users
                SET highscore = %s
                WHERE username = %s
                """,
                (self.high_score, self.username)
            )

            self.db.commit()

    # --------------------------------

    def enemy_killed(self, enemy_type):

        if enemy_type == "basic":
            self.add_score(10)

        elif enemy_type == "strong":
            self.add_score(20)

        elif enemy_type == "mega_goblin":
            self.add_score(100)

    # --------------------------------

    def level_completed(self):

        self.add_score(500)

    # --------------------------------

    def reset(self):

        self.current_score = 0

    # --------------------------------

    def get_text(self):

        return f"Score: {self.current_score} | High: {self.high_score}"
