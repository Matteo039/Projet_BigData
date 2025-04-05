from pymongo import MongoClient, errors
from datetime import datetime, timedelta

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


def get_data(ville=None, date_debut=None, date_fin=None, limit=100):
    client = get_mongo_client()
    if not client:
        return []

    try:
        db = client[DATABASE_NAME]
        collection = db[COLLECTION_NAME]

        query = {}
        if ville:
            query['Ville'] = ville

        if date_debut and date_fin:
            # Convertir les dates en objets datetime
            start_date = datetime.strptime(date_debut, '%Y-%m-%d')
            end_date = datetime.strptime(date_fin, '%Y-%m-%d')

            # Créer une liste de toutes les dates entre la date de début et la date de fin
            date_list = [start_date + timedelta(days=x) for x in range((end_date - start_date).days + 1)]

            # Préparer les données pour le graphique
            graph_data = {}  # Utiliser un dictionnaire pour stocker les moyennes par jour

            for date in date_list:
                date_str = date.strftime('%d/%m/%Y')
                daily_query = query.copy()  # Copier la requête de base
                daily_query['Début'] = {'$regex': f'^{date_str}'}

                daily_data = list(collection.find(daily_query).limit(limit))
                total_valeur = 0
                count = 0

                for item in daily_data:
                    try:
                        total_valeur += float(item['Valeur'])
                        count += 1
                    except (KeyError, ValueError) as e:
                        print(f"Erreur: Impossible d'extraire la valeur pour l'item {item}. Erreur: {e}")

                if count > 0:
                    moyenne = total_valeur / count
                    graph_data[date.strftime('%Y-%m-%d')] = moyenne  # Stocker la moyenne avec la date comme clé
                else:
                    graph_data[date.strftime('%Y-%m-%d')] = None  # Stocker None s'il n'y a pas de données

            # Convertir le dictionnaire en liste de tuples pour le graphique
            graph_data_list = list(graph_data.items())

            return graph_data_list

        elif date_debut:
            # Si seule la date de début est fournie
            start_date = datetime.strptime(date_debut, '%Y-%m-%d')
            date_str = start_date.strftime('%d/%m/%Y')
            query['Début'] = {'$regex': f'^{date_str}'}

            data = list(collection.find(query).limit(limit))

            graph_data = []
            for item in data:
                try:
                    heure = item['Début'].split(' ')[1]
                    valeur = item['Valeur']
                    graph_data.append((heure, valeur))
                except (KeyError, IndexError):
                    print(f"Erreur: Impossible d'extraire l'heure ou la valeur pour l'item {item}")

            # Trier les données par heure
            graph_data.sort(key=lambda x: x[0])

            return graph_data
        else:
            return []

    except Exception as e:
        print(f"Erreur lors de la récupération des données: {e}")
        return []
    finally:
        client.close()


def get_available_cities():
    client = get_mongo_client()
    if not client:
        print("Erreur : Impossible de se connecter à MongoDB dans get_available_cities().")
        return []

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