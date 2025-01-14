import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from movies.models import Movie
import requests

API_KEY = '0d7c60fd7811d07743a5a4bfe142ad40'
TMDB_IMAGE_BASE_URL = "https://image.tmdb.org/t/p/w500"

def fetch_poster(tmdb_id):
    try:
        url = f"https://api.themoviedb.org/3/movie/{tmdb_id}?api_key={API_KEY}"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            poster_path = data.get("poster_path")
            return f"{TMDB_IMAGE_BASE_URL}{poster_path}" if poster_path else None
        else:
            return None
    except Exception as e:
        print(f"Error fetching poster for TMDB ID {tmdb_id}: {e}")
        return None
    
def get_recommendations(title, top_n=10):

    movies = Movie.objects.all()
    data = [
        {
            "id": movie.tmdb_id,
            "title": movie.title,
            "overview": movie.overview,
            "categories": ", ".join([category.name for category in movie.categories.all()]),
            "rating": movie.rating,
        }
        for movie in movies
    ]
    dbcontent = pd.DataFrame(data)

    dbcontent['features'] = dbcontent['title'] + " " + dbcontent['overview'] + " " + dbcontent['categories']

    tfidf = TfidfVectorizer(stop_words='english')
    tfidf_matrix = tfidf.fit_transform(dbcontent['features'])

    cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)
    
    try:
        idx = dbcontent[dbcontent['title'].str.lower() == title.lower()].index[0]
    except IndexError:
        return f"Movie '{title}' not found in the database."
    
    #Oblicza podobieństwa
    sim_scores = list(enumerate(cosine_sim[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    

    # "n" podobnych filmów
    sim_scores = sim_scores[1:top_n + 1]
    movie_indices = [i[0] for i in sim_scores]
    similarity_scores = [i[1] for i in sim_scores]

    recommended_movies = dbcontent.iloc[movie_indices].reset_index(drop=True)
    recommended_movies['id'] = recommended_movies['id']
    recommended_movies['similarity'] = similarity_scores

    recommended_movies['poster'] = recommended_movies['id'].apply(fetch_poster)

    
    return recommended_movies.to_dict('records')
