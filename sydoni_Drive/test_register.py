from backend.users import register_user

#Simulation d'un enregistrement
success, message = register_user(
    nom="COULIBALY",
    prenom="Faez",
    telephone="05494378",
    email="coulifaezakirah@gmail.com",
    universite="Universiter bit",
    role="automobiliste"
)

print(message)