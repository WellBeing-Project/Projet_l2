import customtkinter as ctk
from utils import get_db, calcul_score, add_history
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt


class MenuPrincipal(ctk.CTk):

    def __init__(self, user_id):
        super().__init__()

        self.user_id = user_id
        self.title("WellBeing – Tableau de bord")
        self.geometry("1100x700")
        self.configure(fg_color="#F5F7F8")

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # SIDEBAR
        self.sidebar = ctk.CTkFrame(self, width=260, corner_radius=20, fg_color="#EAFAF1")
        self.sidebar.grid(row=0, column=0, sticky="ns", padx=20, pady=20)

        ctk.CTkLabel(self.sidebar, text="🌱 WellBeing",
                     font=("Poppins", 26, "bold"), text_color="#1E8449").pack(pady=20)

        self._menu_btn("👤 Mon profil", self.page_profil)
        self._menu_btn("✏️ Modifier profil", self.page_modifier)
        self._menu_btn("❤️ Score & graphique", self.page_score)
        self._menu_btn("🤖 Analyse repas (IA)", self.page_ia)

        ctk.CTkButton(self.sidebar, text="Déconnexion",
                      fg_color="#D35B58", hover_color="#B84444",
                      height=45, command=self.destroy).pack(pady=40, fill="x")

        # CONTENT
        self.content = ctk.CTkFrame(self, corner_radius=20, fg_color="#FEF9E7")
        self.content.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)

        self.page_profil()

    # ======================================================
    # FIX : Cancel animations to avoid "invalid command name"
    # ======================================================
    def cancel_after_tasks(self):
        try:
            tasks = self.tk.call("after", "info").split()
            for task in tasks:
                try:
                    self.after_cancel(task)
                except:
                    pass
        except:
            pass

    # ======================================================
    def clear_content(self):
        self.cancel_after_tasks()
        for w in self.content.winfo_children():
            try:
                w.destroy()
            except:
                pass

    # ======================================================
    def _menu_btn(self, text, command):
        btn = ctk.CTkButton(self.sidebar, text=text, fg_color="#2ECC71",
                            hover_color="#27AE60", corner_radius=12,
                            height=45, command=command)
        btn.pack(pady=8, fill="x")

    # ======================================================
    def page_profil(self):
        self.clear_content()

        ctk.CTkLabel(self.content, text="👤 Mon Profil",
                     font=("Poppins", 30, "bold"),
                     text_color="#1E8449").pack(pady=25)

        conn = get_db()
        cur = conn.cursor()
        cur.execute("""
            SELECT email, age, weight, height, gender, activity
            FROM users WHERE id=%s
        """, (self.user_id,))
        email, age, p, t, g, a = cur.fetchone()
        conn.close()

        infos = [
            f"Email : {email}",
            f"Âge : {age or 'Non renseigné'}",
            f"Poids : {p or 'Non renseigné'} kg",
            f"Taille : {t or 'Non renseigné'} m",
            f"Sexe : {g or 'Non renseigné'}",
            f"Activité : {a or 'Non renseigné'}",
        ]

        for info in infos:
            ctk.CTkLabel(self.content, text=info,
                         font=("Poppins", 20), text_color="#555").pack(pady=5)

    # ======================================================
    def page_modifier(self):
        self.clear_content()

        ctk.CTkLabel(self.content, text="✏️ Modifier mon profil",
                     font=("Poppins", 28, "bold"), text_color="#1E8449").pack(pady=20)

        self.age = self._entry("Âge")
        self.weight = self._entry("Poids (kg)")
        self.height = self._entry("Taille (m)")
        self.gender = self._entry("Sexe (H/F)")
        self.activity = self._entry("Activité (faible / moyenne / élevée)")

        ctk.CTkButton(self.content, text="Enregistrer",
                      fg_color="#27AE60", height=45,
                      command=self.save_profile).pack(pady=25)

    def _entry(self, placeholder):
        e = ctk.CTkEntry(self.content, placeholder_text=placeholder,
                         width=250, height=45, corner_radius=10)
        e.pack(pady=8)
        return e

    # ======================================================
    def save_profile(self):
        age = self.age.get().strip()
        weight = self.weight.get().strip()
        height = self.height.get().strip()
        gender = self.gender.get().strip()
        activity = self.activity.get().lower().strip()

        if activity not in ["faible", "moyenne", "élevée"]:
            ctk.CTkLabel(self.content, text="❌ Activité invalide",
                         font=("Poppins", 18), text_color="red").pack(pady=10)
            return

        try:
            weight = float(weight)
            height = float(height)
            age = int(age)
        except:
            ctk.CTkLabel(self.content, text="❌ Valeurs invalides",
                         font=("Poppins", 18), text_color="red").pack(pady=10)
            return

        conn = get_db()
        cur = conn.cursor()
        cur.execute("""
            UPDATE users
            SET age=%s, weight=%s, height=%s, gender=%s, activity=%s
            WHERE id=%s
        """, (age, weight, height, gender, activity, self.user_id))
        conn.commit()
        conn.close()

        score = calcul_score(weight, height, age, activity)
        add_history(self.user_id, weight, score)

        self.page_score()

    # ======================================================
    def page_score(self):
        self.clear_content()

        conn = get_db()
        cur = conn.cursor()
        cur.execute("""
            SELECT weight, height, age, activity
            FROM users WHERE id=%s
        """, (self.user_id,))
        w, h, a, act = cur.fetchone()
        conn.close()

        if None in (w, h, a, act):
            ctk.CTkLabel(self.content, text="⚠️ Complète ton profil.",
                         font=("Poppins", 20), text_color="#555").pack(pady=20)
            return

        score = calcul_score(w, h, a, act)

        # COLORS + SMILEY
        if score < 40:
            color, smiley, msg = "#D9534F", "😢", "Santé très faible."
        elif score < 60:
            color, smiley, msg = "#F39C12", "😐", "Santé moyenne."
        elif score < 75:
            color, smiley, msg = "#F4D03F", "😊", "Santé correcte."
        else:
            color, smiley, msg = "#2ECC71", "😁", "Excellent !"

        ctk.CTkLabel(self.content, text="❤️ Score Santé",
                     font=("Poppins", 32, "bold"),
                     text_color="#1E8449").pack(pady=10)

        ctk.CTkLabel(self.content, text=smiley,
                     font=("Poppins", 80), text_color=color).pack()

        ctk.CTkLabel(self.content, text=f"{score}/100",
                     font=("Poppins", 60, "bold"),
                     text_color=color).pack(pady=10)

        ctk.CTkLabel(self.content, text=msg,
                     font=("Poppins", 20), text_color="#555").pack(pady=5)

        # HISTOGRAM
        conn = get_db()
        cur = conn.cursor()
        cur.execute("""
            SELECT date, score FROM history
            WHERE user_id=%s ORDER BY date
        """, (self.user_id,))
        rows = cur.fetchall()
        conn.close()

        if len(rows) == 0:
            ctk.CTkLabel(self.content, text="Aucun historique.",
                         font=("Poppins", 16), text_color="#777").pack(pady=20)
            return

        dates = [str(r[0]) for r in rows]
        scores = [r[1] for r in rows]

        colors = [
            "#D9534F" if s < 40 else
            "#F39C12" if s < 60 else
            "#F4D03F" if s < 75 else
            "#2ECC71" for s in scores
        ]

        fig, ax = plt.subplots(figsize=(7, 3.8), dpi=100)
        ax.bar(dates, scores, color=colors)
        ax.set_title("Historique du Score Santé")
        ax.set_ylim(0, 100)
        ax.tick_params(axis='x', rotation=45)
        fig.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=self.content)
        canvas.get_tk_widget().pack(pady=25)
        canvas.draw()

    # ======================================================
    def page_ia(self):
        self.clear_content()
        ctk.CTkLabel(self.content, text="🤖 Analyse repas (IA)",
                     font=("Poppins", 28, "bold"),
                     text_color="#1E8449").pack(pady=20)

        ctk.CTkLabel(self.content,
                     text="(Module IA bientôt disponible)",
                     font=("Poppins", 20), text_color="#555").pack(pady=40)
