from flask import Flask
from routes import app_routes  # Importez les routes depuis routes.py
import models  # Importez les fonctions de models.py

# Créez l'application Flask
app = Flask(__name__)

# Enregistrez les routes
app.register_blueprint(app_routes)


if __name__ == '__main__':
    print(models.get_mongo_client())  # Testez la connexion MongoDB
    print(models.get_data())  # Testez la récupération de données
    app.run(debug=True)  # Activez le mode debug pour le développement
    
