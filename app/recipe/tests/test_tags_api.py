from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient
from recipe.tests.test_recipe_api import sample_recipe, sample_tag

from core.models import Tag

from recipe.serializers import TagSerializer


TAGS_URL = reverse('recipe:tag-list')


class PubliTagsApiTests(TestCase):
    """Test the publicly available endpoints"""

    def setUp(self) -> None:
        self.client = APIClient()

    def test_login_requiered(self):
        """Test that login is requeired for retrieveing tags"""
        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagsApiTests(TestCase):
    """User tags API tests with authentication"""

    def setUp(self) -> None:
        self.user = get_user_model().objects.create_user(
            email='test@optiwe.com',
            password='superSecurePassword',
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_tags(self):
        """Test retrieving tags"""
        Tag.objects.create(user=self.user, name='Vegan')
        Tag.objects.create(user=self.user, name='Dessert')

        res = self.client.get(TAGS_URL)

        tags = Tag.objects.all().order_by('-name')
        serializer = TagSerializer(tags, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_tag_limited_to_user(self):
        """Test that tags returned are for the authenticated user"""

        user2 = get_user_model().objects.create_user(
            email='other@optiwe.com',
            password='superSecurePassword',
        )
        Tag.objects.create(user=user2, name='Fruity')
        tag = Tag.objects.create(user=self.user, name='Comfort Food')

        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], tag.name)

    def test_create_tag_successful(self):
        """Test creating a new tag"""
        payload = {
            'name': 'Test tag'
        }
        res = self.client.post(TAGS_URL, payload)

        exists = Tag.objects.filter(
            user=self.user,
            name=payload['name']
        ).exists()

        self.assertTrue(exists)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_create_tag_invalid(self):
        """Test creating an invalid tag"""
        payload = {'name': ''}

        res = self.client.post(TAGS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_tags_in_use_succesful(self):
        """Test getting al ussed tags by recipes"""
        tag1 = sample_tag(self.user, 'ta')
        tag2 = sample_tag(self.user, 'tb')
        tag3 = sample_tag(self.user, 'tc')

        recip1 = sample_recipe(self.user, title='recip1')
        recip1.tags.add(tag1)
        recip1.tags.add(tag2)
        recip2 = sample_recipe(self.user, title='recip2')
        recip2.tags.add(tag2)

        payload = {
            'in_use': 1
        }

        res = self.client.get(TAGS_URL, payload)

        serializer1 = TagSerializer(tag1)
        serializer2 = TagSerializer(tag2)
        serializer3 = TagSerializer(tag3)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 2)
        self.assertIn(serializer1.data, res.data)
        self.assertIn(serializer2.data, res.data)
        self.assertNotIn(serializer3.data, res.data)

    def test_get_tags_in_use_invalid_inuse(self):
        payload = {
            'in_use': 'invalid'
        }
        res = self.client.get(TAGS_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_tags_in_use_invalid_key(self):
        payload = {
            'asdasd': 0
        }
        res = self.client.get(TAGS_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)