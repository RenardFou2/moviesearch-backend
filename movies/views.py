from rest_framework.response import Response
from rest_framework.decorators import api_view
from .serializers import MovieSerializer
from movies.recommendation import get_recommendations
import requests
import traceback


API_KEY = '0d7c60fd7811d07743a5a4bfe142ad40'

BASE_URL = 'https://api.themoviedb.org/3/movie/'

CATEGORIES = {
    "top_rated": "top_rated",
    "popular": "popular",
    "now_playing": "now_playing",
    "upcoming": "upcoming",
}

@api_view(['GET'])
def get_movies(request):
    
    movies_by_category = {}
    for category, endpoint in CATEGORIES.items():
        url = f'{BASE_URL}{endpoint}?api_key={API_KEY}'
        response = requests.get(url)
        
        if response.status_code != 200:
            return Response({"error": f"Failed to retrieve {category} movies"}, status=500)
        
        data = response.json().get('results', [])

        movies = [
            {
                'id': item.get('id'),
                'title': item.get('title', 'N/A'),
                'year': item.get('release_date', 'N/A')[:4],
                'rating': item.get('vote_average', 'N/A'),
                'poster': f"https://image.tmdb.org/t/p/w500{item.get('poster_path', '')}"
            }
            for item in data
        ]

        movies_by_category[category] = movies

    return Response(movies_by_category)

@api_view(['GET'])
def get_movie_detail(request, movie_id):
    url = f'https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}'
    response = requests.get(url)
    if response.status_code != 200:
        return Response({"error": "Failed to retrieve data"}, status=500)

    movie = response.json()
    movie_data = {
        'id': movie.get('id'),
        'title': movie.get('title', 'N/A'),
        'year': movie.get('release_date', 'N/A')[:4],
        'rating': movie.get('vote_average', 'N/A'),
        'poster': f"https://image.tmdb.org/t/p/w500{movie.get('poster_path', '')}",
        'overview': movie.get('overview', 'N/A'),
    }
    
    serializer = MovieSerializer(movie_data)
    return Response(serializer.data)

@api_view(['GET'])
def search_movies(request):
    query = request.GET.get('query')
    if not query:
        return Response({"error": "No search query provided"}, status=400)

    url = f'https://api.themoviedb.org/3/search/movie?api_key={API_KEY}&query={query}'
    response = requests.get(url)
    
    if response.status_code != 200:
        return Response({"error": "Failed to retrieve data"}, status=500)

    data = response.json().get('results', [])
    
    movies = [{
        'id': item.get('id'),
        'title': item.get('title', 'N/A'),
        'year': item.get('release_date', 'N/A')[:4],
        'rating': item.get('vote_average', 'N/A'),
        'poster': f"https://image.tmdb.org/t/p/w500{item.get('poster_path', '')}",
        'overview': item.get('overview', 'N/A'),
    } for item in data]
    
    return Response(movies)

@api_view(['GET'])
def search_movies_by_genre(request):
    genre_id = request.query_params.get('genre_id')
    url = f'https://api.themoviedb.org/3/discover/movie?api_key={API_KEY}&with_genres={genre_id}'
    response = requests.get(url)

    if response.status_code != 200:
        return Response({"error": "Failed to retrieve data"}, status=500)

    data = response.json().get('results', [])
    movies = [
        {
            'id': item.get('id'),
            'title': item.get('title', 'N/A'),
            'year': item.get('release_date', 'N/A')[:4],
            'rating': item.get('vote_average', 'N/A'),
            'poster': f"https://image.tmdb.org/t/p/w500{item.get('poster_path', '')}",
        }
        for item in data
    ]

    return Response(movies)

@api_view(['GET'])
def get_genre_names(request):
    url = f'https://api.themoviedb.org/3/genre/movie/list?api_key={API_KEY}'
    response = requests.get(url)

    if response.status_code != 200:
        return Response({"error": "Failed to retrieve genre data"}, status=500)
    
    return Response(response.json())

@api_view(['GET', 'POST'])
def recommend_movies(request):
    if request.method == 'GET':
        title = request.query_params.get('title')
        top_n = int(request.query_params.get('top_n', 10))

        if not title:
            return Response({"error": "A 'title' query parameter is required."}, status=400)

        try:
            recommendations = get_recommendations(title, top_n=top_n)
            return Response(recommendations, status=200)
        except ValueError as e:
            return Response({"error": str(e)}, status=404)
        except Exception as e:
            return Response({"error": f"An unexpected error occurred: {str(e)}"}, status=500)

    elif request.method == 'POST':
        titles = request.data.get('titles', [])
        top_n = int(request.data.get('top_n', 15))

        #Test
        print(f"Received titles: {titles}")

        if not titles:
            return Response({"error": "At least one title is required."}, status=400)

        try:
            recommendations = []
            for title in titles:
                try:
                    print(f"Getting recommendations for {title}")
                    recs = get_recommendations(title, top_n)

                    # Jeśli nie ma rekomendacji
                    if isinstance(recs, str):
                        print(recs)
                        continue

                    recommendations.extend(recs)
                except Exception as e:
                    print(f"Error getting recommendations for {title}: {str(e)}")
                    continue

            # Usuwa duplikaty
            unique_recommendations = {}
            for rec in recommendations:
                if rec['title'] not in unique_recommendations or rec['similarity'] > unique_recommendations[rec['title']]['similarity']:
                    unique_recommendations[rec['title']] = rec

            sorted_recommendations = sorted(unique_recommendations.values(), key=lambda x: x['similarity'], reverse=True)

            return Response(sorted_recommendations, status=200)
        except Exception as e:
            traceback.print_exc()
            return Response({"error": f"An unexpected error occurred: {str(e)}"}, status=500)