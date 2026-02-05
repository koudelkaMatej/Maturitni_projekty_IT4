import mysql.connector

db = mysql.connector.connect(
    host="dbs.spskladno.cz",
    user="student31",
    password="spsnet",
    database="vyuka31"
)

cursor = db.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE,
    highscore INT DEFAULT 0
)
""")

db.commit()

cursor.close()
db.close()

print("Databáze připravena ✅")

