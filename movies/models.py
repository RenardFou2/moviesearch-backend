from django.db import models
import pickle
import json

class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Movie(models.Model):
    tmdb_id = models.CharField(max_length=10, unique=True)
    title = models.CharField(max_length=255)
    year = models.DateField(null=True)
    rating = models.FloatField()
    overview = models.CharField(max_length=500)
    poster = models.URLField(blank=True, null=True)
    categories = models.ManyToManyField(Category, related_name='movies')
    vector = models.BinaryField(null=True)

    def __str__(self):
        return self.title
    
    def set_vector(self, vector):
        """Save NumPy vector as binary data."""
        self.vector = pickle.dumps(vector)

    def get_vector(self):
        """Load NumPy vector from binary data."""
        return pickle.loads(self.vector) if self.vector else None