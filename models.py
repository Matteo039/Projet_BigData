from pymongo import MongoClient, errors
from bson import ObjectId  # Importez ObjectId pour la conversion

# --- Configuration ---
MONGO_URI = "mongodb+srv://corentinpineau:eUUKxqRL2mQ3fcFq@villescluster.gb3tu.mongodb.net/?retryWrites=true&w=majority&appName=VillesCluster"
DATABASE_NAME = "VillesDB"  # Remplacez par le NOM DE VOTRE BASE
DATA_FOLDER = "villes"  # Plus besoin de cette variable ici

# --- Fonctions utilitaires ---

def get_mongo_client():
    """Retourne un client MongoDB connecté (ou None si erreur)."""
    try:
        client = MongoClient(MONGO_URI)
        client.admin.command('ping')  # Test de connexion
        print("Connecté à MongoDB")  # Message de succès (facultatif)
        return client
    except errors.ConnectionFailure:
        print("Erreur: Impossible de se connecter à MongoDB.")
        return None
    except Exception as e:
        print(f"Autre erreur MongoDB: {e}")
        return None

# --- Fonctions d'interaction avec MongoDB ---

def get_collections(client=None):
    """Retourne la LISTE DES NOMS de collections."""
    close_client = False  # Pour savoir si on doit fermer le client à la fin
    if client is None:  # Si aucun client n'est fourni
        client = get_mongo_client()  # On en crée un
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
        client = get_mongo_client()
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