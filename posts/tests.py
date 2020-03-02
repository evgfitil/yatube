from django.test import TestCase, Client
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.cache import cache
from .models import Post, User
from .forms import PostForm


class PostsTest(TestCase):
    """Posts application tests."""
    def setUp(self):
        """Setup and user creation."""
        self.client = Client()
        self.user = User.objects.create_user(
            username="someuser", email="someuser@someemail.com", password="somepassword"
        )
        self.client.login(username="someuser", password="somepassword")

    def test_profile(self):
        """Profile creation test."""
        response = self.client.get("/someuser/")
        self.assertEqual(response.status_code, 200)

    def test_cache(self):
        self.client.get('/')
        self.post = Post.objects.create(
            text="This post was created to check the cache", author=self.user
        )

        # Check the new post not on the index page
        response_index = self.client.get('/')
        self.assertNotContains(response_index, self.post.text, status_code=200)
        cache.set('my_key', 'my_value', 20)
        self.assertTrue(cache.get('my_key'))
        
        # Clear cache & check post on the index page
        cache.clear()
        response_index = self.client.get('/')
        self.assertFalse(cache.get('my_key'))
        self.assertContains(response_index, self.post.text, status_code=200)

    def test_new_post(self):
        """Post creating tests."""
        cache.clear()
        self.post = Post.objects.create(
            text="This post was created to check the application", author=self.user
        )

        # Check the new post on the user profile page
        response = self.client.get('/someuser/')
        self.assertContains(response, self.post.text, count=1, status_code=200)
        
        # Check the new post on the post page
        post_url = f"/someuser/{self.post.id}/"
        response_post = self.client.get(post_url)
        self.assertContains(response_post, self.post.text, count=1, status_code=200)
        
        # Check the new post on the index page
        response_index = self.client.get('/')
        self.assertContains(response_index, self.post.text, count=1, status_code=200)
    
    def test_post_edit(self):
        """Post editing tests."""
        cache.clear()
        self.post = Post.objects.create(
            text="This post was created to check the application", author=self.user
        )

        # Post editing
        post_edit = Post.objects.get(id=self.post.id)
        self.post_edit_text = "Some new text"
        post_edit.text = self.post_edit_text
        post_edit.save()
        
        # Check the edited post on the user profile page
        response = self.client.get('/someuser/')
        self.assertContains(response, self.post_edit_text, count=1, status_code=200)
        
        # Check the edited post on the post page
        post_url = f"/someuser/{self.post.id}/"
        response_post = self.client.get(post_url)
        self.assertContains(response_post, self.post_edit_text, count=1, status_code=200)
        
        # Check the edited post on the index page
        response_index = self.client.get('/')
        self.assertContains(response_index, self.post_edit_text, count=1, status_code=200)
    
    def test_page_not_found(self):
        """Non-existent page test."""
        response = self.client.get("some_non_existing_page")
        self.assertEqual(response.status_code, 404)
    
    def test_post_with_image(self):
        """Post with image testing."""
        cache.clear()
        post_image = SimpleUploadedFile(
            name="some_image.jpg", content=open("some_image.jpg", "rb").read(), content_type='image/jpeg'
        )
        self.post = Post.objects.create(
            text="This post was created to check the post with image", author=self.user, image=post_image
        )

        # Checking the image tag on the user profile page
        response = self.client.get('/someuser/')
        self.assertContains(response, '<img', count=1, status_code=200)
        self.assertContains(response, self.post.text, count=1, status_code=200)
        
        # Checking the image tag on the post page
        post_url = f"/someuser/{self.post.id}/"
        response_post = self.client.get(post_url)
        self.assertContains(response_post, '<img', count=1, status_code=200)

        # Checking the image tag on the index page
        response_index = self.client.get('/')
        self.assertContains(response_index, '<img', count=1, status_code=200)
        self.post.delete()

        # Checking uploading not image file
        upload_file = open('some_fake_image.jpg', 'rb')
        image = {'image': SimpleUploadedFile(upload_file.name, upload_file.read())}
        form = PostForm({'text': 'some text'}, image)
        self.assertFalse(form.is_valid())

    def test_coomments(self):
        """Testing comments with authorized and unauthorized users."""
        # Creating post
        self.post = Post.objects.create(
            text="This post was created to check the comments", author=self.user
        )
        
        # Creating comment by auth user
        post_url = f"/someuser/{self.post.id}/comment"
        self.client.post(post_url, {'text': 'some comment text'})
        get_url = f"/someuser/{self.post.id}/"
        response = self.client.get(get_url)
        self.assertContains(response, 'some comment text', status_code=200)
        
        # Creating comment by unauth user
        self.client.logout()
        response = self.client.post(post_url, {'text': 'comment'})
        redirect_url = f"/auth/login/?next=/someuser/{self.post.id}/comment"
        self.assertRedirects(response, redirect_url)

    def test_unauthorized_user(self):
        """Unauthorized user redirect test."""
        self.client.logout()
        response = self.client.get('/new/')
        self.assertRedirects(response, '/auth/login/?next=/new/')

    def test_followers(self):
        """Testing favorites authors posts."""
        # Creating author user and authors posts
        self.author = User.objects.create_user(
            username="author", email="author@someemail.com", password="somepassword"
        )
        self.client.login(username="author", password="somepassword")
        self.author_post = Post.objects.create(
            text="This post for my followers", author=self.author
        )
        
        # Creating follower, subscribe to the author and check author post on follow page
        self.follower = User.objects.create_user(
            username="follower", email="follower@mail.com", password="somepassword"
        )
        self.client.login(username="follower", password="somepassword")
        self.client.get('/author/follow')
        response = self.client.get('/follow/')
        self.assertContains(response, "This post for my followers", count=1, status_code=200)
        
        # Checking unfollow function
        self.client.get('/author/unfollow')
        response = self.client.get('/follow/')
        self.assertNotContains(response, "This post for my followers", status_code=200)
        
        # Checking post on follow page by other user
        self.client.login(username="someuser", password="somepassword")
        response = self.client.get('/follow/')
        self.assertNotContains(response, "This post for my followers", status_code=200)
