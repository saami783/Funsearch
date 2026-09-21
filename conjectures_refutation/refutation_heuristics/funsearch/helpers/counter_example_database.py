import os
import sqlite3

def check_if_counterexample_exists(g6: str) -> bool:
    connexion = sqlite3.connect("counterexamples.db")
    cursor = connexion.cursor()
    requete = "SELECT 1 FROM graph WHERE g6_counterexample = ?"
    cursor.execute(requete, (g6,))

    resultat = cursor.fetchone()

    connexion.close()

    return resultat is not None

def check_if_db_exists() -> bool:
    return os.path.exists("counterexamples.db")

def create_db():
    import os
    import sqlite3
    connexion = sqlite3.connect("counterexamples.db")
    cursor = connexion.cursor()

    create_table = """
                   CREATE TABLE IF NOT EXISTS graph
                   (   id INTEGER PRIMARY KEY AUTOINCREMENT,
                       g6_counterexample TEXT NOT NULL UNIQUE
                   )
                   """

    cursor.execute(create_table)
    connexion.commit()
    connexion.close()

def insert_counterexample(g6: str):
    connexion = sqlite3.connect("counterexamples.db")
    cursor = connexion.cursor()
    requete = "INSERT INTO graphs (g6_counterexample) VALUES (?)"
    cursor.execute(requete, (g6,))

    connexion.commit()
    connexion.close()