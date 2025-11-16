import sqlite3
import hashlib
import datetime
import matplotlib.pyplot as plt


################################
# BASE DE DONNÉES
################################

def get_db():
    return sqlite3.connect("wellbeing.db")


def create_tables():
    conn = get_db()
    cur = conn.cursor()

    # Table utilisateurs
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE,
            password TEXT,
            age INTEGER,
            weight REAL,
            height REAL,
            gender TEXT,
            activity TEXT
        );
    """)

    # Table historique
    cur.execute("""
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            date TEXT,
            weight REAL,
            score INTEGER
        );
    """)

    conn.commit()
    conn.close()


################################
# CRYPTAGE & AUTHENTIFICATION
################################

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def create_user(email, password):
    try:
        conn = get_db()
        cur = conn.cursor()

        cur.execute("INSERT INTO users (email, password) VALUES (?, ?)",
                    (email, hash_password(password)))

        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print("Erreur création utilisateur :", e)
        return False


def login(email, password):
    conn = get_db()
    cur = conn.cursor()

    cur.execute("SELECT id, password FROM users WHERE email=?", (email,))
    result = cur.fetchone()
    conn.close()

    if result is None:
        return None

    user_id, stored_hash = result

    if stored_hash == hash_password(password):
        return user_id
    else:
        return None



################################
# SCORE SANTÉ
################################

def calcul_score(poids, taille, age, activite):
    imc = poids / (taille * taille)
    score = 100

    # Effet IMC
    if imc > 25:
        score -= 20
    elif imc < 18:
        score -= 10

    # Effet âge
    if age > 45:
        score -= 15

    # Effet activité
    if activite == "faible":
        score -= 20
    elif activite == "moyenne":
        score -= 10

    return max(0, min(score, 100))


################################
# HISTORIQUE
################################

def add_history(user_id, weight, score):
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO history (user_id, date, weight, score)
        VALUES (?, ?, ?, ?)
    """, (user_id, datetime.date.today(), weight, score))

    conn.commit()
    conn.close()



################################
# GRAPHIQUE
################################

def afficher_graphique(user_id):
    conn = get_db()
    cur = conn.cursor()

    cur.execute("SELECT date, score FROM history WHERE user_id=? ORDER BY date", (user_id,))
    rows = cur.fetchall()
    conn.close()

    if len(rows) == 0:
        print("\nAucun historique trouvé.")
        return

    dates = [r[0] for r in rows]
    scores = [r[1] for r in rows]

    plt.plot(dates, scores, marker="o")
    plt.title("Évolution du Score Santé")
    plt.xlabel("Date")
    plt.ylabel("Score")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()
