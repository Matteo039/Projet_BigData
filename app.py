from flask import Flask
from routes import app_routes  # Importez les routes depuis routes.py
import models  # Importez models.py pour les fonctions de traitement de données
import threading  # Pour la gestion des threads

# Créez l'application Flask
app = Flask(__name__)

# Enregistrez les routes
app.register_blueprint(app_routes)


if __name__ == '__main__':
    # Vérifiez si la base de données est accessible
    # models.get_mongo_client()  # Connexion à MongoDB
    # print(models.get_collections())  # Récupère les collections
    # print(models.get_data_from_collection('villes'))  # Récupère les données d'une collection
    # Lancer la tâche en arrière-plan
    threading.Thread(target=models.preload_data).start()
    app.run(debug=True)  # Activez le mode debug pour le développement