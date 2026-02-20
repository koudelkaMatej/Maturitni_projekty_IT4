from flask import Flask, request
import Maturitni_projekty_IT4.Lukáš_Jíra.databaze as databaze


app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def hlavni_stranka():
    zprava_pro_uzivatele = ""
    zobrazit_formular = True  # Na začátku chceme formulář vidět
    prihlaseny_jmeno = ""


    # 1. KONTROLA FORMULÁŘE (Když uživatel klikne na tlačítko)
    if request.method == "POST":
        jmeno = request.form.get("jmeno")
        heslo = request.form.get("heslo")
       
        if databaze.registrace(jmeno, heslo):
            zprava_pro_uzivatele = "✅ Registrace úspěšná!"
            zobrazit_formular = False # Schováme formulář
            prihlaseny_jmeno = jmeno  # Uložíme si jméno pro zobrazení v rohu
        else:
            zprava_pro_uzivatele = "❌ Toto jméno už je zabrané, zkus jiné."


    # 2. NAČTENÍ VÝSLEDKŮ
    data = databaze.ziskej_data()
    radky_tabulky = ""
    poradi = 1
    for hrac in data:
        radky_tabulky += f"""
            <tr>
                <td>{poradi}.</td>
                <td>{hrac[0]}</td>
                <td>{hrac[1]}</td>
                <td>{hrac[2]}</td>
            </tr>
        """
        poradi += 1


    # 3. PŘÍPRAVA HTML BLOKŮ (Tady se rozhoduje, co hráč uvidí)
    if zobrazit_formular:
        # Hráč není zaregistrovaný -> Ukážeme formulář
        sekce_registrace = f"""
            <p style="color: #d11a2a; font-weight: bold; font-size: 18px;">{zprava_pro_uzivatele}</p>
            <form method="POST">
                <input type="text" name="jmeno" placeholder="Vymysli si jméno" required><br><br>
                <input type="password" name="heslo" placeholder="Tvé tajné heslo" required><br><br>
                <input type="submit" value="ZAREGISTROVAT SE">
            </form>
        """
        profil_v_rohu = "" # V rohu nic není
    else:
        # Hráč se právě zaregistroval -> Schováme formulář
        sekce_registrace = f"""
            <h2 style="color: #50c878;">{zprava_pro_uzivatele}</h2>
            <p>Účet byl vytvořen. Můžeš se vrátit do okna hry a kliknout na <b>PŘIHLÁSIT SE</b>.</p>
        """
        profil_v_rohu = f"""
            <div style="position: absolute; top: 20px; right: 20px; background-color: #543847; padding: 10px 20px; border-radius: 10px; font-weight: bold; border: 2px solid white;">
                👤 Účet: {prihlaseny_jmeno}
            </div>
        """


    # 4. HLAVNÍ HTML
    html_kod = f"""
    <!DOCTYPE html>
    <html lang="cs">
    <head>
        <meta charset="UTF-8">
        <title>Flappy Bird - Web</title>
        <style>
            body {{ font-family: Arial; background-color: #70c5ce; text-align: center; color: white; margin: 0; padding: 20px; }}
            .okno {{ background-color: #ded895; width: 600px; margin: 30px auto; padding: 20px; border: 4px solid #543847; border-radius: 10px; position: relative; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
            td, th {{ padding: 10px; border-bottom: 2px solid #543847; color: #543847; }}
            h1 {{ color: #e6601e; text-shadow: 2px 2px 0px black; }}
            input[type=text], input[type=password] {{ padding: 10px; font-size: 16px; border-radius: 5px; border: 2px solid #543847; }}
            input[type=submit] {{ padding: 10px 20px; font-size: 16px; background-color: #50c878; color: white; border: none; border-radius: 5px; cursor: pointer; font-weight: bold; }}
            input[type=submit]:hover {{ background-color: #64ff96; }}
        </style>
    </head>
    <body>
       
        {profil_v_rohu} <div class="okno">
            <h1>📝 Vytvoření účtu</h1>
            {sekce_registrace} </div>


        <div class="okno">
            <h1>🏆 TOP VÝSLEDKY 🏆</h1>
            <table>
                <tr><th>Pořadí</th><th>Jméno</th><th>Skóre</th><th>Datum</th></tr>
                {radky_tabulky}
            </table>
        </div>


    </body>
    </html>
    """
    return html_kod


if __name__ == "__main__":
    print("🚀 Zapínám webový server... Nech toto okno otevřené!")
    print("Otevři si v prohlížeči adresu: http://127.0.0.1:5000")
    app.run(port=5000)
