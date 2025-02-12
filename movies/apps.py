from django.apps import AppConfig
import pandas as pd
import numpy as np
import pickle

class MoviesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'movies'
    vectors = None

    def ready(self):
        from django.core.exceptions import ObjectDoesNotExist
        from movies.models import Movie
        try:
            movies = Movie.objects.all().values("tmdb_id", "title", "overview", "rating", "vector", "poster")
            movie_list = list(movies)
            dbcontent = pd.DataFrame(movie_list)

            def deserialize_vector(byte_data):
                try:
                    return pickle.loads(byte_data)
                except Exception as e:
                    print(f"Error deserializing vector: {e}")   
                    return np.zeros(5000)  # Default

            dbcontent["vector"] = dbcontent["vector"].apply(deserialize_vector)
            self.__class__.vectors = dbcontent
            print("TF-IDF vectors preloaded into memory.")
        except ObjectDoesNotExist:
            print("No movies found. Skipping vector preload.")