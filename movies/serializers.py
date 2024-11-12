from rest_framework import serializers
from .models import Category, Movie

class MovieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Movie
        fields = ['id', 'title', 'year', 'rating', 'poster', 'overview']

class CategorySerializer(serializers.ModelSerializer):
    movies = MovieSerializer(many=True, read_only=True)

    class Meta:
        model = Category
        fields = ['id', 'name', 'movies']