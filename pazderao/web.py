import os
from flask import Flask, render_template
from settings import CESTA_PRO_DATA # import cesty k souboru s časy

app = Flask(__name__) # inicializace Flask aplikace

def nacti_casy(obtiznost):
    vysledky = []
    if not os.path.exists(CESTA_PRO_DATA): # kontrola existence souboru
        return vysledky

    hledana_sekce = obtiznost.upper() + ":"
    cteme_sekci = False

    with open(CESTA_PRO_DATA, "r", encoding="utf-8") as f:
        for radek in f:
            radek = radek.strip()
            if not radek: continue
            
            if radek == hledana_sekce: # nalezení začátku obtížnosti
                cteme_sekci = True
                continue
            
            if cteme_sekci and radek.endswith(":"): # ukončení sekce při dalším dvojtečce
                cteme_sekci = False
                break
            
            if cteme_sekci and ", " in radek: # rozdělení jména a času
                casti = radek.split(", ")
                if len(casti) == 2:
                    vysledky.append({"jmeno": casti[0], "cas": casti[1]})
    
    vysledky.sort(key=lambda x: x['cas']) # seřazení od nejrychlejšího času
    return vysledky

@app.route('/')
def index():
    return render_template('index.html') # vykreslení úvodní stránky

@app.route('/tab')
def tabulka():
    lehka = nacti_casy("LEHKÁ") # načtení dat pro jednotlivé tabulky
    stredni = nacti_casy("STŘEDNÍ")
    tezka = nacti_casy("TĚŽKÁ")
    return render_template('tab.html', lehka=lehka, stredni=stredni, tezka=tezka)

@app.route('/about')
def about():
    return render_template('about.html') # vykreslení stránky o projektu

@app.route('/login')
def login():
    return render_template('login.html') # vykreslení přihlašovacího formuláře

if __name__ == '__main__':
    app.run(debug=True, port=5000) # spuštění lokálního serveru