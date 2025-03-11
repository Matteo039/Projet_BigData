from pymongo import MongoClient

# Configuration de la connexion MongoDB
MONGO_URI = "mongodb://localhost:27017/"  # Changez si nécessaire
DATABASE_NAME = "votre_base_de_donnees"  # Nom de votre base de données
COLLECTION_NAME = "votre_collection"  # Nom de votre collection

# Connexion au client MongoDB (faites-en une fonction pour la réutiliser)
def get_mongo_client():
    """Retourne un client MongoDB connecté."""
    return MongoClient(MONGO_URI)

# Fonctions d'interaction avec la base de données
def get_data():
    """Récupère des données de la collection."""
    client = get_mongo_client()
    db = client[DATABASE_NAME]
    collection = db[COLLECTION_NAME]
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
    client = get_mongo_client()
    db = client[DATABASE_NAME]
    collection = db[COLLECTION_NAME]
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
    client = get_mongo_client()
    client.close()
    return {'message': 'Traitement effectué (mais cette fonction ne fait rien pour l\'instant)', 'input': input_data}