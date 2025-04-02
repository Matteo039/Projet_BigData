from pymongo import MongoClient, errors
<<<<<<< Updated upstream
from bson import ObjectId
=======
from datetime import datetime
>>>>>>> Stashed changes

MONGO_URI = "mongodb+srv://corentinpineau:eUUKxqRL2mQ3fcFq@villescluster.gb3tu.mongodb.net/?retryWrites=true&w=majority&appName=VillesCluster"
DATABASE_NAME = "VillesDB"
COLLECTION_NAME = "villes"

<<<<<<< Updated upstream
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

def get_data(ville=None, limit=100):
    client = get_mongo_client()
    if not client:
        return []
=======
>>>>>>> Stashed changes

def get_mongo_client():
    try:
<<<<<<< Updated upstream
        db = client[DATABASE_NAME]
        collection = db[COLLECTION_NAME]

        query = {}
        if ville:
            query['Ville'] = ville

        data = list(collection.find(query).limit(limit))
        for document in data:
            document['_id'] = str(document['_id'])

        return data

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

def get_collections(client=None):
    close_client = False
    if client is None:
        client = get_mongo_client()
        if client is None:
            return []
        close_client = True

    try:
        db = client[DATABASE_NAME]
        return db.list_collection_names()
    except Exception as e:
        print(f"Erreur (liste collections): {e}")
        return []
    finally:
        if close_client and client:
            client.close()

def get_data_from_collection(collection_name, query={}, projection=None, limit=10, client=None):
    close_client = False
    if client is None:
        client = get_mongo_client()
        if client is None:
            return []
        close_client = True

    try:
        db = client[DATABASE_NAME]
        collection = db[collection_name]
        cursor = collection.find(query, projection)
        cursor = cursor.limit(limit)

        data = []
        for document in cursor:
            document['_id'] = str(document['_id'])
            data.append(document)
        return data
=======
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


def get_data(ville=None, date=None, limit=100):
    client = get_mongo_client()
    if not client:
        return []

    try:
        db = client[DATABASE_NAME]
        collection = db[COLLECTION_NAME]

        query = {}
        if ville:
            query['Ville'] = ville
        if date:
            # Convertir la date en objet datetime et formater pour la requête
            selected_date = datetime.strptime(date, '%Y-%m-%d')
            date_str = selected_date.strftime('%d/%m/%Y')  # Ajuste le format ici
            query['Début'] = {'$regex': f'^{date_str}'}  # Recherche la date au début de la chaîne

        data = list(collection.find(query).limit(limit))

        # Préparer les données pour le graphique
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
>>>>>>> Stashed changes

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