import customtkinter as ctk
from CTkMessagebox import CTkMessagebox
# Supposons que utils.py et interface_acc existent
from utils import login, create_user 
# import interface_acc 

# --- PARAMÈTRES GLOBAUX DU THÈME ---
# Couleurs personnalisées (Vert WellBeing)
BRAND_GREEN = "#1E8449"  # Vert foncé pour le texte
PRIMARY_BUTTON_COLOR = "#2ECC71"  # Vert vif pour l'action principale
HOVER_COLOR = "#27AE60"
SECONDARY_BUTTON_COLOR = "#A9DFBF"  # Vert très clair pour l'action secondaire

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("green") # Maintien du thème par défaut pour les widgets non stylisés

class WellBeingApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("WellBeing – Connexion")
        self.geometry("900x650")
        self.minsize(600, 450) # Ajout d'une taille minimale
        
        # Fond simple au lieu du dégradé en Canvas
        self.configure(fg_color="#F0F3F4") 
        
        # Conteneur principal pour toutes les cartes
        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.pack(fill="both", expand=True)

        self.afficher_login()

    # --- MÉTHODES DE DESIGN PARTAGÉES ---

    def _creer_carte_principale(self, titre_page):
        """ Crée le cadre de la carte centrale avec l'ombre et le titre. """
        
        # Nettoyer l'ancien contenu
        for widget in self.main_container.winfo_children():
            widget.destroy()

        shadow = ctk.CTkFrame(self.main_container,
                      corner_radius=25,
                      fg_color="#A0A0A0", # Remplacé par un gris uni
                      width=440,
                      height=520)

        # Carte principale (background blanc)
        frame = ctk.CTkFrame(self.main_container,
                             corner_radius=20,
                             fg_color="white",
                             width=420,
                             height=500,
                             border_width=1,
                             border_color="#E0E0E0") # Bordure très fine pour "pop"
        frame.place(relx=0.5, rely=0.5, anchor="center")
        
        # Conteneur de widgets pour utiliser .grid() ou .pack() à l'intérieur
        content_frame = ctk.CTkFrame(frame, fg_color="transparent")
        content_frame.pack(fill="both", padx=30, pady=30) # Padding global pour l'intérieur

        # Titre de l'application
        ctk.CTkLabel(content_frame,
                     text="🌱 WellBeing",
                     font=ctk.CTkFont(family="Arial", size=36, weight="bold"), # Police système
                     text_color=BRAND_GREEN).pack(pady=(0, 2))

        # Sous-titre
        ctk.CTkLabel(content_frame,
                     text=titre_page,
                     font=ctk.CTkFont(family="Arial", size=16),
                     text_color="#6C7A89").pack(pady=(0, 25))
                     
        return content_frame

    # -----------------------------------
    # LOGIN PAGE
    # -----------------------------------
    def afficher_login(self):
        content_frame = self._creer_carte_principale("Connexion à votre espace")

        # Champs
        self.email_login = ctk.CTkEntry(content_frame,
                                        placeholder_text="Adresse email",
                                        height=45,
                                        width=300,
                                        corner_radius=12,
                                        font=ctk.CTkFont(size=14))
        self.email_login.pack(pady=10)

        self.password_login = ctk.CTkEntry(content_frame,
                                           placeholder_text="Mot de passe",
                                           show="*",
                                           height=45,
                                           width=300,
                                           corner_radius=12,
                                           font=ctk.CTkFont(size=14))
        self.password_login.pack(pady=10)

        # Boutons
        ctk.CTkButton(content_frame,
                      text="Se connecter",
                      command=self.connecter,
                      height=45,
                      width=300,
                      corner_radius=18,
                      fg_color=PRIMARY_BUTTON_COLOR,
                      hover_color=HOVER_COLOR,
                      font=ctk.CTkFont(weight="bold", size=15)).pack(pady=(25, 10))

        ctk.CTkButton(content_frame,
                      text="Créer un compte",
                      command=self.afficher_register,
                      height=45,
                      width=300,
                      corner_radius=18,
                      fg_color=SECONDARY_BUTTON_COLOR,
                      hover_color="#9CD0A9",
                      text_color=BRAND_GREEN, # Texte vert foncé sur fond vert clair
                      font=ctk.CTkFont(size=15)).pack()


    # -----------------------------------
    # REGISTER PAGE
    # -----------------------------------
    def afficher_register(self):
        content_frame = self._creer_carte_principale("Créer un compte")

        self.email_register = ctk.CTkEntry(content_frame,
                                           placeholder_text="Adresse email",
                                           height=45,
                                           width=300,
                                           corner_radius=12,
                                           font=ctk.CTkFont(size=14))
        self.email_register.pack(pady=10)

        self.password_register = ctk.CTkEntry(content_frame,
                                              placeholder_text="Mot de passe",
                                              show="*",
                                              height=45,
                                              width=300,
                                              corner_radius=12,
                                              font=ctk.CTkFont(size=14))
        self.password_register.pack(pady=10)

        ctk.CTkButton(content_frame,
                      text="Valider et Se connecter",
                      command=self.creer_compte,
                      height=45,
                      width=300,
                      fg_color=PRIMARY_BUTTON_COLOR,
                      hover_color=HOVER_COLOR,
                      corner_radius=18,
                      font=ctk.CTkFont(weight="bold", size=15)).pack(pady=(25, 10))

        ctk.CTkButton(content_frame,
                      text="Retour à la connexion", # Texte plus explicite
                      command=self.afficher_login,
                      height=45,
                      width=300,
                      fg_color="#E8E8E8", # Bouton de retour gris
                      hover_color="#D0D0D0",
                      text_color="#4F705D",
                      corner_radius=18,
                      font=ctk.CTkFont(size=15)).pack()

    # --- LOGIQUE MÉTIER (INCHANGÉE) ---
    def connecter(self):
        email = self.email_login.get()
        password = self.password_login.get()

        user_id = login(email, password)
        if user_id:
            self.destroy()
            # interface_acc.MenuPrincipal(user_id).mainloop() # Décommenter si interface_acc est prêt
            print("Connexion réussie ! Passage à l'interface principale.")
        else:
            CTkMessagebox(title="Erreur", message="Email ou mot de passe incorrect.")


    def creer_compte(self):
        email = self.email_register.get()
        password = self.password_register.get()

        if create_user(email, password):
            CTkMessagebox(title="Succès", message="Compte créé avec succès ! Vous pouvez maintenant vous connecter.")
            self.afficher_login()
        else:
            CTkMessagebox(title="Erreur", message="Cet email existe déjà.")


if __name__ == "__main__":
    # La fonction 'login' et 'create_user' doit être définie ou mockée pour le test
    def login(email, password):
        # Mock de la fonction de connexion
        if email == "test@test.com" and password == "123":
            return 1 # ID Utilisateur
        return None

    def create_user(email, password):
        # Mock de la fonction de création
        if email == "existant@test.com":
            return False
        return True # Succès

    app = WellBeingApp()
    app.mainloop()


