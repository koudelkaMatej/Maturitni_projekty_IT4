import os
from flask import Flask, render_template
from settings import CESTA_PRO_DATA

app = Flask(__name__)

def nacti_casy(obtiznost):
    vysledky = []
    if not os.path.exists(CESTA_PRO_DATA):
        return vysledky

    hledana_sekce = obtiznost.upper() + ":"
    cteme_sekci = False

    with open(CESTA_PRO_DATA, "r", encoding="utf-8") as f:
        for radek in f:
            radek = radek.strip()
            if not radek: continue
            
            if radek == hledana_sekce:
                cteme_sekci = True
                continue
            
            if cteme_sekci and radek.endswith(":"):
                cteme_sekci = False
                break # Už jsme prošli celou naši sekci
            
            if cteme_sekci and ", " in radek:
                casti = radek.split(", ")
                if len(casti) == 2:
                    vysledky.append({"jmeno": casti[0], "cas": casti[1]})
    
    # --- TADY JE TO KOUZLO ---
    # Seřadíme seznam podle hodnoty 'cas' (od nejmenšího po největší)
    vysledky.sort(key=lambda x: x['cas'])
    
    return vysledky

# --- ROUTY (Zůstávají stejné) ---

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/tab')
def tabulka():
    lehka = nacti_casy("LEHKÁ")
    stredni = nacti_casy("STŘEDNÍ")
    tezka = nacti_casy("TĚŽKÁ")
    return render_template('tab.html', lehka=lehka, stredni=stredni, tezka=tezka)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/login')
def login():
    return render_template('login.html')

if __name__ == '__main__':
    app.run(debug=True, port=5000)