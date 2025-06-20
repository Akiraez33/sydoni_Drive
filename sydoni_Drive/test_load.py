from backend.users import get_user_role

# Ce script est un exemple simple pour tester la fonction get_user_role du backend.
# Il simule une tentative de récupération du rôle d'un utilisateur par son email.

# Définir un email d'utilisateur pour le test
# Remplacez "toto.com" par un email d'utilisateur existant dans votre fichier users.json
# ou par un email non existant pour tester le cas d'erreur.
email_de_test = "toto.com"

# Appeler la fonction get_user_role du backend
# Cette fonction retourne un tuple: (succès_booléen, rôle_ou_message_erreur)
success, role_or_error_message = get_user_role(email_de_test)

# Afficher le résultat du test
if success:
    print(f"Rôle de l'utilisateur {email_de_test} : {role_or_error_message}")
else:
    print(f"Erreur lors de la récupération du rôle pour {email_de_test} : {role_or_error_message}")

# Exemples d'utilisation et de tests supplémentaires:
# 1. Tester avec un email qui existe et qui a un rôle défini.
# 2. Tester avec un email qui n'existe pas pour vérifier le message d'erreur.
# 3. Tester après avoir modifié le rôle d'un utilisateur via une autre fonction (ex: update_user_role).


