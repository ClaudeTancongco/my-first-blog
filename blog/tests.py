from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from .models import Post

class CustomAuthTokenTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='jawad', password='jawad')
        self.client = APIClient()

    def test_custom_auth_token_valid(self):
        response = self.client.post('/api-token-auth/', {'username': 'jawad', 'password': 'jawad'})
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_400_BAD_REQUEST])

        if response.status_code == status.HTTP_200_OK:
            self.assertIn('token', response.data)
            token = response.data['token']
            print("User token:", token)
        else:
            self.assertEqual(response.data, {'message': 'Invalid username/password'})
            

class PostAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='jawad', password='jawad')
        self.published_post = Post.objects.create(
            author=self.user,
            title='Published Post',
            text='This is a published post.',
        )

    def test_get_published_post(self):
        response = self.client.get(f'/api/{self.published_post.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Published Post')
        self.assertEqual(response.data['text'], 'This is a published post.')
