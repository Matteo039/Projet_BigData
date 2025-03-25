from flask import Flask
from routes import app_routes
import models

app = Flask(__name__)
app.register_blueprint(app_routes)

if __name__ == '__main__':
    models.get_mongo_client()  # Connexion à MongoDB
    print(models.get_collections())  # Récupère les collections
    print(models.get_data_from_collection('villes'))  # Récupère les données d'une collection
    #app.run(debug=True)