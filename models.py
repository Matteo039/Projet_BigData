from pymongo import MongoClient, errors
from datetime import datetime, timedelta
from dateutil import parser

MONGO_URI = "mongodb+srv://corentinpineau:eUUKxqRL2mQ3fcFq@villescluster.gb3tu.mongodb.net/?retryWrites=true&w=majority&appName=VillesCluster"
DATABASE_NAME = "VillesDB"
COLLECTION_NAME = "villes"


def get_mongo_client():
    try:
        # Added serverSelectionTimeoutMS to avoid infinite hangs on connection issues
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        # The ismaster command is cheap and does not require auth.
        client.admin.command('ping')
        print("Connecté à MongoDB")
        return client
    except errors.ConnectionFailure as e:
        print(f"Erreur de connexion à MongoDB: {e}")
        return None
    except Exception as e:
        print(f"Autre erreur MongoDB lors de la connexion: {e}")
        return None


def calculate_average(collection, query, limit):
    """
    Calculates the total value and count for documents matching a query.
    Handles missing 'Valeur' key, 'valeur' key variation, and quality codes 'N'.
    """
    data = list(collection.find(query).limit(limit))
    total_valeur = 0
    count = 0
    skipped_count = 0 # Optional: Track how many items are skipped

    for item in data:
        # Check for invalid quality codes ('N') - handle both key variations
        quality_code_capital = item.get('CodeQualité')
        quality_code_lower = item.get('code qualité')

        if quality_code_capital == 'N' or quality_code_lower == 'N':
            # Skip items with 'N' quality code
            skipped_count += 1
            # print(f"Skipping item due to quality code 'N': {item}") # Optional: Log skipped items
            continue

        # Try to get the value using either 'Valeur' or 'valeur' key
        value = item.get('Valeur')
        if value is None:
            value = item.get('valeur')

        if value is not None and value != '': # Also check for empty string
            try:
                total_valeur += float(value)
                count += 1
            except ValueError as e:
                # Log specific error for non-numeric values
                print(f"Erreur: Impossible de convertir la valeur '{value}' en flottant pour l'item {item}. Erreur: {e}")
                skipped_count += 1 # Count non-numeric values as skipped
            # No need for KeyError here because we used .get()
        else:
            # Log specific error for missing value key after checking both variations
            # print(f"Skipping item due to missing or empty 'Valeur'/'valeur': {item}") # Optional: Log skipped items
            skipped_count += 1


    # print(f"Processed {len(data)} items, skipped {skipped_count}. Counted {count} valid items.") # Optional: summary log
    return total_valeur, count


