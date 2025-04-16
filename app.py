from flask import Flask
from routes import app_routes
import models

app = Flask(__name__)

# Récupérer la liste des villes au démarrage de l'application
app.config['available_cities'] = models.get_available_cities()

# Récupérer les données pour dataview au démarrage
with app.app_context():
    top_3_cities, bottom_3_cities = models.get_data()
    app.config['dataview_data'] = {'top_3_cities': top_3_cities, 'bottom_3_cities': bottom_3_cities}

# Enregistrer le blueprint
app.register_blueprint(app_routes, url_prefix='/')

if __name__ == '__main__':
    models.get_mongo_client()
    app.run(debug=True)