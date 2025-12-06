import mysql.connector
import hashlib
import datetime
import base64
import requests
import json

# =====================================================
#  CONFIGURATION OLLAMA (IA LOCALE)
# =====================================================

OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "llava-phi3:latest"  # modèle vision installé localement


# =====================================================
#  IA TEXTE
# =====================================================
def ask_ollama(prompt):
    """Envoie un prompt texte à Ollama et retourne proprement la réponse."""
    try:
        payload = {"model": OLLAMA_MODEL, "prompt": prompt}

        r = requests.post(OLLAMA_URL, json=payload, stream=True)

        final_text = ""

        # Ollama renvoie un flux JSON → on lit ligne par ligne
        for line in r.iter_lines():
            if not line:
                continue
            try:
                data = json.loads(line.decode())
                if "response" in data:
                    final_text += data["response"]
            except:
                continue

        return final_text.strip()

    except Exception as e:
        print("Erreur Ollama texte:", e)
        return "[Erreur IA]"


# =====================================================
#  IA VISION (LLAVA)
# =====================================================
# =====================================================
#  IA VISION (LLAVA) — Nouvelle version
# =====================================================

 
def analyze_image_with_ollama(image_path):
    try:
        # --- Encode image en base64 ---
        with open(image_path, "rb") as f:
            img_base64 = base64.b64encode(f.read()).decode("utf-8")

        # --- PROMPT : réponse UNIQUEMENT en JSON FRANÇAIS ---
        prompt = """
        Tu es un assistant spécialisé en analyse nutritionnelle d'images.
        Tu dois OBLIGATOIREMENT répondre UNIQUEMENT avec du JSON strict,
        sans aucun texte, phrase, emoji, explication ou commentaire.

        La réponse doit être en FRANÇAIS.
        N'inventes pas d'aliments que tu ne vois pas, si tu n'es pas certain n'écris pas.

        Format EXACT attendu :

        {
            "items": [
                {"name": "nom de l'aliment", "calories": nombre, "color": "vert|orange|rouge"}
            ],
            "total": nombre,
            "advice": "phrase de conseil en français"
        }

        Règles :
        - "color" indique si l'aliment est sain ("vert"), modéré ("orange") ou riche ("rouge").
        - Donne une estimation réaliste en calories.
        - Ne retourne RIEN d'autre que le JSON.
        """

        payload = {
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "images": [img_base64],
            "stream": False
        }

        response = requests.post(OLLAMA_URL, json=payload)
        raw = response.json().get("response", "").strip()

        # --- Extraction du JSON pur ---
        start = raw.find("{")
        end = raw.rfind("}")

        if start == -1 or end == -1:
            raise ValueError("Aucun JSON détecté dans la réponse.")

        json_text = raw[start:end + 1]

        return json.loads(json_text)

    except Exception as e:
        print("Erreur analyse image Ollama:", e)
        return {
            "items": [],
            "total": 0,
            "advice": "Impossible d'analyser le repas."
        }

# =====================================================
#  CONFIGURATION MYSQL
# =====================================================

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "30Juin2006*",
    "database": "wellbeing"
}

def get_db():
    return mysql.connector.connect(**DB_CONFIG)


# =====================================================
#  CRÉATION DES TABLES
# =====================================================

def create_tables():
    conn = get_db()
    cur = conn.cursor()

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
#  SÉCURITÉ MOT DE PASSE
# =====================================================

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


# =====================================================
#  CRÉATION UTILISATEUR
# =====================================================

def create_user(email, password):
    try:
        conn = get_db()
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO users (email, password)
            VALUES (%s, %s)
        """, (email, hash_password(password)))

        conn.commit()
        conn.close()
        return True

    except mysql.connector.IntegrityError:
        return False

    except Exception as e:
        print("Erreur create_user:", e)
        return False


# =====================================================
#  LOGIN
# =====================================================

def login(email, password):
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
#  CALCUL SCORE SANTÉ
# =====================================================

def calcul_score(poids, taille, age, activite):
    try:
        poids = float(poids)
        taille = float(taille)
        age = int(age)
    except:
        return None

    if taille <= 0 or poids <= 0:
        return None

    imc = poids / (taille ** 2)
    score = 100

    if imc > 35:
        score -= 40
    elif imc > 30:
        score -= 30
    elif imc > 25:
        score -= 15
    elif imc < 18:
        score -= 10

    if age > 60:
        score -= 20
    elif age > 45:
        score -= 10

    activite = activite.lower()
    if activite == "faible":
        score -= 25
    elif activite == "moyenne":
        score -= 10
    elif activite == "élevée":
        score += 5
    else:
        score -= 15

    return max(0, min(100, score))


# =====================================================
#  HISTORIQUE
# =====================================================

def add_history(user_id, weight, score):
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
