from flask import Flask, render_template, request, session, redirect, url_for
import mysql.connector
import webbrowser
from settings import host, username, password, database, povolené_znaky
from flask import request

app = Flask(__name__)
app.secret_key = "HESLO1234567890" # tajný klíč, aby fungovalo přihlašování a session

def get_db():
    return mysql.connector.connect(host=host, user=username, password=password, database=database) # připojení k db

@app.route('/')
def index():
    user = session.get('user') # zjištění, jestli je v paměti někdo přihlášený
    return render_template('index.html', user=user)

@app.route('/tab')
def tabulka():
    user = session.get('user')
    level = request.args.get('level', default=2, type=int) # vytažení levelu z adresy (default je 2)
    
    try:
        conn = mysql.connector.connect(host=host, user=username, password=password, database=database)
        cursor = conn.cursor(dictionary=True) # výsledky z db budou jako seznam, co se dobře vypisuje

        query = "SELECT username, time_str FROM pazderao_casy WHERE level = %s ORDER BY time_ms ASC LIMIT 10" # sql dotaz pro top 10
        cursor.execute(query, (level,))
        leaderboard = cursor.fetchall() # uložení vytažených dat do proměnné

        cursor.close()
        conn.close()
        
        return render_template('tab.html', leaderboard=leaderboard, level=level, user=user) # poslání dat do tab.html
    
    except Exception as e:
        print(f"chyba db: {e}")
        return f"Chyba při načítání žebříčku: {e}"

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST': # kontrola, jestli uživatel zrovna odeslal formulář
        user_input = request.form.get('username', '')
        if all(c in povolené_znaky for c in user_input) and user_input.strip() != "": # kontrola znaků kvůli bezpečnosti
            session['user'] = user_input.capitalize() # uložení jména do paměti s velkým písmenem
            return redirect(url_for('profile')) # po přihlášení šup na profil
            
    return render_template('login.html', user=session.get('user'))

@app.route('/logout')
def logout():
    session.pop('user', None) # smazání jména z paměti (odhlášení)
    return redirect(url_for('index'))

@app.route('/about')
def about():
    user = session.get('user') # zjištění jména pro zobrazení v horním menu
    return render_template('about.html', user=user)
    
@app.route('/profile')
def profile():
    if 'user' not in session: # když není nikdo přihlášený, hodí ho to na login
        return redirect(url_for('login'))
        
    user_name = session['user']
    stats = []
    
    try:
        conn = get_db()
        cursor = conn.cursor(dictionary=True)
        query = "SELECT level, time_str FROM pazderao_casy WHERE username = %s ORDER BY level ASC, time_ms ASC" # vytažení časů jen pro tohohle hráče
        cursor.execute(query, (user_name,))
        stats = cursor.fetchall()
    except Exception as e:
        print(f"chyba profilu: {e}")
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close() # bezpečné zavření kurzoru
            conn.close() # zavření spojení s db
            
    return render_template('profile.html', user=user_name, stats=stats) # zobrazení historie časů v profile.html

if __name__ == '__main__':
    webbrowser.open("http://127.0.0.1:5000") # automatické otevření webu v prohlížeči
    app.run(debug=True, port = 5000) # spuštění aplikace