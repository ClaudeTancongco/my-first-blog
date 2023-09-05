from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from .models import Post, Comment
from rest_framework.authtoken.models import Token


class CustomAuthTokenTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='wkwkwk', password='wkwkwkwk')
        self.client = APIClient()

    def test_custom_auth_token_valid(self):
        response = self.client.post('/api-token/', {'username': 'wkwkwk', 'password': 'wkwkwkw'})
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_400_BAD_REQUEST])

        if response.status_code == status.HTTP_200_OK:
            self.assertIn('token', response.data)
            token = response.data['token']
            print("User token:", token)
    
    def test_custom_auth_token_invalid(self):
            
        response = self.client.post('/api-token/', {'username': 'wkwkwk', 'password': 'wkwkw'})
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_400_BAD_REQUEST])

        if response.status_code == status.HTTP_400_BAD_REQUEST:
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)  # Check for a 400 Bad Request response
            self.assertIn('non_field_errors', response.data)  # Check that 'non_field_errors' is present in the response data
            self.assertEqual(response.data['non_field_errors'][0], "Unable to log in with provided credentials.")  # Check the specific error message

            
class PostsAPITest(TestCase):
        def setUp(self):
            self.client = APIClient()
            self.user = User.objects.create_user(username='wkwkwk', password='wkwkwkwk')
            self.token = Token.objects.create(user=self.user)  # Create an authentication token for the user

            self.published_post = Post.objects.create(
            author=self.user,
            title='Published Post',
            text='This is a published post.',
        )
            
        def test_get_posts(self):
        # Include the authentication token in the request headers
            self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')

            response = self.client.get(f'/api/')
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            response = response.json()
            # print(response)

        def test_post_post(self):

            self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')

            data = {'title': 'Posty', 
                    'text': 'Posty Text',
                    'published_date': '2023-08-31T00:00:00Z',
                    'author': 1}
            
            response = self.client.post('/api/', data)
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            responseJson = response.json()
            post_id = responseJson['id']
            submitted_post = Post.objects.filter(id=post_id)[0]

            self.assertEqual(submitted_post.title, 'Posty')
            self.assertEqual(submitted_post.text, 'Posty Text')
            self.assertEqual(submitted_post.published_date.strftime('%Y-%m-%dT%H:%M:%SZ'), '2023-08-31T00:00:00Z')


class PostAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='wkwkwk', password='wkwkwkwk')
        self.user2 =  User.objects.create_user(username='user2', password='password2')
        self.token = Token.objects.create(user=self.user)  # Create an authentication token for the user

        self.published_post = Post.objects.create(
            author=self.user,
            title='Published Post',
            text='This is a published post.',
        )

    # /// GET ///

    def test_get_post(self):
        # Include the authentication token in the request headers
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')

        response = self.client.get(f'/api/{self.published_post.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Published Post')
        self.assertEqual(response.data['text'], 'This is a published post.')
        
    def test_get_post_404(self):

        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        response = self.client.get(f'/api/5487578395783/')

        # Assert that the response is a 404 Not Found
        self.assertEqual(response.status_code, 404)

    # /// PUT ///

    def test_put_post_as_auth(self):

        self.client.login(username='wkwkwk', password='wkwkwkwk')

        data = {
            'title': 'Poster', 
            'text': 'Poster Text',
            'published_date': '2023-08-31T08:00:00+08:00',
            'author': 1}
        
        response = self.client.put(f'/api/{self.published_post.id}/', data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['title'], 'Poster')
        self.assertEqual(response.data['text'], 'Poster Text')
        self.assertEqual(response.data['author'], 1)
        self.assertEqual(response.data['published_date'], '2023-08-31T08:00:00+08:00')

    def test_put_post_not_auth(self):

        self.client.login(username='user2', password='password2')

        data = {
            'title': 'Posty', 
            'text': 'Posty Text',
            'published_date': '2023-08-31T00:00:00Z',
            'author': 1}
        
        response = self.client.put(f'/api/{self.published_post.id}/', data)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.data['detail'], 'You are not authorized to edit this post.')

    def test_put_post_404(self):

        self.client.login(username='user2', password='password2')

        data = {
            'title': 'Posty', 
            'text': 'Posty Text',
            'published_date': '2023-08-31T00:00:00Z',
            'author': 1}
        
        response = self.client.put(f'/api/dfgndsgjnhrdgrgbre/', data)
        self.assertEqual(response.status_code, 404)

    # /// DELETE ///

    def test_delete_post_as_auth(self):

        # Authenticate as user2 (a different user)
        self.client.login(username='wkwkwk', password='wkwkwkwk')

        # Delete a post created by user1
        response = self.client.delete(f'/api/{self.published_post.id}/')

        # Assert that the response is a 204  status code
        self.assertEqual(response.status_code, 204)

        # Verify that the post doesn't exist in the database
        post_exists = Post.objects.filter(id=self.published_post.id).exists()
        self.assertFalse(post_exists)

    def test_delete_post_not_auth(self):

        # Authenticate as user2 (a different user)
        self.client.login(username='user2', password='password2')

        # Attempt to delete a post created by user1
        response = self.client.delete(f'/api/{self.published_post.id}/')

        # Assert that the response is a 403 Forbidden status code
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.data['detail'], 'You are not authorized to delete this post.')

        # Verify that the post still exists in the database
        post_exists = Post.objects.filter(id=self.published_post.id).exists()
        self.assertTrue(post_exists)

    def test_delete_post_404(self):

        self.client.login(username='wkwkwk', password='wkwkwkwk')

        response = self.client.delete(f'/api/34298085843/')

        self.assertEqual(response.status_code, 404)


class CommentAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='wkwkwk', password='wkwkwkwk')
        self.token = Token.objects.create(user=self.user)  # Create an authentication token for the user

        self.published_post = Post.objects.create(
            author=self.user,
            title='Test Post',
            text='Example',
            published_date="2023-08-17T08:00:00+08:00"
        )

        self.comment = Comment.objects.create(
            post=self.published_post,
            author='AJ Santos',
            text="I like this post",
            approved_comment=True
        )

    # /// GET ///

    def test_get_comment_from_post(self):

        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        response = self.client.get(f'/apicomment/{self.comment.id}/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Convert the response content to a string
        response_text = response.content.decode('utf-8')

        # Check if each expected comment is present in the response text
        expected_comments = [self.comment.text]
        for comment in expected_comments:
            self.assertIn(comment, response_text)

    def test_get_comment_404(self):

        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        response = self.client.get(f'/apicomment/5487578395783/')

        # Assert that the response is a 404 Not Found
        self.assertEqual(response.status_code, 404)

    # /// POST ///

    def test_post_comment_from_post(self):

        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        response = self.client.post(f'/apicomment/')

        data = {
            "text": "testing lang",
            "author": 'hi',
            "post": 1,
            "approved_comment": True
        }

        response = self.client.post(f'/apicomment/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        responseJson = response.json()
        list = Comment.objects.filter(pk=responseJson['id'])
        commentDetails = list[0]
        self.assertEqual(responseJson['author'], commentDetails.author)
        self.assertEqual(responseJson['text'], commentDetails.text)
        self.assertEqual(responseJson['approved_comment'], commentDetails.approved_comment)
        
    def test_post_comment_404(self):
        
        data = {
            "text": "Chilling",
            "author": "Spaghetti",
            "approved_comment": True
        }
        response = self.client.post(f'/apicomment/lol/', data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

