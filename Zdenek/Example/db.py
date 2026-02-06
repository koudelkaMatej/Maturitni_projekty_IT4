# db.py
import mysql.connector

def get_db():
    return mysql.connector.connect(
        host="dbs.spskladno.cz",
        user="student24",
        password="spsnet",
        database="vyuka24"
    )
