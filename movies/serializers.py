from rest_framework import serializers
from .models import Category, Movie

class MovieSerializer(serializers.ModelSerializer):
    categories = serializers.StringRelatedField(many=True)
    backdrops = serializers.ListField(child=serializers.CharField(), required=False)

    class Meta:
        model = Movie
        fields = ['id', 'title', 'year', 'rating', 'poster', 'overview', 'categories', 'backdrops']

class CategorySerializer(serializers.ModelSerializer):
    movies = MovieSerializer(many=True, read_only=True)

    class Meta:
        model = Category
        fields = ['id', 'name', 'movies']