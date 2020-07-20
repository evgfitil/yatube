import re
import tempfile

import pytest
from django.contrib.auth import get_user_model
from django.core.paginator import Paginator, Page
from django.db.models import fields

try:
    from posts.models import Post
except ImportError:
    assert False, 'The Post model is not found'

try:
    from posts.models import Follow
except ImportError:
    assert False, 'The Follow model is not found'


def search_field(fields, attname):
    for field in fields:
        if attname == field.attname:
            return field
    return None


def search_refind(execution, user_code):
    """Search refind"""
    for temp_line in user_code.split('\n'):
        if re.search(execution, temp_line):
            return True
    return False


class TestFollow:

    def test_follow(self):
        model_fields = Follow._meta.fields

        user_field = search_field(model_fields, 'user_id')
        assert user_field is not None, 'Add the user who created the event `user` of the `Follow` model'
        assert type(user_field) == fields.related.ForeignKey, \
            'The `user` attribute of the `Follow` model must be an `ForeignKey`'
        assert user_field.related_model == get_user_model(), \
            'The `user` attribute of the `Follow` model must be a reference to the `User` model'
        assert user_field.remote_field.related_name == 'follower', \
            'The `user` attribute of the `Follow` model should have a `related_name="follower"`'
        # assert user_field.on_delete == CASCADE, \
        #     'The `user` attribute of the `Follow` model should have a `on_delete=models.CASCADE`'

        author_field = search_field(model_fields, 'author_id')
        assert author_field is not None, 'Add the user who created the event `author` of the `Follow` model'
        assert type(author_field) == fields.related.ForeignKey, \
            'The `author` attribute of the `Follow` model must be an `ForeignKey`'
        assert author_field.related_model == get_user_model(), \
            'The `author` attribte of the `Follow` model must be a refference to the `User` model'
        assert author_field.remote_field.related_name == 'following', \
            'The `author` attribute of the `Follow` model should have a `related_name="following"`'
        # assert author_field.on_delete == CASCADE, \
        #     'The `author` attribute of the `Follow` model should have a `on_delete=models.CASCADE`'

    def check_url(self, client, url, str_url):
        try:
            response = client.get(f'{url}')
        except Exception as e:
            assert False, f'''The page `{str_url}` is not working properly. Error: `{e}`'''
        if response.status_code in (301, 302) and response.url == f'{url}/':
            response = client.get(f'{url}/')
        assert response.status_code != 404, f'The page `{str_url}` is not found, check it in *urls.py*'
        return response

    @pytest.mark.django_db(transaction=True)
    def test_follow_not_auth(self, client, user):
        response = self.check_url(client, '/follow', '/follow/')
        if not(response.status_code in (301, 302) and response.url.startswith(f'/auth/login')):
            assert False, \
                'Check that non-authorized user redirect from `/follow/` to the authorization page'

        response = self.check_url(client, f'/{user.username}/follow', '/<username>/follow/')
        if not(response.status_code in (301, 302) and response.url.startswith(f'/auth/login')):
            assert False, 'Check that non-authorized user redirect from `/<username>/follow/` ' \
                          'redirect to the authorization page'

        response = self.check_url(client, f'/{user.username}/unfollow', '/<username>/unfollow/')
        if not(response.status_code in (301, 302) and response.url.startswith(f'/auth/login')):
            assert False, 'Check that non-authorized user redirect from `/<username>/unfollow/` ' \
                          'redirect to the authorization page'

    @pytest.mark.django_db(transaction=True)
    def test_follow_auth(self, user_client, user, post):
        assert user.follower.count() == 0, 'Check the follow counter'
        self.check_url(user_client, f'/{post.author.username}/follow', '/<username>/follow/')
        assert user.follower.count() == 0, "Check that you can't follow up for yourself"

        user_1 = get_user_model().objects.create_user(username='TestUser_2344')
        user_2 = get_user_model().objects.create_user(username='TestUser_73485')

        self.check_url(user_client, f'/{user_1.username}/follow', '/<username>/follow/')
        assert user.follower.count() == 1, 'Check that you can follow to a user'
        self.check_url(user_client, f'/{user_1.username}/follow', '/<username>/follow/')
        assert user.follower.count() == 1, 'Check that you can only subscribe to a user once'

        image = tempfile.NamedTemporaryFile(suffix=".jpg").name
        Post.objects.create(text='Test post 4564534', author=user_1, image=image)
        Post.objects.create(text='Test post 354745', author=user_1, image=image)

        Post.objects.create(text='Test post 245456', author=user_2, image=image)
        Post.objects.create(text='Test post 9789', author=user_2, image=image)
        Post.objects.create(text='Test post 4574', author=user_2, image=image)

        response = self.check_url(user_client, f'/follow', '/follow/')
        assert 'paginator' in response.context, \
            'Check that you passed the `paginator` variable into the context of the `/follow/` page'
        assert type(response.context['paginator']) == Paginator, \
            'Check that the `paginator` variable type `Paginator` on the `/follow/` page'
        assert 'page' in response.context, \
            'Check that you passed the `page` variable into the context of the `/follow/` page'
        assert type(response.context['page']) == Page, \
            'Check that the `page` variable type `Page` on the `/follow/` page'
        assert len(response.context['page']) == 2, \
            'Check that on the `/follow/` posts of the authors you followed to'

        self.check_url(user_client, f'/{user_2.username}/follow', '/<username>/follow/')
        assert user.follower.count() == 2, 'Check that you can follow to a user'
        response = self.check_url(user_client, f'/follow', '/follow/')
        assert len(response.context['page']) == 5, \
            'Check that on the `/follow/` posts of the authors you followed to'

        self.check_url(user_client, f'/{user_1.username}/unfollow', '/<username>/unfollow/')
        assert user.follower.count() == 1, 'Check that you can unfollow user'
        response = self.check_url(user_client, f'/follow', '/follow/')
        assert len(response.context['page']) == 3, \
            'Check that on the `/follow/` posts of the authors you followed to'

        self.check_url(user_client, f'/{user_2.username}/unfollow', '/<username>/unfollow/')
        assert user.follower.count() == 0, 'Check that you can unfollow user'
        response = self.check_url(user_client, f'/follow', '/follow/')
        assert len(response.context['page']) == 0, \
            'Check that on the `/follow/` posts of the authors you followed to'
