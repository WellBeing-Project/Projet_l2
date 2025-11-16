from utils import (
    create_tables,
    create_user,
    login,
    calcul_score,
    get_db,
    add_history,
    afficher_graphique
)

################################
# CHOISIR LE MODE : CONSOLE / INTERFACE GRAPHIQUE
################################

USE_GUI = True   # <<< METS False POUR UTILISER LE TERMINAL

if USE_GUI:
    from interface import WellBeingApp   # on importe l’interface Tkinter


################################
#  MODE CONSOLE : AFFICHER LE PROFIL
################################

def afficher_profil(user_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT email, age, weight, height, gender, activity 
        FROM users WHERE id=?
    """, (user_id,))
    data = cur.fetchone()
    conn.close()

    print("\n=== MON PROFIL ===")
    print(f"Email      : {data[0]}")
    print(f"Âge        : {data[1]}")
    print(f"Poids      : {data[2]} kg")
    print(f"Taille     : {data[3]} m")
    print(f"Sexe       : {data[4]}")
    print(f"Activité   : {data[5]}")


################################
#  MODE CONSOLE : MODIFIER LE PROFIL
################################

def modifier_profil(user_id):
    print("\n=== MODIFIER MON PROFIL ===")

    try:
        age = int(input("Âge : "))
        poids = float(input("Poids (kg) : "))
        taille = float(input("Taille (m) : "))
        sexe = input("Sexe : ").lower()
        activite = input("Activité (faible/moyenne/élevée) : ").lower()
    except:
        print("Erreur : valeurs invalides.")
        return

    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        UPDATE users 
        SET age=?, weight=?, height=?, gender=?, activity=?
        WHERE id=?
    """, (age, poids, taille, sexe, activite, user_id))

    conn.commit()
    conn.close()

    score = calcul_score(poids, taille, age, activite)
    add_history(user_id, poids, score)

    print(f"\n✓ Profil mis à jour ! Score santé : {score}/100")


################################
#  MENU UTILISATEUR (TERMINAL)
################################

def menu_user(user_id):
    while True:
        print("\n=== MENU UTILISATEUR ===")
        print("1. Mon profil")
        print("2. Calculer mon score santé")
        print("3. Voir mon graphique de santé")
        print("4. (IA bientôt) Analyser un repas")
        print("0. Déconnexion")

        choix = input("> ")

        if choix == "1":
            afficher_profil(user_id)

        elif choix == "2":
            conn = get_db()
            cur = conn.cursor()
            cur.execute("SELECT weight, height, age, activity FROM users WHERE id=?", (user_id,))
            p, t, a, act = cur.fetchone()
            conn.close()

            score = calcul_score(p, t, a, act)
            print(f"\nVotre score santé : {score}/100")

        elif choix == "3":
            afficher_graphique(user_id)

        elif choix == "4":
            print("📸 Module IA bientôt disponible.")

        elif choix == "0":
            print("Déconnexion...")
            break

        else:
            print("Choix invalide.")


################################
#  MENU PRINCIPAL (TERMINAL)
################################

def main_console():
    print("=== BIENVENUE DANS WELLBEING ===")

    while True:
        print("\n1. Créer un compte")
        print("2. Se connecter")
        print("0. Quitter")

        choix = input("> ")

        if choix == "1":
            email = input("Email : ")
            password = input("Mot de passe : ")

            if create_user(email, password):
                print("✓ Compte créé")
            else:
                print("Erreur : email déjà utilisé.")

        elif choix == "2":
            email = input("Email : ")
            password = input("Mot de passe : ")

            user_id = login(email, password)
            if user_id:
                print("✓ Connexion réussie")
                menu_user(user_id)
            else:
                print("✗ Email ou mot de passe incorrect.")

        elif choix == "0":
            print("À bientôt !")
            break


################################
#  LANCEMENT AUTO
################################

if __name__ == "__main__":
    create_tables()

    if USE_GUI:
        WellBeingApp()   # << LANCEMENT DE L’INTERFACE GRAPHIQUE
    else:
        main_console()   # << LANCEMENT VERSION TERMINALE
