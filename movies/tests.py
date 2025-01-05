from django.test import TestCase
from movies.models import Movie, Category
from movies.recommendation import get_recommendations

class RecommendationTestCase(TestCase):
    def setUp(self):

        category1 = Category.objects.create(name="Sci-Fi")
        category2 = Category.objects.create(name="Adventure")

        movie1 = Movie.objects.create(
            tmdb_id="1",
            title="Avatar",
            year="2009-12-10",
            rating="7.9",
            overview="A paraplegic Marine dispatched to the moon Pandora...",
            poster="https://example.com/avatar.jpg",
        )
        movie1.categories.add(category1, category2)

        movie2 = Movie.objects.create(
            tmdb_id="2",
            title="Titanic",
            year="1997-12-19",
            rating="7.8",
            overview="A seventeen-year-old aristocrat falls in love...",
            poster="https://example.com/titanic.jpg",
        )
        movie2.categories.add(category1)

    def test_get_recommendations(self):
        recommendations = get_recommendations("Avatar", top_n=1)
        self.assertEqual(len(recommendations), 1)
        self.assertEqual(recommendations[0]["title"], "Titanic")
