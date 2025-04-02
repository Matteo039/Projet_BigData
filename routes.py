from flask import Blueprint, jsonify, request, render_template
from models import get_data, get_available_cities

app_routes = Blueprint('app_routes', __name__)

@app_routes.route('/')
def index():
    return render_template('index.html')

@app_routes.route('/city', methods=['GET'])
def cities():
    available_cities = get_available_cities()
    selected_ville = request.args.get('ville')
<<<<<<< Updated upstream
    data = get_data(ville=selected_ville)  # Récupérer les données

    # Ajoute ces lignes pour le débogage
    for item in data:
        print("Item:", item)  # Affiche l'item actuel pour voir sa structure

    return render_template('city.html', cities=available_cities, ville=selected_ville, data=data)

@app_routes.route('/about')
def a_propos():
    return render_template('aPropos.html')

@app_routes.route('/data', methods=['GET'])
def get_all_data_route():
    try:
        data = get_data()
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
=======
    selected_date = request.args.get('date')  # Récupérer la date

    graph_data = get_data(ville=selected_ville, date=selected_date)  # Passer la date

    return render_template('city.html', cities=available_cities, ville=selected_ville, graph_data=graph_data, selected_date=selected_date)
>>>>>>> Stashed changes
