import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import re
from interface_acc import MenuPrincipal
from utils import login, create_user



BRAND_GREEN = "#1E8449"
PRIMARY_BUTTON_COLOR = "#2ECC71"
HOVER_COLOR = "#27AE60"
SECONDARY_BUTTON_COLOR = "#A9DFBF"

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("green")

class WellBeingApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("WellBeing – Connexion")
        self.geometry("900x650")
        self.minsize(600, 450)

        # Dégradé
        self.bg_canvas = tk.Canvas(self, highlightthickness=0, bd=0)
        self.bg_canvas.pack(fill="both", expand=True)
        self.bg_canvas.bind("<Configure>", self._draw_gradient)

        # Container central
        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.place(relx=0.5, rely=0.5, anchor="center")

        self.afficher_login()

    # -------------------------------------------------------------------
    # DÉGRADÉ DE FOND
    # -------------------------------------------------------------------
    def _draw_gradient(self, event=None):
        self.bg_canvas.delete("grad")

        w = self.bg_canvas.winfo_width()
        h = self.bg_canvas.winfo_height()

        color1 = "#A8E6CF"
        color2 = "#1E8449"
        steps = 200

        r1, g1, b1 = self.winfo_rgb(color1)
        r2, g2, b2 = self.winfo_rgb(color2)

        for i in range(steps):
            r = int(r1 + (r2 - r1) * i / steps)
            g = int(g1 + (g2 - g1) * i / steps)
            b = int(b1 + (b2 - b1) * i / steps)
            color = f"#{r//256:02x}{g//256:02x}{b//256:02x}"

            y1 = int(i * h / steps)
            y2 = int((i + 1) * h / steps)

            self.bg_canvas.create_rectangle(
                0, y1, w, y2,
                outline="", fill=color, tags="grad"
            )

    # -------------------------------------------------------------------
    # CARTE CENTRALE
    # -------------------------------------------------------------------
    def _creer_carte_principale(self, titre_page):
        for widget in self.main_container.winfo_children():
            widget.destroy()

        frame = ctk.CTkFrame(
            self.main_container,
            corner_radius=20,
            fg_color="white",
            width=420,
            height=500
        )
        frame.pack()

        content = ctk.CTkFrame(frame, fg_color="transparent")
        content.pack(padx=30, pady=30)

        ctk.CTkLabel(
            content,
            text="🌱 WellBeing",
            font=ctk.CTkFont(size=36, weight="bold"),
            text_color=BRAND_GREEN
        ).pack()

        ctk.CTkLabel(
            content,
            text=titre_page,
            font=ctk.CTkFont(size=16),
            text_color="#6C7A89"
        ).pack(pady=(0, 25))

        return content

    # -------------------------------------------------------------------
    # PAGE LOGIN
    # -------------------------------------------------------------------
    def afficher_login(self):
        content = self._creer_carte_principale("Connexion à votre espace")

        self.email_login = ctk.CTkEntry(content, placeholder_text="Email", width=300, height=45)
        self.email_login.pack(pady=10)

        self.password_login = ctk.CTkEntry(content, placeholder_text="Mot de passe",
                                           show="*", width=300, height=45)
        self.password_login.pack(pady=10)

        self.email_login.focus()

        ctk.CTkButton(
            content,
            text="Se connecter",
            command=self.connecter,
            fg_color=PRIMARY_BUTTON_COLOR,
            hover_color=HOVER_COLOR,
            width=300,
            height=45
        ).pack(pady=15)

        ctk.CTkButton(
            content,
            text="Créer un compte",
            command=self.afficher_register,
            fg_color=SECONDARY_BUTTON_COLOR,
            hover_color="#9CD0A9",
            text_color=BRAND_GREEN,
            width=300,
            height=45
        ).pack()

    # -------------------------------------------------------------------
    # PAGE REGISTER
    # -------------------------------------------------------------------
    def afficher_register(self):
        content = self._creer_carte_principale("Créer un compte")

        self.email_register = ctk.CTkEntry(content, placeholder_text="Email", width=300, height=45)
        self.email_register.pack(pady=10)

        self.password_register = ctk.CTkEntry(content, placeholder_text="Mot de passe",
                                              show="*", width=300, height=45)
        self.password_register.pack(pady=10)

        ctk.CTkButton(
            content,
            text="Valider",
            command=self.creer_compte,
            fg_color=PRIMARY_BUTTON_COLOR,
            hover_color=HOVER_COLOR,
            width=300,
            height=45
        ).pack(pady=15)

        ctk.CTkButton(
            content,
            text="Retour",
            command=self.afficher_login,
            width=300,
            height=45
        ).pack()

    # -------------------------------------------------------------------
    # CONNEXION
    # -------------------------------------------------------------------
    def connecter(self):
        email = self.email_login.get().strip()
        password = self.password_login.get().strip()

        if not email or not password:
            messagebox.showerror("Erreur", "Veuillez remplir tous les champs.")
            return

        if len(email) > 30 or len(password) > 30:
            messagebox.showerror("Erreur", "Email (login) et mot de passe doivent faire 20 caractères maximum.")
            return

        user_id = login(email, password)

        if user_id:
            self.destroy()
            MenuPrincipal(user_id).mainloop()
        else:
            messagebox.showerror("Erreur", "Email ou mot de passe incorrect")

    # -------------------------------------------------------------------
    # INSCRIPTION
    # -------------------------------------------------------------------
    def creer_compte(self):
        email = self.email_register.get().strip()
        password = self.password_register.get().strip()

        if not email or not password:
            messagebox.showerror("Erreur", "Veuillez remplir tous les champs.")
            return

        if len(email) > 30:
            messagebox.showerror("Erreur", "Email (login) trop long (20 caractères max).")
            return

        if len(password) > 30:
            messagebox.showerror("Erreur", "Mot de passe trop long (20 caractères max).")
            return

        pattern = r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"
        if not re.match(pattern, email):
            messagebox.showerror("❌ Erreur", "Adresse email invalide.\nExemple : nom@gmail.com")
            return

        if len(password) < 5:
            messagebox.showerror("❌ Erreur", "Mot de passe trop court (min. 4 caractères).")
            return

        if create_user(email, password):
            messagebox.showinfo("✔️ Succès", "Compte créé ! Vous pouvez vous connecter.")
            self.afficher_login()
        else:
            messagebox.showerror("❌ Erreur", "Email déjà utilisé.")
