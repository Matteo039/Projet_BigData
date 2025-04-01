from flask import Flask
from routes import app_routes  # Importez les routes depuis routes.py
import models  # Importez models.py pour les fonctions de traitement de données

# Créez l'application Flask
app = Flask(__name__)

# Enregistrez les routes
app.register_blueprint(app_routes)


if __name__ == '__main__':
    # Vérifiez si la base de données est accessible
    client = models.get_mongo_client()
    
    #app.run(debug=True)  # Activez le mode debug pour le développement