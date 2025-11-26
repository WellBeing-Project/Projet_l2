import mysql.connector
import hashlib
import datetime


# =====================================================
#  CONFIGURATION BASE DE DONNÉES MYSQL
# =====================================================

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "30Juin2006*",   # change si besoin
    "database": "wellbeing"
}


def get_db():
    """Retourne une connexion MySQL."""
    return mysql.connector.connect(**DB_CONFIG)


# =====================================================
#  CRÉATION DES TABLES
# =====================================================

def create_tables():
    conn = get_db()
    cur = conn.cursor()

    # Table utilisateurs
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            email VARCHAR(255) UNIQUE,
            password VARCHAR(255),
            age INT,
            weight FLOAT,
            height FLOAT,
            gender VARCHAR(20),
            activity VARCHAR(20)
        );
    """)

    # Table historique
    cur.execute("""
        CREATE TABLE IF NOT EXISTS history (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT,
            date DATE,
            weight FLOAT,
            score INT,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        );
    """)

    conn.commit()
    conn.close()


# =====================================================
#  UTILITAIRES
# =====================================================

def hash_password(password):
    """Hash SHA256 pour sécuriser les mots de passe."""
    return hashlib.sha256(password.encode()).hexdigest()


# =====================================================
#  CRÉATION UTILISATEUR
# =====================================================

def create_user(email, password):
    """Crée un utilisateur. Retourne True si création OK."""
    try:
        conn = get_db()
        cur = conn.cursor()

        cur.execute(
            "INSERT INTO users (email, password) VALUES (%s, %s)",
            (email, hash_password(password))
        )

        conn.commit()
        conn.close()
        return True

    except mysql.connector.IntegrityError:
        # Email déjà existant
        return False

    except Exception as e:
        print("Erreur create_user :", e)
        return False


# =====================================================
#  LOGIN
# =====================================================

def login(email, password):
    """Retourne user_id si connexion OK, sinon None."""
    conn = get_db()
    cur = conn.cursor()

    cur.execute("SELECT id, password FROM users WHERE email=%s", (email,))
    row = cur.fetchone()
    conn.close()

    if row is None:
        return None

    user_id, stored_hash = row

    if stored_hash == hash_password(password):
        return user_id
    return None


# =====================================================
#  CALCUL SCORE SANTÉ (IMC + âge + activité)
# =====================================================

def calcul_score(poids, taille, age, activite):
    """Retourne un score santé entre 0 et 100."""

    try:
        poids = float(poids)
        taille = float(taille)
        age = int(age)
    except:
        return None  # données invalides

    # empêcher crash / valeurs impossibles
    if taille <= 0 or poids <= 0:
        return None

    imc = poids / (taille ** 2)
    score = 100

    # -------------------------
    # Effet IMC
    # -------------------------
    if imc > 35:         # obésité sévère
        score -= 40
    elif imc > 30:       # obésité
        score -= 30
    elif imc > 25:       # surpoids
        score -= 15
    elif imc < 18:       # trop maigre
        score -= 10

    # -------------------------
    # Effet âge
    # -------------------------
    if age > 60:
        score -= 20
    elif age > 45:
        score -= 10

    # -------------------------
    # Effet activité
    # -------------------------
    activite = activite.lower()

    if activite == "faible":
        score -= 25
    elif activite == "moyenne":
        score -= 10
    elif activite == "élevée":
        score += 5
    else:
        # activité invalide → on pénalise
        score -= 15

    # score final borné
    return max(0, min(100, score))


# =====================================================
#  HISTORIQUE / TRACKING
# =====================================================

def add_history(user_id, weight, score):
    """Enregistre le poids & score du jour dans l'historique."""
    try:
        conn = get_db()
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO history (user_id, date, weight, score)
            VALUES (%s, %s, %s, %s)
        """, (user_id, datetime.date.today(), weight, score))

        conn.commit()
        conn.close()

    except Exception as e:
        print("Erreur add_history :", e)
