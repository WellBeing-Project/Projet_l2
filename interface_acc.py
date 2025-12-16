import customtkinter as ctk
from utils import get_db, calcul_score, add_history, analyze_image_with_ollama
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from tkinter import filedialog
from PIL import Image
import os
from datetime import datetime



class MenuPrincipal(ctk.CTk):

    def __init__(self, user_id):
        super().__init__()

        self.user_id = user_id
        self.title("WellBeing – Tableau de bord")
        self.geometry("1200x750")
        self.configure(fg_color="#F5F7F8")

        self.selected_image_path = None

        # Layout global
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # ------------------ SIDEBAR ------------------
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


        ctk.CTkButton(
            self.sidebar, text="Déconnexion",
            fg_color="#D9534F", hover_color="#B33A3A",
            command=self.destroy
        ).pack(pady=30, fill="x")

        # Contenu principal
        self.content = ctk.CTkFrame(self, corner_radius=20, fg_color="#FEF9E7")
        self.content.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)

        self.page_profil()

    # ------------------------------------------------------------
    def clear_content(self):
        for widget in self.content.winfo_children():
            widget.destroy()

    def _menu_btn(self, text, command):
        btn = ctk.CTkButton(
            self.sidebar, text=text,
            fg_color="#2ECC71", hover_color="#27AE60",
            height=45, corner_radius=12,
            command=command
        )
        btn.pack(fill="x", pady=8)

    # ============================================================
    # PAGE PROFIL
    # ============================================================
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
            ctk.CTkLabel(self.content, text=info,
                         font=("Poppins", 20), text_color="#555").pack(pady=5)

    # ============================================================
    # PAGE MODIFIER PROFIL
    # ============================================================
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
            gender = self.gender.get().strip()
            activity = self.activity.get().lower().strip()
            if activity not in ["faible", "moyenne", "élevée"]:
                return
        except:
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

    # ============================================================
    # PAGE SCORE + GRAPH
    # ============================================================
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

        score = calcul_score(w, h, a, act)

        # Système de couleur + smiley
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
                     font=("Poppins", 90), text_color=color).pack()

        ctk.CTkLabel(self.content, text=f"{score}/100",
                     font=("Poppins", 60, "bold"),
                     text_color=color).pack(pady=10)

        ctk.CTkLabel(self.content, text=msg,
                     font=("Poppins", 22), text_color="#555").pack(pady=5)

        # ------------------ GRAPHIQUE ------------------
        conn = get_db()
        cur = conn.cursor()
        cur.execute("""
            SELECT date, score FROM history
            WHERE user_id=%s ORDER BY date
        """, (self.user_id,))
        rows = cur.fetchall()
        conn.close()

        if len(rows) > 0:
            dates = [str(r[0]) for r in rows]
            scores = [r[1] for r in rows]

            bar_colors = [
                "#D9534F" if s < 40 else
                "#F39C12" if s < 60 else
                "#F4D03F" if s < 75 else
                "#2ECC71"
                for s in scores
            ]

            fig, ax = plt.subplots(figsize=(7, 3.8), dpi=100)
            ax.bar(dates, scores, color=bar_colors)
            ax.set_title("Historique du Score Santé")
            ax.set_ylim(0, 100)
            ax.tick_params(axis='x', rotation=45)
            fig.tight_layout()

            canvas = FigureCanvasTkAgg(fig, master=self.content)
            canvas.get_tk_widget().pack(pady=25)
            canvas.draw()

    # ============================================================
    # PAGE IA
    # ============================================================
    def page_ia(self):
        self.clear_content()

        ctk.CTkLabel(
            self.content, text="🤖 Analyse repas",
            font=("Poppins", 32, "bold"),
            text_color="#1E8449"
        ).pack(pady=20)

        ctk.CTkButton(
            self.content, text="📸 Choisir une image",
            fg_color="#2ECC71", hover_color="#27AE60",
            height=45, command=self._choose_image
        ).pack(pady=10)

        self.image_label = ctk.CTkLabel(self.content, text="")
        self.image_label.pack(pady=10)

        ctk.CTkButton(
            self.content, text="Analyser le repas",
            fg_color="#1F8EF1", hover_color="#1669B5",
            height=45, command=self._analyze_image
        ).pack(pady=15)

        self.response_label = ctk.CTkTextbox(
            self.content, width=700, height=260,
            font=("Poppins", 16),
            fg_color="#FEF9E7", corner_radius=12
        )
        self.response_label.pack(pady=20)

    # ============================================================
    # IA : CHOISIR IMAGE
    # ============================================================
    def _choose_image(self):
        file = filedialog.askopenfilename(
            filetypes=[("Images", "*.jpg *.jpeg *.png")]
        )
        if not file:
            return

        self.selected_image_path = "temp_resized.jpg"

        img = Image.open(file).convert("RGB")
        img = img.resize((384, 384))
        img.save(self.selected_image_path, "JPEG", quality=60)

        preview = ctk.CTkImage(Image.open(self.selected_image_path), size=(250, 250))
        self.image_label.configure(image=preview)
        self.image_label.image = preview

    # ============================================================
    # IA : ANALYSE IMAGE
    # ============================================================
    def _analyze_image(self):
        self.response_label.delete("0.0", "end")

        if not self.selected_image_path:
            self.response_label.insert("end", "⚠️ Aucune image sélectionnée.")
            return

        self.response_label.insert("end", "⏳ Analyse en cours...\n")

        data = analyze_image_with_ollama(self.selected_image_path)

        self.response_label.delete("0.0", "end")

        if not isinstance(data, dict) or "items" not in data:
            self.response_label.insert("end", "❌ Erreur IA.")
            return

        self.response_label.insert("end", "🍽️ Aliments détectés :\n\n")

        for item in data["items"]:
            color = item.get("color", "orange")
            ic = "🟢" if color == "vert" else ("🟠" if color == "orange" else "🔴")
            self.response_label.insert(
                "end", f"{ic} {item['name']} — {item['calories']} kcal\n"
            )

        total = data.get("total", 0)
        self.response_label.insert("end", f"\n🔥 Total : {total} calories\n\n")

        self.response_label.insert("end", f"💡 Conseil : {data.get('advice')}\n")

    def page_blog(self):
        self.clear_content()

        ctk.CTkLabel(
            self.content,
            text="📰 Blog santé",
            font=("Poppins", 30, "bold"),
            text_color="#1E8449"
        ).pack(pady=20)

        main = ctk.CTkFrame(self.content, fg_color="transparent")
        main.pack(fill="both", expand=True, padx=20, pady=10)

        # Colonne gauche (liste + bouton)
        left = ctk.CTkFrame(main, width=300, corner_radius=12, fg_color="#EAFAF1")
        left.pack(side="left", fill="y", padx=(0, 15))

        ctk.CTkButton(
            left,
            text="➕ Nouvel article",
            fg_color="#3498DB", hover_color="#2E86C1",
            command=self.page_blog_create
        ).pack(fill="x", padx=10, pady=(10, 6))

        self.blog_list = ctk.CTkScrollableFrame(left, fg_color="transparent")
        self.blog_list.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # Colonne droite (contenu)
        right = ctk.CTkFrame(main, corner_radius=12, fg_color="#FEF9E7")
        right.pack(side="right", fill="both", expand=True)

        self.blog_text = ctk.CTkTextbox(right, font=("Poppins", 16))
        self.blog_text.pack(fill="both", expand=True, padx=12, pady=12)

        self._refresh_blog_list()


    def _refresh_blog_list(self):
        # Vide la liste
        for w in self.blog_list.winfo_children():
            w.destroy()

        os.makedirs("articles", exist_ok=True)
        files = sorted([f for f in os.listdir("articles") if f.endswith(".txt")], reverse=True)

        if not files:
            self.blog_text.delete("0.0", "end")
            self.blog_text.insert("end", "Aucun article.\nClique sur ➕ Nouvel article pour en créer un.")
            return

        for f in files:
            ctk.CTkButton(
                self.blog_list,
                text=f.replace(".txt", ""),
                fg_color="#2ECC71", hover_color="#27AE60",
                command=lambda name=f: self._open_article(os.path.join("articles", name))
            ).pack(fill="x", pady=6)

        # Ouvre le plus récent
        self._open_article(os.path.join("articles", files[0]))

    def _open_article(self, path):
        self.blog_text.delete("0.0", "end")

        try:
            with open(path, "r", encoding="utf-8") as f:
                lines = f.readlines()

            # Suppression de "Titre:" et "Date:"
            title = lines[0].replace("Titre:", "").strip()
            date = lines[1].replace("Date:", "").strip()
            content = "".join(lines[3:])  # saute la ligne '---'

            # Affichage propre
            self.blog_text.insert("end", title + "\n", "title")
            self.blog_text.insert("end", date + "\n\n", "date")
            self.blog_text.insert("end", content)

            # Styles
            self.blog_text.tag_configure("title", font=("Poppins", 22, "bold"))
            self.blog_text.tag_configure("date", font=("Poppins", 12))

        except Exception:
            self.blog_text.insert("end", "❌ Impossible de lire l’article.")

    def page_blog_create(self):
        self.clear_content()

        ctk.CTkLabel(
            self.content,
            text="✍️ Créer un article",
            font=("Poppins", 30, "bold"),
            text_color="#1E8449"
        ).pack(pady=20)

        form = ctk.CTkFrame(self.content, corner_radius=12, fg_color="#EAFAF1")
        form.pack(fill="both", expand=True, padx=20, pady=10)

        ctk.CTkLabel(form, text="Titre", font=("Poppins", 16, "bold")).pack(anchor="w", padx=12, pady=(12, 4))
        self.blog_title_entry = ctk.CTkEntry(form, placeholder_text="Ex: 5 conseils pour mieux dormir")
        self.blog_title_entry.pack(fill="x", padx=12, pady=(0, 12))

        ctk.CTkLabel(form, text="Contenu", font=("Poppins", 16, "bold")).pack(anchor="w", padx=12, pady=(0, 4))
        self.blog_body_text = ctk.CTkTextbox(form, font=("Poppins", 14))
        self.blog_body_text.pack(fill="both", expand=True, padx=12, pady=(0, 12))

        btns = ctk.CTkFrame(form, fg_color="transparent")
        btns.pack(fill="x", padx=12, pady=(0, 12))

        ctk.CTkButton(
            btns,
            text="Publier",
            fg_color="#2ECC71", hover_color="#27AE60",
            command=self._save_blog_post
        ).pack(side="left")

        ctk.CTkButton(
            btns,
            text="Annuler",
            fg_color="#E74C3C", hover_color="#C0392B",
            command=self.page_blog
        ).pack(side="left", padx=10)

        self.blog_create_msg = ctk.CTkLabel(form, text="", font=("Poppins", 14))
        self.blog_create_msg.pack(anchor="w", padx=12, pady=(0, 12))


    def _save_blog_post(self):
        title = (self.blog_title_entry.get() or "").strip()
        body = (self.blog_body_text.get("0.0", "end") or "").strip()

        if not title or not body:
            self.blog_create_msg.configure(text="❌ Titre et contenu obligatoires.", text_color="#C0392B")
            return

        os.makedirs("articles", exist_ok=True)

        # Nom de fichier "safe"
        safe = "".join(c.lower() if c.isalnum() else "-" for c in title).strip("-")
        safe = "-".join([p for p in safe.split("-") if p])
        date_str = datetime.now().strftime("%Y-%m-%d")
        filename = f"{date_str}-{safe[:60]}.txt"

        path = os.path.join("articles", filename)
        content = f"Titre: {title}\nDate: {date_str}\n---\n{body}\n"

        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
            self.page_blog()          # retour blog
            self._refresh_blog_list() # recharge liste
        except Exception:
            self.blog_create_msg.configure(text="❌ Erreur lors de la sauvegarde.", text_color="#C0392B")



