from flask import Flask, render_template, request
import mysql.connector
from settings import * 
import os

app = Flask(__name__)

# Funkce pro vytvoření čerstvého spojení (prevence timeoutu)
def get_db_connection():
    return mysql.connector.connect(
        host = host,
        user = username,
        password = password,
        database = database
    )


def get_data_from_file(obtiznost):
    vysledky = []
    sekce = f"{obtiznost.upper()}:"
    uvnitr_sekce = False

    if not os.path.exists(CESTA_PRO_DATA):
        return []

    with open(CESTA_PRO_DATA, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line == sekce:
                uvnitr_sekce = True
                continue
            if uvnitr_sekce and (line.endswith(":") or not line):
                uvnitr_sekce = False
            
            if uvnitr_sekce and " - " in line:
                jmeno, cas = line.split(" - ")
                vysledky.append({"jmeno": jmeno, "cas": cas})
    
    return vysledky


def get_leaderboard(obtiznost):
    # Seznam povolených sloupců (prevence SQL injection)
    povolené_sloupce = ["Easy", "Medium", "Hard"]
    if obtiznost not in povolené_sloupce:
        obtiznost = "Easy"

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # U timeru řadíme ASC (vzestupně), protože menší čas je LEPŠÍ výsledek
    query = f"SELECT username, {obtiznost} FROM Score ORDER BY {obtiznost} ASC"
    
    cursor.execute(query)
    rows = cursor.fetchall()
    
    cursor.close()
    conn.close()
    return rows

@app.route('/', methods=['GET', 'POST'])
def index():
    # Pokud uživatel klikne na tlačítko obtížnosti ve formuláři
    obtiznost = request.form.get('obtiznost', 'Easy')
    leaderboard = get_leaderboard(obtiznost)
    return render_template('index.html', obtiznost=obtiznost, leaderboard=leaderboard)

@app.route('/')
def index():
    obtiznost = request.args.get('obtiznost', 'LEHKÁ')
    leaderboard = get_data_from_file(obtiznost)
    return render_template('tab.html', leaderboard=leaderboard, obtiznost=obtiznost)

if __name__ == '__main__':
    app.run(debug=True)

@app.route('/info')
def info():
    # Tady bude tvůj ER-diagram a popis projektu
    return render_template('info.html')

@app.route('/login')
def login():
    # Zatím jen statická stránka pro login
    return render_template('login.html')

if __name__ == '__main__':
    # Spuštění Flask serveru
    app.run(debug=True)