def get_data(ville=None, date_debut=None, date_fin=None, intervalle='heure', limit=100):
    client = get_mongo_client()
    if not client:
        return ([], []) if not ville and not date_debut else [] # Return appropriate empty type

    try:
        db = client[DATABASE_NAME]
        collection = db[COLLECTION_NAME]

        if ville or date_debut or date_fin:
            query = {}
            if ville:
                query['Ville'] = ville

            # --- Logic for specific date/date range queries (used by /city) ---
            if date_debut: # Simplified logic, assuming at least date_debut is provided for this path
                try:
                    start_date = parser.parse(date_debut)
                    # If date_fin is not provided, set it to the start date for daily/hourly
                    if date_fin:
                         end_date = parser.parse(date_fin)
                    else:
                         end_date = start_date # For single day view

                    if end_date < start_date:
                         print("Erreur: La date de fin doit être postérieure ou égale à la date de début.")
                         return []

                except ValueError:
                    print("Format de date invalide. Utilisez un format reconnaissable (YYYY-MM-DD ou DD/MM/YYYY).")
                    return []

                graph_data = {} # Use a dictionary for easier date/time keying

                current_date = start_date
                # Loop through dates from start_date to end_date
                while current_date <= end_date:
                    if intervalle == 'heure' and current_date == start_date and start_date == end_date:
                         # Specific case: single day hourly view
                         for hour in range(24):
                            # Construct regex for a specific hour on a specific date
                            date_time_str_query = current_date.strftime('%d/%m/%Y') + f' {hour:02d}:00'
                            hourly_query = query.copy()
                            # Using regex for exact start time match
                            hourly_query['Début'] = date_time_str_query # Exact match is better than regex here

                            # Use calculate_average
                            total_valeur, count = calculate_average(collection, hourly_query, limit)
                            # Store result in graph_data, key is the full date time string
                            graph_data[date_time_str_query] = total_valeur / count if count > 0 else None

                    elif intervalle == 'jour':
                        # Construct regex for a specific day
                        date_str_query = current_date.strftime('%d/%m/%Y')
                        daily_query = query.copy()
                        daily_query['Début'] = {'$regex': f'^{date_str_query}'} # Regex to match start of string

                        # Use calculate_average
                        total_valeur, count = calculate_average(collection, daily_query, limit)
                        # Store result, key is YYYY-MM-DD for consistent sorting in chart
                        graph_data[current_date.strftime('%Y-%m-%d')] = total_valeur / count if count > 0 else None

                    elif intervalle == 'mois':
                         # Calculate average for the *current_date*'s month (only once per month in the loop)
                         month_key = current_date.strftime('%Y-%m')
                         if month_key not in graph_data: # Ensure we process each month only once
                            date_str_query = current_date.strftime('%m/%Y')
                            monthly_query = query.copy()
                            monthly_query['Début'] = {'$regex': f'/{date_str_query}'} # Regex to match MM/YYYY anywhere in string

                            # Use calculate_average
                            total_valeur, count = calculate_average(collection, monthly_query, limit)
                            # Store result, key is YYYY-MM
                            graph_data[month_key] = total_valeur / count if count > 0 else None

                    # Move to the next interval based on the chosen interval
                    if intervalle == 'heure' and current_date == start_date and start_date == end_date:
                         # For single day hourly, the loop through dates is just the start date, hours are handled inside
                         current_date += timedelta(days=1) # Exit after processing the day
                    elif intervalle == 'jour':
                         current_date += timedelta(days=1)
                    elif intervalle == 'mois':
                         # Move to the first day of the *next* month
                         # This prevents processing the same month multiple times
                         if current_date.month == 12:
                              current_date = current_date.replace(year=current_date.year + 1, month=1, day=1)
                         else:
                              current_date = current_date.replace(month=current_date.month + 1, day=1)
                    else: # Fallback, should not happen if intervalle is handled above
                         break # Exit loop if intervalle is unknown


                # Convert the dictionary to a list of tuples for the graph
                # Sort by key (which are formatted dates/times)
                graph_data_list = sorted(graph_data.items())

                return graph_data_list

            else:
                 # This block should ideally not be reached if date_debut is checked above
                 # Added a print/return to avoid unexpected behavior
                 print("Error: get_data called with ville but no date_debut.")
                 return []


        else:
            # --- Logic for Dataview (used by /dataview) ---
            # If no filters provided, calculate top/bottom 3 for a fixed date
            date_str_dataview = "31/12/2024" # Using the fixed date from the original code

            # Récupérer toutes les villes distinctes
            cities = get_available_cities(client) # Pass client to avoid reconnecting

            city_data = {}  # Dictionnaire pour stocker les données de chaque ville
            for ville in cities:
                if ville is None: # Skip None entries if they somehow appear in distinct
                    continue
                query = {'Ville': ville, 'Début': {'$regex': f'^{date_str_dataview}'}}

                # Use calculate_average here too
                total_valeur, count = calculate_average(collection, query, limit)

                if count > 0:
                    moyenne = total_valeur / count
                    city_data[ville] = moyenne
                else:
                    # If no data or only invalid data, don't include the city or set value to None/0
                    # Setting to None means it won't be included in sorted_cities by the filter below
                    city_data[ville] = None


            # Filter out cities with no valid data and sort
            city_data = {ville: valeur for ville, valeur in city_data.items() if valeur is not None}
            sorted_cities = sorted(city_data.items(), key=lambda x: x[1], reverse=True)

            # Récupérer les 3 pires et les 3 meilleures villes
            # Ensure we don't try to slice more items than exist
            top_3_cities = sorted_cities[:min(3, len(sorted_cities))]
            bottom_3_cities = sorted_cities[-min(3, len(sorted_cities)):] # Slices from the end

            # Ensure we handle cases with very few cities
            if len(sorted_cities) <= 3:
                 # If 3 or fewer cities, top 3 and bottom 3 might overlap or be the same
                 # Depending on desired behavior, you might adjust this.
                 # For now, keep the slicing, it will return all cities for both lists if <= 3
                 pass


            return top_3_cities, bottom_3_cities

    except Exception as e:
        print(f"Erreur générale lors de la récupération des données: {e}")
        # Return appropriate empty type based on context
        return ([], []) if not ville and not date_debut else []

    finally:
        # Ensure client is closed only if it was successfully created
        if client:
            client.close()


# Modified get_available_cities to optionally accept a client
def get_available_cities(client=None):
    # Use the provided client if available, otherwise create a new one
    if client is None:
        client_to_close = get_mongo_client()
        if not client_to_close:
             return []
        client = client_to_close
    else:
        client_to_close = None # Don't close the client passed from get_data

    try:
        db = client[DATABASE_NAME]
        collection = db[COLLECTION_NAME]
        cities = collection.distinct("Ville")
        # Filter out None values from the distinct list if any exist
        cities = [city for city in cities if city is not None]
        print(f"Villes récupérées depuis MongoDB : {cities}")
        return cities

    except Exception as e:
        print(f"Erreur lors de la récupération des villes: {e}")
        return []
    finally:
        # Only close the client if it was created *inside* this function
        if client_to_close:
            client_to_close.close()