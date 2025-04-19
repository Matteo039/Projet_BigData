from flask import Blueprint, jsonify, request, render_template, current_app
from models import get_data
from datetime import datetime, timedelta # Importer timedelta
from dateutil import parser

app_routes = Blueprint('app_routes', __name__)


@app_routes.route('/')
def index():
    return render_template('index.html')


@app_routes.route('/city', methods=['GET'])
def cities():
    available_cities = current_app.config['available_cities']
    selected_ville = request.args.get('ville')
    selected_date_debut_str = request.args.get('date_debut')
    selected_date_fin_str = request.args.get('date_fin')
    selected_intervalle = request.args.get('intervalle', 'heure') # Récupère l'intervalle choisi par l'utilisateur (défaut heure)

    error_message = None # Message pour les erreurs bloquantes (format date, date fin < date debut)
    info_message = None  # Message pour informer l'utilisateur d'un ajustement automatique
    show_graph = True    # Indique si le graphique doit être potentiellement affiché
    graph_data = []      # Initialiser graph_data comme une liste vide

    date_debut = None
    date_fin = None
    intervalle_for_query = selected_intervalle # L'intervalle réellement utilisé pour interroger la base de données

    # --- 1. Parsing et validation initiale des dates ---
    if selected_date_debut_str:
        try:
            date_debut = parser.parse(selected_date_debut_str)
            if selected_date_fin_str:
                date_fin = parser.parse(selected_date_fin_str)
            else:
                # Si pas de date de fin, on considère qu'il s'agit d'une seule journée
                date_fin = date_debut

            if date_fin < date_debut:
                error_message = "La date de fin doit être postérieure ou égale à la date de début."
                show_graph = False # Ne pas afficher le graphique en cas d'erreur grave

        except ValueError:
            error_message = "Format de date invalide. Veuillez utiliser un format reconnaissable (ex: YYYY-MM-DD ou DD/MM/YYYY)."
            show_graph = False # Ne pas afficher le graphique en cas d'erreur grave
    else:
        # Cas où aucune date de début n'a été sélectionnée.
        # On pourrait ajouter un message ici si on veut forcer la sélection d'une date.
        # Pour l'instant, on affiche juste rien (graph_data est vide, show_graph reste True par défaut
        # mais le template gère graph_data vide). On pourrait mettre show_graph = False ici aussi.
        pass # Pas de date sélectionnée, ne rien faire de spécial, le template gérera l'absence de données

    # --- 2. Logique d'ajustement automatique de l'intervalle (si pas d'erreur bloquante) ---
    if show_graph and selected_date_debut_str: # S'il n'y a pas d'erreur de date ET qu'au moins une date est sélectionnée
        if selected_intervalle == 'heure':
            # Calculer la durée en jours (incluant le jour de début et de fin)
            # Par exemple, du 1er au 7, c'est 7 jours. Du 1er au 8, c'est 8 jours.
            # La différence (date_fin - date_debut).days est 6 pour 7 jours, 7 pour 8 jours.
            # On veut switcher si la période est STRICTEMENT plus longue que 7 jours,
            # donc à partir de 8 jours inclus.
            # Différence de jours = 7 ou plus => période de 8 jours ou plus.
            duration_days = (date_fin - date_debut).days

            if duration_days >= 7: # Si la différence est de 7 jours ou plus (soit 8 jours ou plus dans la période)
                intervalle_for_query = 'jour' # Changer l'intervalle utilisé pour la requête à 'jour'
                info_message = "La période sélectionnée est supérieure à 7 jours. Les données sont affichées par 'Jour' pour une meilleure lisibilité."
                # Note: selected_intervalle conserve la valeur 'heure' pour que le bouton radio reste coché sur 'Heure'

    # --- 3. Récupérer les données (si pas d'erreur bloquante) ---
    if show_graph and selected_date_debut_str: # S'il n'y a pas d'erreur et qu'une date a été sélectionnée
         # Appel à get_data avec l'intervalle potentiellement ajusté
        graph_data = get_data(ville=selected_ville,
                               date_debut=selected_date_debut_str,
                               date_fin=selected_date_fin_str,
                               intervalle=intervalle_for_query)
        # get_data retournera [] si aucune donnée n'est trouvée ou si une erreur interne s'est produite.
        # Le template gérera le cas où graph_data est vide.
        if not graph_data:
             # Si get_data retourne vide, on pourrait vouloir ajouter un message spécifique,
             # mais le template gère déjà l'affichage "Aucune donnée trouvée".
             pass # Rien de spécifique à faire ici

    # --- 4. Renvoyer au template ---
    return render_template('city.html',
                           cities=available_cities,
                           ville=selected_ville,
                           graph_data=graph_data,
                           selected_date_debut=selected_date_debut_str, # Pass back the string values
                           selected_date_fin=selected_date_fin_str,     # Pass back the string values
                           selected_intervalle=selected_intervalle,     # Pass back the user's original selection
                           error_message=error_message,
                           info_message=info_message, # Pass the info message
                           show_graph=show_graph) # Control block display in template

@app_routes.route('/dataview', methods=['GET'])
def dataview():
    # Assurez-vous que les données de dataview sont chargées au démarrage
    # Utilisez .get avec une valeur par défaut sûre
    data = current_app.config.get('dataview_data', {'top_3_cities': [], 'bottom_3_cities': []})
    top_3_cities = data.get('top_3_cities', [])
    bottom_3_cities = data.get('bottom_3_cities', [])
    return render_template('dataview.html', top_3_cities=top_3_cities, bottom_3_cities=bottom_3_cities)

@app_routes.route('/about')
def a_propos():
    return render_template('aPropos.html')