from flask import Flask, render_template, jsonify, request
import random
import requests
import pickle,csv
import pandas as pd

app = Flask(__name__, template_folder='templates')
model = 0
global_user_id = 300000
with open('32m.pkl', 'rb') as file:  # wb or rb
    model = pickle.load(file)

movies = pd.read_csv("movies.csv", dtype={'imdbId': str})



def generate_reccomendations():
    global global_user_id

    ratings = pd.read_csv("ratings.csv")

    rated_movie_ids = set(ratings[ratings['userId'] == global_user_id]['movieId'])

    sampled_movies = movies[~movies['movieId'].isin(rated_movie_ids)].sample(n=10000)

    predictions = []

    for index, row in sampled_movies.iterrows():
        movie_id = row['movieId']
        predicted_rating = model.predict(global_user_id, movie_id)

        # Store all relevant information
        predictions.append({
            'movieId': movie_id,
            'title': row['title'],
            'imdbId': row['imdbId'],
            'predicted_rating': predicted_rating.est
        })

    predictions.sort(key=lambda x: x['predicted_rating'], reverse=True)

    top_recommendations = predictions[:10]


    def fetch_movie_poster(imdb_id):
        apikey = " " #PUT YOUR API KEY HERE
        api_url = f"https://www.omdbapi.com/?i=tt{imdb_id}&apikey=" + apikey
        response = requests.get(api_url)
        data = response.json()


        title = data.get("Title", "Unknown Title")
        poster_url = data.get("Poster", "https://via.placeholder.com/300x450?text=No+Poster")

        return {"title": title, "image": poster_url}


    movie_array = []
    for movie in top_recommendations:
        movie_info = fetch_movie_poster(movie['imdbId'])
        movie_info['movieId'] = movie['movieId']
        movie_array.append(movie_info)

    return movie_array

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/home')
def home():
    global global_user_id
    profile_name = request.args.get('profile')
    if(profile_name == "SUBJECT 1"):
        global_user_id = 300000
    elif profile_name == "SUBJECT 2" :
        global_user_id = 300001
    else :
        global_user_id = 300002
    return render_template('home.html', profile=profile_name)

@app.route('/generate_reccomendations')
def generate():
    entries = generate_reccomendations()
    return jsonify(entries=entries)


@app.route('/submit_rating', methods=['POST'])
def submit_rating():
    data = request.get_json()
    movie_id = data['movie_id']
    rating = data['rating']

    user_id = global_user_id  

    new_rating = [user_id, movie_id, rating, 0]


    with open('ratings.csv', mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(new_rating)

    print(f"Received rating for movie_id: {movie_id} with rating: {rating}")

    return jsonify({"message": "Rating recorded to database!"})

if __name__ == '__main__':
    app.run(debug=True)
