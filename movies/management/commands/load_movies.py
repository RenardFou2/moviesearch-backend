import csv
import json
from datetime import datetime
from django.core.management.base import BaseCommand
from movies.models import Movie, Category

class Command(BaseCommand):
    help = 'Wczytuje dane z pliku tmdb_5000_movies.csv do bazy danych'

    def handle(self, *args, **kwargs):
        with open('tmdb_5000_movies.csv', 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                try:
                    release_date = row['release_date']
                    if release_date:
                        try:
                            release_date = datetime.strptime(release_date, "%Y-%m-%d").date()
                        except ValueError:
                            self.stdout.write(self.style.ERROR(
                                f"Invalid date format for movie: {row['original_title']} ({release_date})"))
                            continue
                    else:
                        self.stdout.write(self.style.WARNING(
                            f"Missing release date for movie: {row['original_title']}"))
                        continue

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

                    self.stdout.write(self.style.SUCCESS(
                        f"{'Added' if created else 'Updated'} movie: {movie.title}"))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(
                        f"Error processing movie {row['original_title']} ({row['id']}): {e}"))
