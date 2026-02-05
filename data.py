import mysql.connector

mydb = mysql.connector.connect(
    host="dbs.spskladno.cz",
    user="student31",
    password="spsnet",
    database="vyuka31"
)

cursor = mydb.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS scores (
    id INT AUTO_INCREMENT PRIMARY KEY,
    player_name VARCHAR(50),
    score INT,
    level INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

mydb.commit()
cursor.close()
mydb.close()
