import customtkinter as ctk
from CTkMessagebox import CTkMessagebox
from utils import login, create_user
import interface_acc

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("green")


class WellBeingApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("WellBeing – Connexion")
        self.geometry("900x650")
        self.resizable(True, True)

        # Canvas du fond dégradé
        self.gradient = ctk.CTkCanvas(self, width=900, height=650, highlightthickness=0)
        self.gradient.pack(fill="both", expand=True)
        self.draw_gradient()

        self.afficher_login()

    def draw_gradient(self):
        """Dégradé vert vertical"""
        for i in range(650):
            r = max(0, min(255, 150 - int(i * 0.10)))
            g = max(0, min(255, 220 - int(i * 0.08)))
            b = max(0, min(255, 170 - int(i * 0.05)))
            color = f"#{r:02x}{g:02x}{b:02x}"
            self.gradient.create_line(0, i, 900, i, fill=color)


    # -----------------------------------
    # LOGIN PAGE
    # -----------------------------------
    def afficher_login(self):
        self.gradient.delete("all")
        self.draw_gradient()

        # Ombre
        shadow = ctk.CTkFrame(self,
                              corner_radius=25,
                              fg_color="#D0D0D0",
                              width=430,
                              height=510)
        shadow.place(relx=0.5, rely=0.5, anchor="center")

        # Carte
        frame = ctk.CTkFrame(self,
                             corner_radius=25,
                             fg_color="white",
                             width=420,
                             height=500)
        frame.place(relx=0.5, rely=0.5, anchor="center")

        # Titre
        ctk.CTkLabel(frame,
                     text="🌱 WellBeing",
                     font=("Poppins", 38, "bold"),
                     text_color="#1C3A2E").pack(pady=(30, 2))

        ctk.CTkLabel(frame,
                     text="Connexion à votre espace",
                     font=("Poppins", 18),
                     text_color="#4F705D").pack(pady=(0, 25))

        # Champs
        self.email_login = ctk.CTkEntry(frame,
                                        placeholder_text="Adresse email",
                                        height=45,
                                        width=300,
                                        corner_radius=12)
        self.email_login.pack(pady=10)

        self.password_login = ctk.CTkEntry(frame,
                                           placeholder_text="Mot de passe",
                                           show="*",
                                           height=45,
                                           width=300,
                                           corner_radius=12)
        self.password_login.pack(pady=10)

        # Boutons
        ctk.CTkButton(frame,
                      text="Se connecter",
                      command=self.connecter,
                      height=45,
                      width=300,
                      corner_radius=18,
                      fg_color="#3AA76D",
                      hover_color="#31965F").pack(pady=(25, 10))

        ctk.CTkButton(frame,
                      text="Créer un compte",
                      command=self.afficher_register,
                      height=45,
                      width=300,
                      corner_radius=18,
                      fg_color="#8BCF9F",
                      hover_color="#76BE8C").pack()


    # -----------------------------------
    # REGISTER PAGE
    # -----------------------------------
    def afficher_register(self):
        self.gradient.delete("all")
        self.draw_gradient()

        shadow = ctk.CTkFrame(self,
                              corner_radius=25,
                              fg_color="#00000022",
                              width=430,
                              height=510)
        shadow.place(relx=0.5, rely=0.5, anchor="center")

        frame = ctk.CTkFrame(self,
                             corner_radius=25,
                             fg_color="white",
                             width=420,
                             height=500)
        frame.place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(frame, text="🌱 WellBeing",
                     font=("Poppins", 38, "bold"),
                     text_color="#1C3A2E").pack(pady=(30, 2))

        ctk.CTkLabel(frame, text="Créer un compte",
                     font=("Poppins", 18),
                     text_color="#4F705D").pack(pady=(0, 25))

        self.email_register = ctk.CTkEntry(frame,
                                           placeholder_text="Adresse email",
                                           height=45,
                                           width=300,
                                           corner_radius=12)
        self.email_register.pack(pady=10)

        self.password_register = ctk.CTkEntry(frame,
                                              placeholder_text="Mot de passe",
                                              show="*",
                                              height=45,
                                              width=300,
                                              corner_radius=12)
        self.password_register.pack(pady=10)

        ctk.CTkButton(frame,
                      text="Valider",
                      command=self.creer_compte,
                      height=45,
                      width=300,
                      fg_color="#3AA76D",
                      hover_color="#2F8A58",
                      corner_radius=18).pack(pady=(25, 10))

        ctk.CTkButton(frame,
                      text="Retour",
                      command=self.afficher_login,
                      height=45,
                      width=300,
                      fg_color="#9BCFAE",
                      hover_color="#8ABF9D",
                      corner_radius=18).pack()


    def connecter(self):
        email = self.email_login.get()
        password = self.password_login.get()

        user_id = login(email, password)
        if user_id:
            self.destroy()
            interface_acc.MenuPrincipal(user_id).mainloop()
        else:
            CTkMessagebox(title="Erreur", message="Email ou mot de passe incorrect.")


    def creer_compte(self):
        email = self.email_register.get()
        password = self.password_register.get()

        if create_user(email, password):
            CTkMessagebox(title="Succès", message="Compte créé avec succès !")
            self.afficher_login()
        else:
            CTkMessagebox(title="Erreur", message="Cet email existe déjà.")



if __name__ == "__main__":
    app = WellBeingApp()
    app.mainloop()
