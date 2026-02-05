from flask import Flask, render_template, request
import mysql.connector
import webbrowser
from settings import *
app = Flask(__name__)
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

@app.route('/user/<username>')
def user_profile(username):
    for char in list(username): #Kontrola jestli nebyl v uri využit nevyžádaný znak
        if char not in povolené_znaky:
            return f"Uživatel {username} nenalezen.", 404
    query = "SELECT * FROM Score WHERE username = %s"
    mycursor.execute(query, (username,))
    user_data = mycursor.fetchone()

    if not user_data:
        return f"Uživatel {username} nenalezen.", 404
    columns = [desc[0] for desc in mycursor.description] #Hodnoty skóre uživatele
    user_dict = dict(zip(columns, user_data)) #Hodnoty spojím do dict, pro snazší manipulaci s daty
    return render_template('profile.html', user=user_dict)

if __name__ == '__main__':
    webbrowser.open("http://localhost:5000")
    app.run(debug=False)
