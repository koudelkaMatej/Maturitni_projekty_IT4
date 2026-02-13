from flask import Flask, render_template, request, flash, redirect, url_for, session
import mysql.connector
import webbrowser, random
from settings import *
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)
app.secret_key = str(random.randint(1203,108234))
mydb = mysql.connector.connect(
    host = host
    ,user = username
    ,password = password
    ,database = database
)
mycursor = mydb.cursor()
def get_leaderboard(obtiznost):
    if obtiznost not in (sloupce): #Prevence
        obtiznost = "Easy"
    query = f"""
        SELECT username, {obtiznost}
        FROM Score
        ORDER BY {obtiznost} DESC
    """#získám jméno a hodnotu skóre + vše seřadím dle hodnot skóre
    mycursor.execute(query)
    rows = mycursor.fetchall()
    return rows #Vracím hodnoty

@app.route('/', methods=['GET', 'POST'])
def index():
    obtiznost = request.form.get('obtiznost', 'Easy') #Získám hodnoty z GET requestu
    leaderboard = get_leaderboard(obtiznost) #Využiju funkce pro srovnání leaderboardu
    return render_template('index.html', obtiznost=obtiznost, leaderboard=leaderboard)


@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_input = request.form.get('username')
        for char in list(user_input): #Kontrola jestli nebyl v inputu využit nevyžádaný znak
            if char not in povolené_znaky:
                return render_template('login.html', msg="Nepovolený znak detekován")
        pass_input = request.form.get('password')

        mycursor.execute(f"SELECT * FROM Score WHERE username = '{user_input}'")
        user_data = mycursor.fetchone()

        if user_data and check_password_hash(user_data[1], pass_input):
            session['user'] = user_input
            return redirect(url_for('index'))
        else:
            return render_template("login.html", msg="Chybné jméno nebo heslo")
            
    return render_template('login.html', msg="")

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        user_input = request.form.get('username')
        for char in list(user_input): #Kontrola jestli nebyl v inputu využit nevyžádaný znak
            if char not in povolené_znaky:
                return render_template('register.html', msg="Nepovolený znak detekován")
        pass_input = request.form.get('password')
        confirm_pass = request.form.get('confirm_password')

        if pass_input != confirm_pass:
            return render_template('register.html', msg="Hesla se neshodují")

        mycursor.execute(f"SELECT username FROM Score WHERE username = '{user_input}'")
        if mycursor.fetchone():
            return render_template('register.html', msg="Uživatel s tímto jménem již existuje")

        hashed_password = generate_password_hash(pass_input)
        mycursor.execute(f"INSERT INTO Score (username, password, Easy, Medium, Hard) VALUES ('{user_input}', '{hashed_password}', 0, 0, 0)")
        mydb.commit()
        return redirect(url_for('login'))

    return render_template('register.html', msg="")

@app.route('/user/<username>')
def user_profile(username):
    for char in list(username): #Kontrola jestli nebyl v uri využit nevyžádaný znak
        if char not in povolené_znaky:
            return f"Uživatel {username} nenalezen.", 404
    mycursor.execute(f"SELECT * FROM Score WHERE username = '{username}'")
    user_data = list(mycursor.fetchone())
    if not user_data:
        return f"Uživatel {username} nenalezen.", 404
    columns = [desc[0] for desc in mycursor.description] #Hodnoty skóre uživatele
    #Mazání sloupce password uživatele
    columns.pop(1)
    user_data.pop(1)
    user_dict = dict(zip(columns, user_data)) #Hodnoty spojím do dict, pro snazší manipulaci s daty
    return render_template('profile.html', user=user_dict)

if __name__ == '__main__':
    webbrowser.open("http://localhost:5000")
    app.run(debug=False)
