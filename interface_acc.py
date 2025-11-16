import customtkinter as ctk

from utils import get_db, calcul_score, add_history, afficher_graphique


class MenuPrincipal(ctk.CTk):
    def __init__(self, user_id):
        super().__init__()

        self.user_id = user_id
        self.title("WellBeing – Tableau de bord")
        self.geometry("1000x650")

        # Layout 70% (main panel) - 30% (menu)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # -------------------------------
        # MENU LATERAL
        # -------------------------------
        self.menu = ctk.CTkFrame(self, width=250, corner_radius=20)
        self.menu.grid(row=0, column=0, sticky="nsw", padx=20, pady=20)

        ctk.CTkLabel(self.menu, text="📊 Menu WellBeing",
                     font=("Poppins", 22, "bold")).pack(pady=20)

        ctk.CTkButton(self.menu, text="Mon profil",
                      command=self.page_profil, height=40).pack(pady=10, fill="x")

        ctk.CTkButton(self.menu, text="Modifier mon profil",
                      command=self.page_modifier, height=40).pack(pady=10, fill="x")

        ctk.CTkButton(self.menu, text="Voir mon score santé",
                      command=self.page_score, height=40).pack(pady=10, fill="x")

        ctk.CTkButton(self.menu, text="Graphique santé",
                      command=lambda: afficher_graphique(self.user_id),
                      height=40).pack(pady=10, fill="x")

        ctk.CTkButton(self.menu, text="Analyser un repas (IA)",
                      command=self.page_ia, height=40, fg_color="#A88BEB").pack(pady=10, fill="x")

        ctk.CTkButton(self.menu, text="Déconnexion",
                      command=self.destroy, fg_color="#D35B58", height=40).pack(pady=40, fill="x")

        # -------------------------------
        # PANEL PRINCIPAL (CONTENU)
        # -------------------------------
        self.content = ctk.CTkFrame(self, corner_radius=20)
        self.content.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)

        self.page_profil()

    # -------------------------------
    # PAGE : MON PROFIL
    # -------------------------------
    def page_profil(self):
        self.clear_content()

        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT email, age, weight, height, gender, activity FROM users WHERE id=?", (self.user_id,))
        email, age, weight, height, gender, activity = cur.fetchone()
        conn.close()

        ctk.CTkLabel(self.content, text="👤 Mon Profil", font=("Poppins", 28, "bold")).pack(pady=20)

        infos = [
            f"Email : {email}",
            f"Âge : {age if age else 'Non renseigné'}",
            f"Poids : {weight if weight else 'Non renseigné'} kg",
            f"Taille : {height if height else 'Non renseigné'} m",
            f"Sexe : {gender if gender else 'Non renseigné'}",
            f"Activité : {activity if activity else 'Non renseigné'}"
        ]

        for txt in infos:
            ctk.CTkLabel(self.content, text=txt, font=("Poppins", 18)).pack(pady=4)

    # -------------------------------
    # PAGE : MODIFIER PROFIL
    # -------------------------------
    def page_modifier(self):
        self.clear_content()

        ctk.CTkLabel(self.content, text="✏️ Modifier mon profil",
                     font=("Poppins", 28, "bold")).pack(pady=20)

        self.age = ctk.CTkEntry(self.content, placeholder_text="Âge")
        self.age.pack(pady=7)

        self.weight = ctk.CTkEntry(self.content, placeholder_text="Poids (kg)")
        self.weight.pack(pady=7)

        self.height = ctk.CTkEntry(self.content, placeholder_text="Taille (m)")
        self.height.pack(pady=7)

        self.gender = ctk.CTkEntry(self.content, placeholder_text="Sexe (H/F)")
        self.gender.pack(pady=7)

        self.activity = ctk.CTkEntry(self.content, placeholder_text="Activité (faible/moyenne/élevée)")
        self.activity.pack(pady=7)

        ctk.CTkButton(self.content, text="Enregistrer",
                      command=self.save_profile, fg_color="#5ED18B").pack(pady=20)

    def save_profile(self):
        age = self.age.get()
        weight = self.weight.get()
        height = self.height.get()
        gender = self.gender.get()
        activity = self.activity.get()

        conn = get_db()
        cur = conn.cursor()
        cur.execute("""
            UPDATE users SET age=?, weight=?, height=?, gender=?, activity=? WHERE id=?
        """, (age, weight, height, gender, activity, self.user_id))
        conn.commit()
        conn.close()

        score = calcul_score(float(weight), float(height), int(age), activity)
        add_history(self.user_id, float(weight), score)

        self.page_score()

    # -------------------------------
    # PAGE : SCORE SANTÉ
    # -------------------------------
    def page_score(self):
        self.clear_content()

        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT weight, height, age, activity FROM users WHERE id=?", (self.user_id,))
        weight, height, age, activity = cur.fetchone()
        conn.close()

        score = calcul_score(weight, height, age, activity)

        color = "#D9534F" if score < 40 else "#F0AD4E" if score < 70 else "#5ED18B"

        ctk.CTkLabel(self.content, text="❤️ Score Santé", font=("Poppins", 28, "bold")).pack(pady=20)

        # Score en gros
        ctk.CTkLabel(self.content,
                     text=f"{score}/100",
                     font=("Poppins", 50, "bold"),
                     text_color=color).pack(pady=10)

        # Message personnalisé
        msg = "⚠️ Santé fragile, attention à toi." if score < 40 else \
              "🙂 Santé correcte, continue !" if score < 70 else \
              "💚 Excellent ! Tu es en super forme."

        ctk.CTkLabel(self.content, text=msg, font=("Poppins", 20)).pack(pady=20)

    # -------------------------------
    # PAGE : IA REPAS
    # -------------------------------
    def page_ia(self):
        self.clear_content()

        ctk.CTkLabel(self.content, text="🤖 Analyse de repas (IA)",
                     font=("Poppins", 28, "bold")).pack(pady=20)

        ctk.CTkLabel(self.content,
                     text="Module IA en construction...",
                     font=("Poppins", 20)).pack(pady=40)

    # -------------------------------
    # CLEAR PANEL
    # -------------------------------
    def clear_content(self):
        for widget in self.content.winfo_children():
            widget.destroy()
import sys
print(sys.executable)
print(sys.version)
