from backend.users import login_user

success, result = login_user(
    email="coulifaezakirah@gmail.com",
    telephone="05494378"
)

if success:
    print("Connexion réussie !")
    print("Bienvenue",result["prenom"],result["nom"])
else:
    print("Erreur de connexion:",result)