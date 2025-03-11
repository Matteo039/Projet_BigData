from flask import Blueprint, request, render_template
from models import get_collections, get_data_from_collection  # Importez les BONNES fonctions

app_routes = Blueprint('app_routes', __name__)

@app_routes.route('/')
def index():
    return render_template('index.html')  # Affiche la page d'accueil

@app_routes.route('/data', methods=['GET'])
def data_page():
    """Affiche le sélecteur de collection et les données."""
    collections = get_collections()  # Récupère la LISTE DES COLLECTIONS
    selected_collection = request.args.get('collection')  # Récupère la collection CHOISIE
    data = []

    if selected_collection:  # Si une collection est sélectionnée
        data = get_data_from_collection(selected_collection)  # Récupère les données de CETTE collection

    # Passe TOUTES les variables nécessaires au template
    return render_template('data.html', collections=collections, selected_collection=selected_collection, data=data)