from flask import Flask, render_template, request, jsonify
import requests
import json
from concurrent.futures import ThreadPoolExecutor
import time
import os
import hashlib

# Importar el módulo CRUD
import CRUD

app = Flask(__name__)
apikey = "b2968c04"

CACHE_DIR = "./cache"

# Create the cache directory if it doesn't exist/ esto es usado para evitar las mismas llamadas
if not os.path.exists(CACHE_DIR):
    os.makedirs(CACHE_DIR)

def cache_get(key):
    """Retrieve data from cache if available."""
    filepath = os.path.join(CACHE_DIR, f"{key}.json")
    if os.path.exists(filepath):
        with open(filepath, "r") as f:
            return json.load(f)
    return None

def cache_set(key, data):
    """Save data to cache."""
    filepath = os.path.join(CACHE_DIR, f"{key}.json")
    with open(filepath, "w") as f:
        json.dump(data, f)

def searchfilms(search_text):
    start_time = time.time()

    urls = [
        f"https://www.omdbapi.com/?s={search_text}&page=1&apikey={apikey}",
        f"https://www.omdbapi.com/?s={search_text}&page=2&apikey={apikey}",
        f"https://www.omdbapi.com/?s={search_text}&page=3&apikey={apikey}"
    ]
    
    with ThreadPoolExecutor() as executor:
        responses = list(executor.map(requests.get, urls))
    merch = [response.json() for response in responses if response.status_code == 200]
    
    end_time = time.time()
    print(f"searchfilms executed in {end_time - start_time:.2f} seconds")

    if merch:
        return merch
    else:
        print("Failed to retrieve search results.")
        return None

def getmoviedetails(movie):
    start_time = time.time()

    cache_key = hashlib.md5(movie["imdbID"].encode()).hexdigest()
    cached_data = cache_get(cache_key)
    
    if cached_data:
        print(f"getmoviedetails cache hit for {movie['Title']}")
        return cached_data

    url = "https://www.omdbapi.com/?i=" + movie["imdbID"] + "&apikey=" + apikey
    response = requests.get(url)
    if response.status_code == 200:
        result = response.json()
        cache_set(cache_key, result)
    else:
        print("Failed to retrieve movie details.")
        result = None

    end_time = time.time()
    print(f"getmoviedetails executed in {end_time - start_time:.2f} seconds")
    return result

def get_country_flag(fullname):
    start_time = time.time()

    cache_key = hashlib.md5(fullname.encode()).hexdigest()
    cached_flag = cache_get(cache_key)
    
    if cached_flag:
        print(f"get_country_flag cache hit for {fullname}")
        return cached_flag

    url = f"https://restcountries.com/v3.1/name/{fullname}?fullText=true"
    response = requests.get(url)
    if response.status_code == 200:
        country_data = response.json()
        flag = country_data[0].get("flags", {}).get("svg", None) if country_data else None
        cache_set(cache_key, flag)
    else:
        print(f"Failed to retrieve flag for country: {fullname}")
        flag = None

    end_time = time.time()
    print(f"get_country_flag executed in {end_time - start_time:.2f} seconds")
    return flag

def merge_data_with_flags(filter):
    start_time = time.time()
    filmssearch = searchfilms(filter)
    moviesdetailswithflags = []
    flag_cache = {}

    for a in filmssearch:
        for movie in a["Search"]:
            moviedetails = getmoviedetails(movie)  # details de movies
            countriesNames = moviedetails["Country"].split(",")
            countries = []

            movie_id = moviedetails["imdbID"]
            movie_title = moviedetails["Title"]
            movie_year = moviedetails["Year"]
            try:
                # Intenta crear la película en la base de datos
                CRUD.create_movie(movie_id, movie_title, f"Año: {movie_year}")
            except Exception as e:
                print(f"Error al crear la película: {e}")

            for country in countriesNames:
                country = country.strip()

                # Obtener la URL de la bandera
                if country in flag_cache:
                    flag = flag_cache[country]
                else:
                    flag = get_country_flag(country)
                    flag_cache[country] = flag

                # Comprobar si el país ya existe antes de crearlo
                if not CRUD.country_exists(country):
                    try:
                        CRUD.create_country(country, flag)
                    except Exception as e:
                        print(f"Error al crear el país: {e}")

                countrywithflag = {
                    "name": country,  # id de country
                    "flag": flag  # url de country
                }
                countries.append(countrywithflag)

            try:
                CRUD.create_movie_country(movie_id, ', '.join([c["name"] for c in countries]))
            except Exception as e:
                print(f"Error al crear la relación película-país: {e}")

            # Construir el resultado para la API
            moviewithflags = {
                "title": movie_title,
                "year": movie_year,
                "countries": countries
            }
            moviesdetailswithflags.append(moviewithflags)

    end_time = time.time()
    print(f"merge_data_with_flags executed in {end_time - start_time:.2f} seconds")
    return moviesdetailswithflags


@app.route("/")
def index():
    filter = request.args.get("filter", "").upper()
    return render_template("index.html", movies=merge_data_with_flags(filter))

@app.route("/api/movies")
def api_movies():
    filter = request.args.get("filter", "")
    return jsonify(merge_data_with_flags(filter))    

if __name__ == "__main__":
    app.run(debug=True)
