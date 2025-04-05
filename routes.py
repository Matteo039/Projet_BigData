from flask import Blueprint, jsonify, request, render_template
from models import get_data, get_available_cities
from datetime import datetime

app_routes = Blueprint('app_routes', __name__)


@app_routes.route('/')
def index():
    return render_template('index.html')


@app_routes.route('/city', methods=['GET'])
def cities():
    available_cities = get_available_cities()
    selected_ville = request.args.get('ville')
    selected_date_debut = request.args.get('date_debut')
    selected_date_fin = request.args.get('date_fin')
    error_message = None
    show_graph = True
    graph_data = None

    if selected_date_debut and selected_date_fin:
        try:
            date_debut = datetime.strptime(selected_date_debut, '%Y-%m-%d')
            date_fin = datetime.strptime(selected_date_fin, '%Y-%m-%d')

            if date_fin < date_debut:
                error_message = "La date de fin doit être postérieure ou égale à la date de début."
                graph_data = []
                show_graph = False
            else:
                graph_data = get_data(ville=selected_ville, date_debut=selected_date_debut, date_fin=selected_date_fin)
        except ValueError:
            error_message = "Format de date invalide. Veuillez utiliser AAAA-MM-JJ."
            graph_data = []
            show_graph = False
    else:
        graph_data = get_data(ville=selected_ville, date_debut=selected_date_debut, date_fin=selected_date_fin)

    return render_template('city.html',
                           cities=available_cities,
                           ville=selected_ville,
                           graph_data=graph_data,
                           selected_date_debut=selected_date_debut,
                           selected_date_fin=selected_date_fin,
                           error_message=error_message,
                           show_graph=show_graph)


@app_routes.route('/dataview', methods=['GET'])
def dataview():
    top_3_cities, bottom_3_cities = get_data()
    return render_template('dataview.html', top_3_cities=top_3_cities, bottom_3_cities=bottom_3_cities)