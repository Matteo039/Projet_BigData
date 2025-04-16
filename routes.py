from flask import Blueprint, jsonify, request, render_template, current_app
from models import get_data
from datetime import datetime
from dateutil import parser

app_routes = Blueprint('app_routes', __name__)


@app_routes.route('/')
def index():
    return render_template('index.html')


@app_routes.route('/city', methods=['GET'])
def cities():
    available_cities = current_app.config['available_cities']
    selected_ville = request.args.get('ville')
    selected_date_debut = request.args.get('date_debut')
    selected_date_fin = request.args.get('date_fin')
    selected_intervalle = request.args.get('intervalle')  # Récupérer l'intervalle
    error_message = None
    show_graph = True
    graph_data = None  # Assurez-vous que graph_data est initialisé

    if selected_date_debut and selected_date_fin:
        try:
            date_debut = parser.parse(selected_date_debut)
            date_fin = parser.parse(selected_date_fin)
            if date_fin < date_debut:
                error_message = "La date de fin doit être postérieure ou égale à la date de début."
                graph_data = []
                show_graph = False
            else:
                graph_data = get_data(ville=selected_ville, date_debut=selected_date_debut, date_fin=selected_date_fin, intervalle=selected_intervalle)
        except ValueError:
            error_message = "Format de date invalide. Veuillez utiliser un format reconnaissable."
            graph_data = []
            show_graph = False
    else:
        graph_data = get_data(ville=selected_ville, date_debut=selected_date_debut, date_fin=selected_date_fin, intervalle=selected_intervalle)

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
    data = current_app.config['dataview_data']
    top_3_cities = data['top_3_cities']
    bottom_3_cities = data['bottom_3_cities']
    return render_template('dataview.html', top_3_cities=top_3_cities, bottom_3_cities=bottom_3_cities)

@app_routes.route('/about')
def a_propos():
    return render_template('aPropos.html')