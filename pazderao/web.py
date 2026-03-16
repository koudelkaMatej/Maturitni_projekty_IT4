from flask import Flask, render_template, request
import mysql.connector
import webbrowser
import os
from settings import *
app = Flask(__name__)


def get_data_from_file(obtiznost):
    """Načte data ze souboru a rozparsuje je podle čárky"""
    vysledky = []
    sekce = f"{obtiznost.upper()}:"
    uvnitr_sekce = False

    if not os.path.exists(CESTA_PRO_DATA):
        return []

    try:
        with open(CESTA_PRO_DATA, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line: continue
                
                if line == sekce:
                    uvnitr_sekce = True
                    continue
                
                # Pokud narazíme na jinou sekci, tuhle ukončíme
                if uvnitr_sekce and line.endswith(":"):
                    uvnitr_sekce = False
                    break
                
                # Zpracování řádku s čárkou
                if uvnitr_sekce and ", " in line:
                    jmeno, cas = line.split(", ")
                    vysledky.append({"jmeno": jmeno, "cas": cas})
    except Exception as e:
        print(f"Chyba při čtení souboru: {e}")
    
    return vysledky

# --- ROUTY (STRÁNKY) ---

@app.route('/', methods=['GET', 'POST'])
def index():
    # Získáme obtížnost buď z formuláře (POST) nebo z URL (GET)
    obtiznost = request.form.get('obtiznost') or request.args.get('obtiznost') or 'LEHKÁ'
    leaderboard = get_data_from_file(obtiznost)
    return render_template('index.html', leaderboard=leaderboard, obtiznost=obtiznost)

@app.route('/about')
def about():
    return render_template('about.html')

# --- SPUŠTĚNÍ ---
if __name__ == '__main__':
    # Spustí web na portu 5000 s automatickým restartem při změně
    app.run(debug=True, port=5000)