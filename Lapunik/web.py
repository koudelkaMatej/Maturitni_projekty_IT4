# web.py - Moderní prezentační stránka a webový žebříček (leaderboard).
# Využívá webový framework Flask. Připojuje se přímo na produkční databázi a dynamicky generuje HTML.
from flask import Flask, url_for
import mysql.connector

app = Flask(__name__)

@app.route("/")
def leaderboard():
    """
    Jediný HTTP endpoint (routa) aplikace, obsluhující zobrazení hlavní stránky.
    Načte skóre sestupně a vygeneruje čistý HTML kód naplněný těmito daty do podoby žebříčku.
    """
    players = []
    error_msg = ""
    try:
        # Dynamické načtení z databáze před každým requestem
        db = mysql.connector.connect(
            host="dbs.spskladno.cz",
            user="student31",
            password="spsnet",
            database="vyuka31"
        )
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT username, highscore FROM users ORDER BY highscore DESC")
        players = cursor.fetchall()
        db.close()
    except Exception as e:
        error_msg = f"<div class='db-error'>Databáze není dostupná.</div>"

    html_start = """
    <!DOCTYPE html>
    <html lang="cs">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Pixel Invaders</title>
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Exo+2:wght@300;400;600;700&family=Roboto:wght@300;400;500;700&display=swap&subset=latin-ext');

            *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

            :root {
                --cyan: #00d4ff;
                --cyan-dim: rgba(0, 212, 255, 0.15);
                --gold: #f5c842;
                --silver: #c0c0c0;
                --bronze: #cd7f3a;
                --bg: #06060f;
                --card: rgba(12, 18, 30, 0.85);
                --border: rgba(0, 212, 255, 0.2);
            }

            body {
                background: var(--bg);
                color: #d0dce8;
                font-family: 'Roboto', sans-serif;
                min-height: 100vh;
                overflow-x: hidden;
            }

            /* Hvězdné pozadí */
            body::before {
                content: '';
                position: fixed;
                inset: 0;
                z-index: -1;
                background-image:
                    radial-gradient(1px 1px at 15% 25%, rgba(255,255,255,0.6), transparent),
                    radial-gradient(1px 1px at 55% 10%, rgba(255,255,255,0.5), transparent),
                    radial-gradient(2px 2px at 80% 60%, rgba(255,255,255,0.4), transparent),
                    radial-gradient(1px 1px at 35% 75%, rgba(255,255,255,0.6), transparent),
                    radial-gradient(1px 1px at 70% 35%, rgba(255,255,255,0.5), transparent),
                    radial-gradient(2px 2px at 10% 85%, rgba(255,255,255,0.3), transparent),
                    radial-gradient(1px 1px at 90% 15%, rgba(255,255,255,0.6), transparent),
                    radial-gradient(1px 1px at 45% 50%, rgba(255,255,255,0.4), transparent);
                background-size: 400px 400px;
                background-repeat: repeat;
            }

            /* Header */
            header {
                padding: 48px 24px 36px;
                text-align: center;
                border-bottom: 1px solid var(--border);
                background: linear-gradient(180deg, rgba(0,30,50,0.6) 0%, transparent 100%);
            }

            .logo {
                font-family: 'Exo 2', sans-serif;
                font-size: clamp(32px, 6vw, 60px);
                font-weight: 700;
                color: #fff;
                letter-spacing: 6px;
                text-transform: uppercase;
                text-shadow: 0 0 30px var(--cyan), 0 0 60px rgba(0,212,255,0.3);
            }

            .tagline {
                margin-top: 10px;
                font-size: 13px;
                letter-spacing: 3px;
                text-transform: uppercase;
                color: var(--cyan);
                opacity: 0.7;
            }

            /* Layout */
            .container {
                max-width: 1180px;
                margin: 48px auto;
                padding: 0 24px;
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 28px;
            }

            @media (max-width: 768px) {
                .container { grid-template-columns: 1fr; }
            }

            /* Karty */
            .card {
                background: var(--card);
                border: 1px solid var(--border);
                border-radius: 12px;
                padding: 28px;
                backdrop-filter: blur(12px);
                transition: border-color 0.25s, box-shadow 0.25s;
            }

            .card:hover {
                border-color: rgba(0,212,255,0.45);
                box-shadow: 0 0 28px rgba(0,212,255,0.08);
            }

            .card-title {
                font-family: 'Exo 2', sans-serif;
                font-size: 13px;
                letter-spacing: 2px;
                text-transform: uppercase;
                color: var(--cyan);
                margin-bottom: 20px;
                padding-bottom: 14px;
                border-bottom: 1px solid var(--border);
            }

            /* Screenshot */
            .screenshot {
                width: 100%;
                border-radius: 8px;
                border: 1px solid var(--border);
                margin-top: 18px;
                display: block;
            }

            /* Ovládání */
            .controls-list {
                list-style: none;
                display: flex;
                flex-direction: column;
                gap: 10px;
            }

            .controls-list li {
                display: flex;
                align-items: center;
                gap: 12px;
                font-size: 14px;
                color: #8aa0b8;
            }

            .key {
                display: inline-block;
                background: rgba(0,212,255,0.1);
                border: 1px solid var(--border);
                border-radius: 5px;
                padding: 2px 8px;
                font-family: 'Exo 2', sans-serif;
                font-size: 12px;
                color: var(--cyan);
                white-space: nowrap;
                min-width: 70px;
                text-align: center;
            }

            .desc { color: #c0cfe0; }

            /* Leaderboard tabulka */
            .db-error {
                background: rgba(200,50,50,0.1);
                border: 1px solid rgba(200,50,50,0.3);
                border-radius: 6px;
                padding: 10px 14px;
                font-size: 13px;
                color: #e07070;
                margin-bottom: 16px;
            }

            .leaderboard {
                width: 100%;
                border-collapse: collapse;
                margin-top: 4px;
            }

            .leaderboard th {
                font-family: 'Exo 2', sans-serif;
                font-size: 11px;
                letter-spacing: 1.5px;
                text-transform: uppercase;
                color: rgba(0,212,255,0.5);
                padding: 0 12px 12px;
                text-align: left;
                border-bottom: 1px solid var(--border);
            }

            .leaderboard td {
                padding: 13px 12px;
                font-size: 14px;
                border-bottom: 1px solid rgba(0,212,255,0.06);
            }

            .leaderboard tr:last-child td { border-bottom: none; }
            .leaderboard tr:hover td { background: var(--cyan-dim); }

            .rank-1 td { color: var(--gold); }
            .rank-2 td { color: var(--silver); }
            .rank-3 td { color: var(--bronze); }

            .rank-num {
                font-family: 'Exo 2', sans-serif;
                font-weight: 700;
            }

            .score-val {
                font-family: 'Exo 2', sans-serif;
                font-weight: 700;
                text-align: right;
            }

            .empty-state {
                text-align: center;
                padding: 40px 0;
                color: #4a6070;
                font-size: 14px;
            }

            /* Footer */
            footer {
                text-align: center;
                padding: 28px;
                font-size: 12px;
                color: #2a3a4a;
                border-top: 1px solid rgba(0,212,255,0.07);
                margin-top: 20px;
            }
        </style>
    </head>
    <body>
        <header>
            <div class="logo">Pixel Invaders</div>
        </header>

        <div class="container">
            <!-- Levá karta: O hře -->
            <div class="card">
                <div class="card-title">O hře</div>
                <p style="font-size:14px;line-height:1.7;color:#8aa0b8;margin-bottom:20px;">
                    2D arkádová střílečka napsaná v Pythonu a Pygame.
                    Přežij co nejdéle, sesbírej vylepšení zbraní, štítů a zdraví.
                    Tvoje nejlepší skóre se ukládá do globální databáze.
                </p>
                <ul class="controls-list">
                    <li><span class="key">← →</span> <span class="desc">Pohyb</span></li>
                    <li><span class="key">SPACE</span> <span class="desc">Střelba</span></li>
                    <li><span class="key">SHIFT</span> <span class="desc">Úhybný manévr (Dash)</span></li>
                    <li><span class="key">ESC</span> <span class="desc">Pauza / Menu</span></li>
                    <li><span class="key">[P]</span> <span class="desc">Přeskočit level (cheat)</span></li>
                </ul>
                <img class="screenshot" src="{img_url}" alt="Náhled hry">
            </div>

            <!-- Pravá karta: Žebříček -->
            <div class="card">
                <div class="card-title">Nejlepší hráči</div>
                {err}
    """

    html = html_start.replace("{img_url}", url_for('static', filename='screenshot.png')).replace("{err}", error_msg)

    # Sestavení zobrazení tabulky – dynamický string format
    if players:
        html += '<table class="leaderboard"><tr><th>#</th><th>Hráč</th><th style="text-align:right">Skóre</th></tr>'
        for i, p in enumerate(players, 1):
            rank_class = f"rank-{i}" if i <= 3 else ""
            medal = ["🥇", "🥈", "🥉"][i-1] if i <= 3 else str(i)
            html += f"""
                <tr class="{rank_class}">
                    <td class="rank-num">{medal}</td>
                    <td>{p['username']}</td>
                    <td class="score-val">{p['highscore']:,}</td>
                </tr>"""
        html += "</table>"
    else:
        html += '<div class="empty-state">Zatím žádní hráči.<br>Buď první kdo se přihlásí!</div>'

    html += """
            </div>
        </div>
        <footer>Pixel Invaders &nbsp;·&nbsp; Python &amp; Pygame</footer>
    </body>
    </html>
    """
    return html

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
