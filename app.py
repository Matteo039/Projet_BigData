from flask import Flask
from routes import app_routes  # Importez les routes depuis routes.py

# Créez l'application Flask
app = Flask(__name__)

# Enregistrez les routes
app.register_blueprint(app_routes)


if __name__ == '__main__':
    app.run(debug=True)  # Activez le mode debug pour le développement