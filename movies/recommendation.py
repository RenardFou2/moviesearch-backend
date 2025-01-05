import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from movies.models import Movie

def get_recommendations(title, top_n=5):

    movies = Movie.objects.all()
    data = [
        {
            "id": movie.id,
            "title": movie.title,
            "overview": movie.overview,
            "categories": ", ".join([category.name for category in movie.categories.all()])
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

    recommended_movies = dbcontent.iloc[movie_indices]
    return recommended_movies[['title', 'overview', 'categories']]
