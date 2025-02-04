import csv
import json
import pickle
import requests
from datetime import datetime
from django.core.management.base import BaseCommand
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np

from movies.models import Movie, Category

TMDB_API_KEY = '0d7c60fd7811d07743a5a4bfe142ad40'
TMDB_BASE_URL = "https://api.themoviedb.org/3"

class Command(BaseCommand):
    help = 'Load movie data from tmdb_5000_movies.csv or TMDB API, then compute TF-IDF vectors'

    def handle(self, *args, **kwargs):
        self.load_from_csv()
        self.fetch_from_tmdb()
        self.compute_and_save_vectors()

    def parse_date(self, date_string):
        if not date_string:
            return None
        try:
            return datetime.strptime(date_string, "%Y-%m-%d").date()
        except ValueError:
            self.stdout.write(self.style.WARNING(f"Invalid date format: {date_string}. Skipping."))
            return None

    def load_from_csv(self):
        try:
            with open('tmdb_5000_movies.csv', 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    try:
                        release_date = self.parse_date(row['release_date'])

                        genres_data = json.loads(row['genres'])
                        categories = [genre['name'] for genre in genres_data]
                        category_objects = [Category.objects.get_or_create(name=cat)[0] for cat in categories]

                        movie, created = Movie.objects.update_or_create(
                            tmdb_id=row['id'],
                            defaults={
                                'title': row['original_title'],
                                'year': release_date,
                                'rating': row['vote_average'],
                                'overview': row['overview'],
                                'poster': row['homepage'],
                            }
                        )
                        movie.categories.set(category_objects)
                        movie.save()

                        self.stdout.write(self.style.SUCCESS(f"{'Added' if created else 'Updated'} movie: {movie.title}"))
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f"Error processing movie {row['original_title']} ({row['id']}): {e}"))
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR("CSV file not found. Skipping CSV import."))

    def fetch_from_tmdb(self):
        categories = {
            "Action": 28,
            "Comedy": 35,
            "Drama": 18,
            "Horror": 27,
            "Science Fiction": 878,
        }

        for category_name, genre_id in categories.items():
            self.stdout.write(f"Fetching movies for category: {category_name}...")

            page = 1
            while page <= 5:
                response = requests.get(
                    f"{TMDB_BASE_URL}/discover/movie",
                    params={
                        "api_key": TMDB_API_KEY,
                        "with_genres": genre_id,
                        "language": "en-US",
                        "sort_by": "popularity.desc",
                        "page": page,
                    },
                )

                if response.status_code != 200:
                    self.stdout.write(self.style.ERROR(f"Failed to fetch movies for {category_name}. Status code: {response.status_code}"))
                    break

                movies = response.json().get("results", [])
                if not movies:
                    break

                for movie_data in movies:
                    try:
                        release_date = self.parse_date(movie_data.get("release_date", ""))

                        movie, created = Movie.objects.update_or_create(
                            tmdb_id=movie_data["id"],
                            defaults={
                                "title": movie_data["title"],
                                'year': release_date,
                                "rating": movie_data.get("vote_average", 0.0),
                                "overview": movie_data.get("overview", ""),
                                "poster": f"https://image.tmdb.org/t/p/w500{movie_data['poster_path']}" if movie_data.get("poster_path") else "",
                            }
                        )

                        category, _ = Category.objects.get_or_create(name=category_name)
                        movie.categories.add(category)

                        self.stdout.write(self.style.SUCCESS(f"{'Added' if created else 'Updated'} movie: {movie.title}"))
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f"Error processing movie {movie_data['title']} ({movie_data['id']}): {e}"))

                page += 1

        self.stdout.write(self.style.SUCCESS("Movies have been successfully fetched and saved from TMDB."))

    def compute_and_save_vectors(self):

        self.stdout.write("Computing TF-IDF vectors...")

        movies = Movie.objects.all()
        data = [
            {
                "tmdb_id": movie.tmdb_id,
                "title": movie.title,
                "overview": movie.overview,
                "categories": ", ".join([category.name for category in movie.categories.all()]),
                "rating": movie.rating,
            }
            for movie in movies
        ]

        features = [
            f"{title} {categories} {overview} {rating}"
            for title, categories, overview, rating in zip(
                [m["title"] for m in data],
                [m["categories"] for m in data],
                [m["overview"] for m in data],
                [m["rating"] for m in data],
            )
        ]

        tfidf = TfidfVectorizer(stop_words='english', ngram_range=(1, 2), max_features=5000)
        tfidf_matrix = tfidf.fit_transform(features)


        for i, movie in enumerate(movies):
            try:
                vector = tfidf_matrix[i].toarray()[0]
                movie.set_vector(vector)  # Zapisać jako binarne
                movie.save()
            except Exception as e:
                print(f"Error processing movie {movie.title} ({movie.tmdb_id}): {e}")


        self.stdout.write(self.style.SUCCESS("TF-IDF vectors computed and saved."))
