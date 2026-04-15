import mysql.connector

def reset_players():
    try:
        connection = mysql.connector.connect(
            host="dbs.spskladno.cz",
            user="student31",
            password="spsnet",
            database="vyuka31"
        )
        cursor = connection.cursor()
        # Smaže všechny záznamy z tabulky users
        cursor.execute("DELETE FROM users")
        connection.commit()
        print("Všichni hráči a jejich skóre byli úspěšně smazáni.")
    except Exception as e:
        print(f"Chyba při mazání databáze: {e}")
    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()

if __name__ == "__main__":
    confirm = input("Opravdu chcete smazat VŠECHNY hráče a jejich rekordy? (ano/ne): ")
    if confirm.lower() == 'ano':
        reset_players()
    else:
        print("Akce byla zrušena.")
