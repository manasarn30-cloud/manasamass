from unittest.mock import patch
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
import requests
from movies.models import Movie, MyList
from movies.tmdb import TMDBClient


class MovieTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user1 = User.objects.create_user('alice', 'alice@example.com', 'Pass1234!')
        self.user2 = User.objects.create_user('bob', 'bob@example.com', 'Pass1234!')

        self.movie1 = Movie.objects.create(
            title='Inception',
            overview='A thief who enters dreams.',
            rating=8.8,
            genre='Sci-Fi, Action',
            release_date='2010-07-15',
            is_featured=True,
            is_trending=True,
            is_popular=True,
            trailer_url='https://www.youtube.com/watch?v=YoHD9XEInc0'
        )

        self.movie2 = Movie.objects.create(
            title='The Dark Knight',
            overview='Batman combats the Joker.',
            rating=9.0,
            genre='Action, Crime',
            release_date='2008-07-16',
            is_trending=True,
            is_popular=True,
            trailer_url='https://www.youtube.com/watch?v=EXeTwQWrcwY'
        )

    def test_home_page_loads_and_displays_movies(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Inception')
        self.assertContains(response, 'Trending Now')

    def test_discover_page_loads(self):
        response = self.client.get(reverse('discover'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Inception')
        self.assertContains(response, 'The Dark Knight')

    def test_discover_search_works(self):
        response = self.client.get(reverse('discover'), {'q': 'Batman'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'The Dark Knight')
        self.assertNotContains(response, 'Inception')

    def test_discover_genre_filter_works(self):
        response = self.client.get(reverse('discover'), {'genre': 'Sci-Fi'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Inception')
        self.assertNotContains(response, 'The Dark Knight')

    def test_movie_detail_view_renders(self):
        response = self.client.get(reverse('movie_detail', args=[self.movie1.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Inception')
        self.assertContains(response, 'Watch Official Trailer')
        self.assertContains(response, 'A thief who enters dreams')

    def test_my_list_requires_authentication(self):
        response = self.client.get(reverse('my_list'))
        self.assertEqual(response.status_code, 302)

    def test_my_list_toggle_adds_and_removes_movie(self):
        self.client.login(username='alice', password='Pass1234!')

        # Toggle Add
        response = self.client.post(reverse('toggle_my_list', args=[self.movie1.id]))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['in_list'])
        self.assertTrue(MyList.objects.filter(user=self.user1, movie=self.movie1).exists())

        # Toggle Remove
        response = self.client.post(reverse('toggle_my_list', args=[self.movie1.id]))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertFalse(data['in_list'])
        self.assertFalse(MyList.objects.filter(user=self.user1, movie=self.movie1).exists())

    def test_my_list_is_user_specific(self):
        MyList.objects.create(user=self.user1, movie=self.movie1)

        # Alice sees her list
        self.client.login(username='alice', password='Pass1234!')
        response = self.client.get(reverse('my_list'))
        self.assertContains(response, 'Inception')

        # Bob logs in and does not see Alice's movie in his list
        self.client.login(username='bob', password='Pass1234!')
        response = self.client.get(reverse('my_list'))
        self.assertNotContains(response, 'Inception')
        self.assertContains(response, 'Your List is Empty')

    @patch('requests.get')
    def test_tmdb_api_timeout_triggers_fallback_catalog(self, mock_get):
        mock_get.side_effect = requests.Timeout("Connection timed out after 5.0s")
        client = TMDBClient()
        # Should gracefully return curated fallback list without crashing
        trending = client.get_trending()
        self.assertGreater(len(trending), 0)
