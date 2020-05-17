from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Recipe

from recipe.serializers import RecipeSerializer

RECIPE_URL = reverse('recipe:recipe-list')


def sample_recipe(user, **params):
    """Create and return a sample recipe"""
    defaults = {
        'title': 'sample recipe',
        'time_minutes': 10,
        'price': 5.00
    }
    defaults.update(params)

    return Recipe.objects.create(user=user, **defaults)


class PublicRecipeApiTests(TestCase):
    """Test the unauthenticated Recipe API"""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """Test auth is required """
        res = self.client.get(RECIPE_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeApiTests(TestCase):
    """Test the authorised user Recipe API"""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            'test@hatxbot.com',
            'password123'
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_recipes(self):
        """Test retrieving a list of Recipe"""
        sample_recipe(user=self.user)
        sample_recipe(user=self.user)

        res = self.client.get(RECIPE_URL)

        recipes = Recipe.objects.all().order_by('-id')
        serializer = RecipeSerializer(recipes, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_recipe_limited_to_user(self):
        """Test that tags returned are for the authenticated user"""
        user2 = get_user_model().objects.create_user(
            'others@hatxbot.com'
            'testpass'
        )
        sample_recipe(user=user2)
        sample_recipe(user=self.user)

        res = self.client.get(RECIPE_URL)
        recipes = Recipe.objects.filter(user=self.user)
        serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data, serializer.data)

    # def test_create_tag_successful(self):
    #     """Test creating a new tag"""
    #     payload = {'name': 'Test tag'}
    #     self.client.post(TAGS_URL, payload)

    #     exists = Tag.objects.filter(
    #         user=self.user,
    #         name=payload['name']
    #     ).exists()
    #     self.assertTrue(exists)

    # def test_create_tag_invalid(self):
    #     """Test creating a new tag with invalid payload"""
    #     payload = {'name': ''}
    #     res = self.client.post(TAGS_URL, payload)

    #     self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
