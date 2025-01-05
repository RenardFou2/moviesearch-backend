from django.urls import path
from .views import get_movies, get_movie_detail, search_movies, search_movies_by_genre, get_genre_names, recommend_movies

urlpatterns = [
    path('api/movies/', get_movies, name='get_movies'),
    path('api/movies/<int:movie_id>/', get_movie_detail, name='get_move_detail'),
    path('api/search/', search_movies, name='search_movies'),
    path('api/genre-search/', search_movies_by_genre, name='search_movies_by_genre'),
    path('api/genre-names/', get_genre_names, name='get_genre_names'),
    path('api/recommendation/', recommend_movies, name='recommend_movies'),
]