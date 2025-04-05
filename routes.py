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
    selected_date = request.args.get('date')  # Récupérer la date

    graph_data = get_data(ville=selected_ville, date=selected_date)  # Passer la date

    return render_template('city.html', cities=available_cities, ville=selected_ville, graph_data=graph_data, selected_date=selected_date)