import pymongo
import pandas as pd
import os
import re
 
# --- Configuration ---
MONGO_URI = "mongodb+srv://corentinpineau:eUUKxqRL2mQ3fcFq@villescluster.gb3tu.mongodb.net/?retryWrites=true&w=majority&appName=VillesCluster"
DATABASE_NAME = "VillesDB"  # Remplacez par le NOM DE VOTRE BASE
DATA_FOLDER = "villes"  # Plus besoin de cette variable ici
 
def clean_column_name(name):
    """Nettoie un nom de colonne (pour MongoDB)."""
    name = name.strip().lower()
    name = re.sub(r'[^a-zA-Z0-9_]', '_', name)
    name = re.sub(r'__+', '_', name)
    return name
 
def import_csv_to_mongodb(csv_filepath, collection_name, mongo_uri=MONGO_URI, db_name=DATABASE_NAME):
    """Importe un CSV dans une collection MongoDB."""
    try:
        client = pymongo.MongoClient(mongo_uri)
        db = client[db_name]
        df = pd.read_csv(csv_filepath, encoding='latin-1', sep=';', decimal=',')
        df.columns = [clean_column_name(col) for col in df.columns]
        data = df.to_dict('records')
        collection = db[collection_name]
        collection.insert_many(data)
        print(f"Données de {csv_filepath} -> collection {collection_name}")  # Message clair
 
    except Exception as e:  # Capture TOUTES les erreurs
        print(f"ERREUR avec {csv_filepath}: {e}")  # Affiche l'erreur
    finally:
        if 'client' in locals() and client:
            client.close()
 
def main():
    """Importe TOUS les CSV du dossier data."""
    if not os.path.exists(DATA_FOLDER):
        print(f"ERREUR: Dossier '{DATA_FOLDER}' introuvable.")
        return
 
    for filename in os.listdir(DATA_FOLDER):
        if filename.endswith(".csv"):
            csv_filepath = os.path.join(DATA_FOLDER, filename)
            collection_name = filename[:-4]  # Nom de la collection = nom du fichier
            collection_name = clean_column_name(collection_name) #Nettoie le nom de la collection
            import_csv_to_mongodb(csv_filepath, collection_name)
 
if __name__ == "__main__":
    main()