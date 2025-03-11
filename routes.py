from flask import Blueprint, jsonify, request, render_template
# Si vous utilisez models.py:
from models import get_data, insert_data, process_data  # Importez les fonctions

# Créez un Blueprint pour organiser les routes
app_routes = Blueprint('app_routes', __name__)

@app_routes.route('/')
def index():
    """Route principale (page d'accueil)."""
    return render_template('index.html')  # Si vous avez un template
    # return "Bienvenue dans votre application de traitement de données!"


@app_routes.route('/data', methods=['GET'])
def get_all_data_route():
    """Récupère toutes les données."""
    try:
        data = get_data()
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app_routes.route('/data', methods=['POST'])
def add_data_route():
    """Ajoute des données."""
    try:
        data = request.get_json()
        insert_data(data)
        return jsonify({'message': 'Données ajoutées avec succès'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app_routes.route('/process', methods=['POST'])
def process_data_route():
    """Route pour le traitement des données."""
    try:
        input_data = request.get_json()  # ou request.form, si vous envoyez des données de formulaire
        results = process_data(input_data) # Appel de votre fonction de models.py
        return jsonify(results)
    except Exception as e:
        return jsonify({'error': str(e)}), 500