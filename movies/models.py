from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Movie(models.Model):
    tmdb_id = models.CharField(max_length=10, unique=True)
    title = models.CharField(max_length=255)
    year = models.DateField()
    rating = models.CharField(max_length=5)
    vote_count = models.IntegerField(default=0)
    overview = models.CharField(max_length=500)
    poster = models.URLField()
    categories = models.ManyToManyField(Category, related_name='movies')

    def __str__(self):
        return self.title