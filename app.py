from flask import Flask, render_template, request, jsonify
import requests
import json

app = Flask(__name__)
apikey = "b2968c04"

def searchfilms(search_text):
    url = "https://www.omdbapi.com/?s=" + search_text + "&page=1"+"&apikey=" + apikey
    url2 = "https://www.omdbapi.com/?s=" + search_text + "&page=2"+"&apikey=" + apikey
    url3 = "https://www.omdbapi.com/?s=" + search_text + "&page=3"+"&apikey=" + apikey
    response = requests.get(url)
    response2 = requests.get(url2)
    response3 = requests.get(url3)
    merch=[response.json(),response2.json(),response3.json()]
    
    if response.status_code == 200:
        return merch
    else:
        print("Failed to retrieve search results.")
        return None
    
def getmoviedetails(movie):
    url = "https://www.omdbapi.com/?i=" + movie["imdbID"] + "&apikey=" + apikey
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print("Failed to retrieve search results.")
        return None

def get_country_flag(fullname):
    url = f"https://restcountries.com/v3.1/name/{fullname}?fullText=true"
    response = requests.get(url)
    if response.status_code == 200:
        country_data = response.json()
        if country_data:
            return country_data[0].get("flags", {}).get("svg", None)
    print(f"Failed to retrieve flag for country code: {fullname}")
    return None

def merge_data_with_flags(filter):
    filmssearch = searchfilms(filter)
    moviesdetailswithflags = []
    

    for a in filmssearch:
        for movie in a["Search"]:
            moviedetails = getmoviedetails(movie)
            countriesNames = moviedetails["Country"].split(",")
            countries = []
            for country in countriesNames:
                countrywithflag = {
                    "name": country.strip(),
                    "flag": get_country_flag(country.strip())
                }
                countries.append(countrywithflag)
            moviewithflags = {
                "title": moviedetails["Title"],
                "year": moviedetails["Year"],
                "countries": countries
            }
            moviesdetailswithflags.append(moviewithflags)

    return moviesdetailswithflags

@app.route("/")
def index():
    filter = request.args.get("filter", "").upper()
    return render_template("index.html", movies = merge_data_with_flags(filter))

@app.route("/api/movies")
def api_movies():
    filter = request.args.get("filter", "")
    return jsonify(merge_data_with_flags(filter))    

if __name__ == "__main__":
    app.run(debug=True)

