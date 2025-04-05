from pymongo import MongoClient, errors
from datetime import datetime, timedelta
from dateutil import parser

MONGO_URI = "mongodb+srv://corentinpineau:eUUKxqRL2mQ3fcFq@villescluster.gb3tu.mongodb.net/?retryWrites=true&w=majority&appName=VillesCluster"
DATABASE_NAME = "VillesDB"
COLLECTION_NAME = "villes"


def get_mongo_client():
    try:
        client = MongoClient(MONGO_URI)
        client.admin.command('ping')
        print("Connecté à MongoDB")
        return client
    except errors.ConnectionFailure:
        print("Erreur: Impossible de se connecter à MongoDB.")
        return None
    except Exception as e:
        print(f"Autre erreur MongoDB: {e}")
        return None


def get_data(ville=None, date_debut=None, date_fin=None, intervalle='heure', limit=100):
    client = get_mongo_client()

    try:
        db = client[DATABASE_NAME]
        collection = db[COLLECTION_NAME]

        if ville or date_debut or date_fin:
            query = {}
            if ville:
                query['Ville'] = ville

            if date_debut and date_fin:
                try:
                    start_date = parser.parse(date_debut)
                    end_date = parser.parse(date_fin)
                except ValueError:
                    print("Format de date invalide. Utilisez un format reconnaissable.")
                    return []

                # Préparer les données pour le graphique
                graph_data = {}  # Utiliser un dictionnaire pour stocker les moyennes par intervalle
                date_list = [start_date + timedelta(days=x) for x in range((end_date - start_date).days + 1)]

                for date in date_list:
                    if intervalle == 'heure':
                        for hour in range(24):
                            date_time_str = date.strftime('%d/%m/%Y') + f' {hour:02d}:00'
                            daily_query = query.copy()
                            daily_query['Début'] = {'$regex': f'^{date_time_str}'}
                            total_valeur, count = calculate_average(collection, daily_query, limit)
                            graph_data[date_time_str] = total_valeur / count if count > 0 else None

                    elif intervalle == 'jour':
                        date_str = date.strftime('%d/%m/%Y')
                        daily_query = query.copy()
                        daily_query['Début'] = {'$regex': f'^{date_str}'}
                        total_valeur, count = calculate_average(collection, daily_query, limit)
                        graph_data[date.strftime('%Y-%m-%d')] = total_valeur / count if count > 0 else None

                    elif intervalle == 'mois':
                        date_str = date.strftime('%m/%Y')
                        monthly_query = query.copy()
                        monthly_query['Début'] = {'$regex': f'.*/{date_str}'}  # Regex pour le mois
                        total_valeur, count = calculate_average(collection, monthly_query, limit)
                        graph_data[date.strftime('%Y-%m')] = total_valeur / count if count > 0 else None

                # Convertir le dictionnaire en liste de tuples pour le graphique
                graph_data_list = list(graph_data.items())
                return graph_data_list

            else:
                try:
                    start_date = parser.parse(date_debut)
                except ValueError:
                    print("Format de date invalide. Utilisez un format reconnaissable.")
                    return []

                # Préparer les données pour le graphique
                graph_data = {}  # Utiliser un dictionnaire pour stocker les moyennes par heure

                for hour in range(24):
                    date_time_str = start_date.strftime('%d/%m/%Y') + f' {hour:02d}:00'
                    daily_query = query.copy()
                    daily_query['Début'] = {'$regex': f'^{date_time_str}'}
                    total_valeur, count = calculate_average(collection, daily_query, limit)
                    graph_data[date_time_str] = total_valeur / count if count > 0 else None
                # Convertir le dictionnaire en liste de tuples pour le graphique
                graph_data_list = list(graph_data.items())
                return graph_data_list

            # Trier les données par heure (conversion en nombre)
            # graph_data.sort(key=lambda x: int(x[0].split(':')[0]))

            return graph_data
        else:
            # Si aucune date n'est fournie, récupérer les 3 pires et les 3 meilleures villes pour le 31 décembre 2024
            date = "2024-12-31"
            selected_date = parser.parse(date)
            date_str = selected_date.strftime('%d/%m/%Y')

            # Récupérer toutes les villes distinctes
            cities = get_available_cities()

            city_data = {}  # Dictionnaire pour stocker les données de chaque ville
            for ville in cities:
                query = {'Ville': ville, 'Début': {'$regex': f'^{date_str}'}}
                data = list(collection.find(query).limit(limit))
                total_valeur = 0
                count = 0

                for item in data:
                    try:
                        total_valeur += float(item['Valeur'])
                        count += 1
                    except (KeyError, ValueError) as e:
                        print(f"Erreur: Impossible d'extraire la valeur pour l'item {item}. Erreur: {e}")

                if count > 0:
                    moyenne = total_valeur / count
                    city_data[ville] = moyenne
                else:
                    city_data[ville] = None

            # Trier les villes en fonction de leur valeur moyenne
            city_data = {ville: valeur for ville, valeur in city_data.items() if valeur is not None}
            sorted_cities = sorted(city_data.items(), key=lambda x: x[1], reverse=True)

            # Récupérer les 3 pires et les 3 meilleures villes
            top_3_cities = sorted_cities[:3]
            bottom_3_cities = sorted_cities[-3:]

            return top_3_cities, bottom_3_cities

    except Exception as e:
        print(f"Erreur lors de la récupération des données: {e}")
        return [], []

    finally:
        client.close()


def calculate_average(collection, query, limit):
    data = list(collection.find(query).limit(limit))
    total_valeur = 0
    count = 0

    for item in data:
        try:
            total_valeur += float(item['Valeur'])
            count += 1
        except (KeyError, ValueError) as e:
            print(f"Erreur: Impossible d'extraire la valeur pour l'item {item}. Erreur: {e}")
    return total_valeur, count


def get_available_cities():
    client = get_mongo_client()

    try:
        db = client[DATABASE_NAME]
        collection = db[COLLECTION_NAME]
        cities = collection.distinct("Ville")
        print(f"Villes récupérées depuis MongoDB : {cities}")
        return cities

    except Exception as e:
        print(f"Erreur lors de la récupération des villes: {e}")
        return []
    finally:
        if client:
            client.close()