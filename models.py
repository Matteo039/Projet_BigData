from pymongo import MongoClient, errors
from bson import ObjectId  # Importez ObjectId pour la conversion

# --- Configuration ---
MONGO_URI = "mongodb+srv://corentinpineau:eUUKxqRL2mQ3fcFq@villescluster.gb3tu.mongodb.net/?retryWrites=true&w=majority&appName=VillesCluster"
DATABASE_NAME = "VillesDB"  # Remplacez par le NOM DE VOTRE BASE
COLLECTION_NAME = "villes"

# Connexion à MongoDB
client = MongoClient(MONGO_URI)
db = client[DATABASE_NAME]  # Accède à la base de données
collection = db[COLLECTION_NAME]  # Accède à la collection

# --- Fonctions d'interaction avec MongoDB ---

def get_data():
    """Récupère des données de la collection."""
    # IMPORTANT: Pour du Big Data, NE FAITES PAS list(collection.find()) sans filtre !
    # Utilisez un filtre, une projection, ou des agrégations.
    # Exemple avec filtre:
    # return list(collection.find({'champ': 'valeur'}))
    # return list(collection.find().limit(100)) # Limitez le nombre de résultats
    # Pour cet exemple de base, on renvoie juste les 100 premiers pour illustrer :
    data = list(collection.find().limit(100))
    client.close()  # Fermez la connexion
    return data

def insert_data(data):
    """Insère des données dans la collection."""
    if isinstance(data, list):
        collection.insert_many(data)  # Insère plusieurs documents
    else:
        collection.insert_one(data)   # Insère un seul document
    client.close()

def process_data(input_data):
    """Fonction de traitement des données (à implémenter)."""
    # C'est ici que vous mettrez votre logique de traitement (Pandas, Dask, PySpark).
    # ... (Voir les exemples de ma réponse précédente)
    # Exemple simple (qui ne fait rien) :
    client.close()
    return {'message': 'Traitement effectué (mais cette fonction ne fait rien pour l\'instant)', 'input': input_data}

def get_collections(client=None):
    """Retourne la LISTE DES NOMS de collections."""
    close_client = False  # Pour savoir si on doit fermer le client à la fin
    if client is None:  # Si aucun client n'est fourni
        if client is None:  # Si la connexion a échoué
            return []  # On retourne une liste vide
        close_client = True  # Il faudra fermer le client

    try:
        db = client[DATABASE_NAME]  # Accède à la base de données
        return db.list_collection_names()  # Retourne la liste des noms de collections
    except Exception as e:
        print(f"Erreur (liste collections): {e}")
        return []  # Retourne une liste vide en cas d'erreur
    finally:
        if close_client and client:  # Ferme le client si on l'a créé
            client.close()

def get_data_from_collection(collection_name, query={}, projection=None, limit=10, client=None):
    """Récupère les données d'UNE collection, avec conversion des ObjectId."""
    close_client = False
    if client is None:
        if client is None:
            return []
        close_client = True

    try:
        db = client[DATABASE_NAME]
        collection = db[collection_name]  # Accède à la collection SPÉCIFIQUE
        cursor = collection.find(query, projection)  # Exécute la requête
        cursor = cursor.limit(limit)  # Limite le nombre de résultats

        data = []
        for document in cursor:  # Itère sur les résultats
            document['_id'] = str(document['_id'])  # Convertit l'ObjectId en string
            data.append(document)  # Ajoute le document à la liste
        return data  # Retourne la liste des documents

    except errors.OperationFailure as e:
        print(f"Erreur (récupération): {e}")
        return []
    except Exception as e:
        print(f"Erreur inattendue: {e}")
        return []
    finally:
        if close_client and client:
            client.close()