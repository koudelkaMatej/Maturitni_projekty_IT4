import mysql.connector

DB_CONFIG = {
    "host": "dbs.spskladno.cz",
    "user": "student42",
    "password": "spsnet",
    "database": "vyuka42",
}


def get_db():
    return mysql.connector.connect(**DB_CONFIG)
