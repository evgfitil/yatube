import re

import pytest
from django.contrib.auth import get_user_model
from django.db.models import fields

try:
    from posts.models import Comment
except ImportError:
    assert False, 'The Comment model is not found'

try:
    from posts.models import Post
except ImportError:
    assert False, 'The Post model is not found'


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


class TestComment:

    def test_comment_model(self):
        model_fields = Comment._meta.fields
        text_field = search_field(model_fields, 'text')
        assert text_field is not None, 'Add the attribute name `text` of the `Comment` model'
        assert type(text_field) == fields.TextField, \
            'The `text` attribute of the `Comment` model must be `TextField`'

        created_field = search_field(model_fields, 'created')
        assert created_field is not None, 'Add the pub date in `created` attribute of the `Comment` model'
        assert type(created_field) == fields.DateTimeField, \
            'The `created` attribute of the `Comment` model must be `DateTimeField`'
        assert created_field.auto_now_add, 'The `created` attribute of the `Comment` model must be an `auto_now_add`'

        author_field = search_field(model_fields, 'author_id')
        assert author_field is not None, 'Add the user who created the event `author` of the `Comment` model'
        assert type(author_field) == fields.related.ForeignKey, \
            'The `author` attribute of the `Comment` model must be an `ForeignKey`'
        assert author_field.related_model == get_user_model(), \
            'The `author` attribute of the `Comment` must be a reference to the `User` model'

        post_field = search_field(model_fields, 'post_id')
        assert post_field is not None, 'Add the `group` attribute in `Comment` model'
        assert type(post_field) == fields.related.ForeignKey, \
            'The `group` attribute of the `Comment` model must be an `ForeignKey`'
        assert post_field.related_model == Post, \
            'The `group` attribute of the `Comment` model must be a reference to the `Post` model'

    @pytest.mark.django_db(transaction=True)
    def test_comment_add_view(self, client, post):
        try:
            response = client.get(f'/{post.author.username}/{post.id}/comment')
        except Exception as e:
            assert False, f'''`/<username>/<post_id>/comment/` page is not working properly. Error: `{e}`'''
        if response.status_code in (301, 302) and response.url == f'/{post.author.username}/{post.id}/comment/':
            url = f'/{post.author.username}/{post.id}/comment/'
        else:
            url = f'/{post.author.username}/{post.id}/comment'
        assert response.status_code != 404, \
            'The page `/<username>/<post_id>/comment/` is not found, check it in *urls.py*'

        response = client.post(url, data={'text': 'New comment!'})
        if not(response.status_code in (301, 302) and response.url.startswith(f'/auth/login')):
            assert False, 'Check that non-authorized user redirect to the authorization page'

    @pytest.mark.django_db(transaction=True)
    def test_comment_add_auth_view(self, user_client, post):
        try:
            response = user_client.get(f'/{post.author.username}/{post.id}/comment')
        except Exception as e:
            assert False, f'''The page `/<username>/<post_id>/comment/` is not working proreply. Error: `{e}`'''
        if response.status_code in (301, 302) and response.url == f'/{post.author.username}/{post.id}/comment/':
            url = f'/{post.author.username}/{post.id}/comment/'
        else:
            url = f'/{post.author.username}/{post.id}/comment'
        assert response.status_code != 404, \
            'The page `/<username>/<post_id>/comment/` is not found, check it in *urls.py*'

        text = 'New comment 94938!'
        response = user_client.post(url, data={'text': text})

        assert response.status_code in (301, 302), \
            'Check that after a comment created, users are redirected to the post page'
        comment = Comment.objects.filter(text=text, post=post, author=post.author).first()
        assert comment is not None, \
            'Check that you create a new comment'
        assert response.url.startswith(f'/{post.author.username}/{post.id}'), \
            'Check that after a comment created, you are redirected to the post page'
