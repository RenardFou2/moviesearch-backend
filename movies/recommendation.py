import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from movies.models import Movie
import requests
from movies.apps import MoviesConfig

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

    dbcontent = MoviesConfig.vectors

    if title.lower() not in dbcontent["title"].str.lower().values:
        return f"Movie '{title}' not found in the database."

    tfidf_matrix = np.stack(dbcontent["vector"].values)
    idx = dbcontent[dbcontent["title"].str.lower() == title.lower()].index[0]

    sim_scores = cosine_similarity(tfidf_matrix[idx].reshape(1, -1), tfidf_matrix).flatten()

    #Top N podobnych filmów
    similar_indices = np.argsort(sim_scores)[::-1][1:top_n + 1]

    recommended_movies = dbcontent.iloc[similar_indices].copy()
    recommended_movies["similarity"] = sim_scores[similar_indices]

    recommended_movies["poster"] = recommended_movies.apply(
        lambda row: fetch_poster(row["tmdb_id"]), axis=1
    )

    recommended_movies.rename(columns={"tmdb_id": "id"}, inplace=True)
    return recommended_movies[["id", "title", "overview", "rating", "poster", "similarity"]].to_dict("records")
