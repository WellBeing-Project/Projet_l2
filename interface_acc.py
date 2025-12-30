import customtkinter as ctk
from utils import get_db, calcul_score, add_history, analyze_image_with_ollama
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from tkinter import filedialog, messagebox
from PIL import Image
import os
from datetime import datetime



# ------------------------------------------------------------
# OUTILS
# ------------------------------------------------------------
def get_user_history(user_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT date, score
        FROM history
        WHERE user_id=%s
        ORDER BY date
    """, (user_id,))
    rows = cur.fetchall()
    conn.close()
    return rows


# ------------------------------------------------------------
# APPLICATION PRINCIPALE APRÈS CONNEXION
# ------------------------------------------------------------
class MenuPrincipal(ctk.CTk):

    def __init__(self, user_id):
        super().__init__()

        self.user_id = user_id
        self.title("WellBeing – Tableau de bord")
        self.geometry("1200x750")
        self.configure(fg_color="#F5F7F8")

        self.selected_image_path = None

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Sidebar
        self.sidebar = ctk.CTkFrame(self, width=260, corner_radius=20, fg_color="#EAFAF1")
        self.sidebar.grid(row=0, column=0, sticky="ns", padx=20, pady=20)

        ctk.CTkLabel(
            self.sidebar, text="🌱 WellBeing",
            font=("Poppins", 26, "bold"), text_color="#1E8449"
        ).pack(pady=20)

        self._menu_btn("👤 Mon profil", self.page_profil)
        self._menu_btn("✏️ Modifier profil", self.page_modifier)
        self._menu_btn("❤️ Score & graphique", self.page_score)
        self._menu_btn("🤖 Analyse repas", self.page_ia)
        self._menu_btn("📰 Blog santé", self.page_blog)
        self._menu_btn("📩 Contact", self.page_contact)


        ctk.CTkButton(
            self.sidebar, text="Déconnexion",
            fg_color="#D9534F", hover_color="#B33A3A",
            command=self.destroy
        ).pack(pady=30, fill="x")

        self.content = ctk.CTkFrame(self, corner_radius=20, fg_color="#FEF9E7")
        self.content.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)

        self.page_profil()

    # ------------------------------------------------------------
    def clear_content(self):
        for widget in self.content.winfo_children():
            widget.destroy()

    def _menu_btn(self, text, command):
        btn = ctk.CTkButton(
            self.sidebar,
            text=text,
            anchor="w",
            command=command
        )
        btn.pack(fill="x", padx=20, pady=6)


    def page_contact(self):
        self.clear_content()

        ctk.CTkLabel(
            self.content,
            text="📩 Contact",
            font=("Poppins", 24, "bold"),
            text_color="#1E8449"
        ).pack(pady=20)

        self.contact_email = ctk.CTkEntry(
            self.content,
            placeholder_text="Votre email"
        )
        self.contact_email.pack(pady=10, padx=40, fill="x")

        self.contact_message = ctk.CTkTextbox(
            self.content,
            height=150
        )
        self.contact_message.pack(pady=10, padx=40, fill="x")

        ctk.CTkButton(
            self.content,
            text="Envoyer",
            command=self.send_contact
        ).pack(pady=20)


    def send_contact(self):
        email = self.contact_email.get().strip()
        message = self.contact_message.get("1.0", "end").strip()

        if not email or not message:
            messagebox.showerror("Erreur", "Tous les champs doivent être remplis")
            return

        print("Contact reçu")
        print("Email :", email)
        print("Message :", message)

        messagebox.showinfo("Message envoyé", "Votre message a bien été transmis.")

        self.contact_email.delete(0, "end")
        self.contact_message.delete("1.0", "end")



    # ------------------------------------------------------------
    # PROFIL
    # ------------------------------------------------------------
    def page_profil(self):
        self.clear_content()

        ctk.CTkLabel(
            self.content, text="👤 Mon Profil",
            font=("Poppins", 30, "bold"),
            text_color="#1E8449"
        ).pack(pady=20)

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
            ctk.CTkLabel(
                self.content, text=info,
                font=("Poppins", 20), text_color="#555"
            ).pack(pady=5)

    # ------------------------------------------------------------
    # MODIFIER PROFIL
    # ------------------------------------------------------------
    def page_modifier(self):
        self.clear_content()

        ctk.CTkLabel(
            self.content, text="✏️ Modifier mon profil",
            font=("Poppins", 28, "bold"), text_color="#1E8449"
        ).pack(pady=20)

        self.age = self._entry("Âge")
        self.weight = self._entry("Poids (kg)")
        self.height = self._entry("Taille (m)")
        self.gender = self._entry("Sexe (H/F)")
        self.activity = self._entry("Activité (faible / moyenne / élevée)")

        ctk.CTkButton(
            self.content, text="Enregistrer",
            fg_color="#27AE60", height=45,
            command=self.save_profile
        ).pack(pady=25)

    def _entry(self, placeholder):
        e = ctk.CTkEntry(self.content, placeholder_text=placeholder,
                         width=260, height=45, corner_radius=10)
        e.pack(pady=6)
        return e


    def save_profile(self):
        try:
            age = int(self.age.get())
            weight = float(self.weight.get())
            height = float(self.height.get())
        except ValueError:
            messagebox.showerror(
                "Erreur",
                "Âge, poids et taille doivent être des nombres."
            )
            return

        gender = self.gender.get().strip()
        activity = self.activity.get().lower().strip()

        if not gender or not activity:
            messagebox.showerror(
                "Erreur",
                "Tous les champs doivent être remplis."
            )
            return

        if activity.startswith("faib"):
            activity = "faible"
        elif activity.startswith("moy"):
            activity = "moyenne"
        elif activity.startswith("el") or activity.startswith("él"):
            activity = "élevée"
        else:
            messagebox.showerror(
                "Erreur",
                "Activité invalide (faible, moyenne ou élevée)."
            )
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

        messagebox.showinfo(
            "Succès",
            "Profil mis à jour avec succès."
        )

        self.page_score()

    # ------------------------------------------------------------
    # SCORE + GRAPHIQUE
    # ------------------------------------------------------------
    def page_score(self):
        self.clear_content()

        data = get_user_history(self.user_id)
        if not data:
            ctk.CTkLabel(
                self.content, text="Aucune donnée disponible",
                font=("Poppins", 18)
            ).pack(pady=20)
            return

        conn = get_db()
        cur = conn.cursor()
        cur.execute("""
            SELECT weight, height, age, activity 
            FROM users WHERE id=%s
        """, (self.user_id,))
        w, h, a, act = cur.fetchone()
        conn.close()

        score = calcul_score(w, h, a, act)

        if score < 40:
            color, smiley, msg = "#D9534F", "😢", "Santé très faible."
        elif score < 60:
            color, smiley, msg = "#F39C12", "😐", "Santé moyenne."
        elif score < 75:
            color, smiley, msg = "#F4D03F", "😊", "Santé correcte."
        else:
            color, smiley, msg = "#2ECC71", "😁", "Excellent !"

        ctk.CTkLabel(
            self.content, text="❤️ Score Santé",
            font=("Poppins", 32, "bold"),
            text_color="#1E8449"
        ).pack(pady=10)

        ctk.CTkLabel(
            self.content, text=smiley,
            font=("Poppins", 90),
            text_color=color
        ).pack()

        ctk.CTkLabel(
            self.content, text=f"{score}/100",
            font=("Poppins", 60, "bold"),
            text_color=color
        ).pack(pady=10)

        ctk.CTkLabel(
            self.content, text=msg,
            font=("Poppins", 22),
            text_color="#555"
        ).pack(pady=5)

        rows = get_user_history(self.user_id)
        dates = [str(r[0]) for r in rows]
        scores = [r[1] for r in rows]

        fig, ax = plt.subplots(figsize=(7, 3.8), dpi=100)
        ax.bar(dates, scores)
        ax.set_ylim(0, 100)
        ax.set_title("Historique du score santé")
        ax.tick_params(axis='x', rotation=45)
        fig.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=self.content)
        canvas.draw()
        canvas.get_tk_widget().pack(pady=25)

    # ------------------------------------------------------------
    # IA
    # ------------------------------------------------------------
    def page_ia(self):
        self.clear_content()

        ctk.CTkLabel(
            self.content, text="🤖 Analyse repas",
            font=("Poppins", 32, "bold"),
            text_color="#1E8449"
        ).pack(pady=20)

        ctk.CTkButton(
            self.content, text="📸 Choisir une image",
            fg_color="#2ECC71",
            command=self._choose_image
        ).pack(pady=10)

        self.image_label = ctk.CTkLabel(self.content, text="")
        self.image_label.pack(pady=10)

        ctk.CTkButton(
            self.content, text="Analyser le repas",
            fg_color="#1F8EF1",
            command=self._analyze_image
        ).pack(pady=15)

        self.response_label = ctk.CTkTextbox(
            self.content, width=700, height=260,
            font=("Poppins", 16)
        )
        self.response_label.pack(pady=20)

    def _choose_image(self):
        file = filedialog.askopenfilename(
            filetypes=[("Images", "*.jpg *.jpeg *.png")]
        )
        if not file:
            return

        self.selected_image_path = "temp.jpg"
        img = Image.open(file).convert("RGB").resize((384, 384))
        img.save(self.selected_image_path)

        preview = ctk.CTkImage(img, size=(250, 250))
        self.image_label.configure(image=preview)
        self.image_label.image = preview

    def _analyze_image(self):
        self.response_label.delete("0.0", "end")
        if not self.selected_image_path:
            return

        data = analyze_image_with_ollama(self.selected_image_path)
        if not data:
            return

        for item in data.get("items", []):
            self.response_label.insert("end", f"- {item['name']} ({item['calories']} kcal)\n")

    # ------------------------------------------------------------
    # BLOG
    # ------------------------------------------------------------
    def page_blog(self):
        self.clear_content()

        ctk.CTkLabel(
            self.content, text="📰 Blog santé",
            font=("Poppins", 30, "bold"),
            text_color="#1E8449"
        ).pack(pady=20)

        main = ctk.CTkFrame(self.content, fg_color="transparent")
        main.pack(fill="both", expand=True, padx=20, pady=10)

        left = ctk.CTkFrame(main, width=300, fg_color="#EAFAF1")
        left.pack(side="left", fill="y", padx=(0, 15))

        ctk.CTkButton(
            left, text="➕ Nouvel article",
            command=self.page_blog_create
        ).pack(fill="x", padx=10, pady=10)

        self.blog_list = ctk.CTkScrollableFrame(left)
        self.blog_list.pack(fill="both", expand=True, padx=10)

        right = ctk.CTkFrame(main)
        right.pack(side="right", fill="both", expand=True)

        self.blog_text = ctk.CTkTextbox(right, font=("Poppins", 16))
        self.blog_text.pack(fill="both", expand=True, padx=12, pady=12)

        self._refresh_blog_list()

    def _refresh_blog_list(self):
        for w in self.blog_list.winfo_children():
            w.destroy()

        os.makedirs("articles", exist_ok=True)
        files = sorted([f for f in os.listdir("articles") if f.endswith(".txt")], reverse=True)

        for f in files:
            ctk.CTkButton(
                self.blog_list,
                text=f.replace(".txt", ""),
                command=lambda name=f: self._open_article(os.path.join("articles", name))
            ).pack(fill="x", pady=5)

        if files:
            self._open_article(os.path.join("articles", files[0]))

    def _open_article(self, path):
        self.blog_text.delete("0.0", "end")
        try:
            with open(path, "r", encoding="utf-8") as f:
                self.blog_text.insert("end", f.read())
        except:
            self.blog_text.insert("end", "Erreur de lecture")

    def page_blog_create(self):
        self.clear_content()

        self.blog_title_entry = ctk.CTkEntry(self.content, placeholder_text="Titre")
        self.blog_title_entry.pack(pady=10)

        self.blog_body_text = ctk.CTkTextbox(self.content)
        self.blog_body_text.pack(fill="both", expand=True, padx=20, pady=10)

        ctk.CTkButton(
            self.content, text="Publier",
            command=self._save_blog_post
        ).pack(pady=10)

    def _save_blog_post(self):
        title = self.blog_title_entry.get().strip()
        body = self.blog_body_text.get("0.0", "end").strip()

        if not title or not body:
            return

        os.makedirs("articles", exist_ok=True)
        date = datetime.now().strftime("%Y-%m-%d")
        filename = f"{date}-{title.replace(' ', '-')}.txt"

        with open(os.path.join("articles", filename), "w", encoding="utf-8") as f:
            f.write(body)

        self.page_blog()
