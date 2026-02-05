from flask import Flask, render_template, jsonify, request
import mysql.connector
from mysql.connector import Error
import json
from datetime import datetime
from flask_cors import CORS

#pip install -r requirements.txt

app = Flask(__name__)
CORS(app)  # Povolit CORS pro komunikaci mezi frontend a backend

# Konfigurace databáze
DB_CONFIG = {
    'host': 'dbs.spskladno.cz',  
    'user': 'student19',          
    'password': 'spsnet',      
    'database': 'vyuka19'  
}

def connect_to_database():
    """Vytvoření připojení k databázi"""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        if connection.is_connected():
            return connection
    except Error as e:
        print(f"Chyba připojení k databázi: {e}")
        return None

def create_table():
    """Vytvoření tabulky pro skóre pokud neexistuje"""
    connection = connect_to_database()
    if connection:
        try:
            cursor = connection.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS scores (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    player_name VARCHAR(50) NOT NULL,
                    score INT NOT NULL,
                    game_date DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            connection.commit()
            cursor.close()
        except Error as e:
            print(f"Chyba při vytváření tabulky: {e}")
        finally:
            if connection.is_connected():
                connection.close()

@app.route('/')
def index():
    """Zobrazí hlavní stránku"""
    return render_template('index.html')

@app.route('/api/scores', methods=['GET'])
def get_scores():
    """Získá skóre z databáze"""
    connection = connect_to_database()
    if connection:
        try:
            cursor = connection.cursor(dictionary=True)
            
            # Získáme top 10 nejlepších skóre
            cursor.execute("""
                SELECT player_name, score, DATE_FORMAT(game_date, '%d.%m.%Y %H:%i') as formatted_date 
                FROM scores 
                ORDER BY score DESC 
                LIMIT 10
            """)
            
            scores = cursor.fetchall()
            cursor.close()
            connection.close()
            
            return jsonify({
                'success': True,
                'scores': scores,
                'last_update': datetime.now().strftime('%d.%m.%Y %H:%M:%S')
            })
            
        except Error as e:
            return jsonify({
                'success': False,
                'error': f"Chyba při načítání skóre: {str(e)}"
            })
    else:
        return jsonify({
            'success': False,
            'error': "Nelze připojit k databázi"
        })

@app.route('/api/scores', methods=['POST'])
def add_score():
    """Přidá nové skóre do databáze"""
    data = request.json
    player_name = data.get('player_name')
    score = data.get('score')
    
    if not player_name or not score:
        return jsonify({
            'success': False,
            'error': "Chybí jméno nebo skóre"
        })
    
    connection = connect_to_database()
    if connection:
        try:
            cursor = connection.cursor()
            cursor.execute("""
                INSERT INTO scores (player_name, score) 
                VALUES (%s, %s)
            """, (player_name, score))
            
            connection.commit()
            cursor.close()
            connection.close()
            
            return jsonify({
                'success': True,
                'message': "Skóre uloženo"
            })
            
        except Error as e:
            return jsonify({
                'success': False,
                'error': f"Chyba při ukládání skóre: {str(e)}"
            })
    else:
        return jsonify({
            'success': False,
            'error': "Nelze připojit k databázi"
        })

if __name__ == '__main__':
    # Vytvoří tabulku při spuštění aplikace
    create_table()
    app.run(debug=True, host='0.0.0.0', port=5000)