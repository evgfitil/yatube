from io import BytesIO

import pytest
from PIL import Image
from django import forms
from django.contrib.auth import get_user_model
from django.core.files.base import File
from posts.models import Post
from django.db.models.query import QuerySet

def get_field_context(context, field_type):
    for field in context.keys():
        if field not in ('user', 'request') and type(context[field]) == field_type:
            return context[field]
    return


class TestPostView:

    @pytest.mark.django_db(transaction=True)
    def test_post_view_get(self, client, post_with_group):
        try:
            response = client.get(f'/{post_with_group.author.username}/{post_with_group.id}')
        except Exception as e:
            assert False, f'''The page `/<username>/<post_id>/` is not working properly. Error: `{e}`'''
        if response.status_code in (301, 302):
            response = client.get(f'/{post_with_group.author.username}/{post_with_group.id}/')
        assert response.status_code != 404, \
            'The page `/<username>/<post_id>/` is not found, check it in *urls.py*'

        profile_context = get_field_context(response.context, get_user_model())
        assert profile_context is not None, \
            'Check that you passed the `author` variable into the context of the page `/<username>/<post_id>/`'

        post_context = get_field_context(response.context, Post)
        assert post_context is not None, \
            'Check that you passed the post into the context of the page `/<username>/<post_id>/`'

        try:
            from posts.forms import CommentForm
        except ImportError:
            assert False, 'CommentForm is not found'

        comment_form_context = get_field_context(response.context, CommentForm)
        assert comment_form_context is not None, \
            'Check that you passed form `CommentForm` into the context of the page `/<username>/<post_id>/`'
        assert len(comment_form_context.fields) == 1, \
            'Check that the form have a 1 title'
        assert 'text' in comment_form_context.fields, \
            'Check that the form have a `text` title'
        assert type(comment_form_context.fields['text']) == forms.fields.CharField, \
            'Check that the `text` type is `CharField`'

        comment_context = get_field_context(response.context, QuerySet)
        assert comment_context is not None, \
            'Check that you passed list of comments with `QuerySet` type into the context of the page `/<username>/<post_id>/`'


class TestPostEditView:

    @pytest.mark.django_db(transaction=True)
    def test_post_edit_view_get(self, client, post_with_group):
        try:
            response = client.get(f'/{post_with_group.author.username}/{post_with_group.id}/edit')
        except Exception as e:
            assert False, f'''The page `/<username>/<post_id>/edit/` is not working properly. Error: `{e}`'''
        if response.status_code in (301, 302) and not response.url.startswith(f'/{post_with_group.author.username}/{post_with_group.id}'):
            response = client.get(f'/{post_with_group.author.username}/{post_with_group.id}/edit/')
        assert response.status_code != 404, \
            'The page `/<username>/<post_id>/edit/` is not found, check it in *urls.py*'

        assert response.status_code in (301, 302), \
            'Check the redirection if a user does not post author'

    @pytest.mark.django_db(transaction=True)
    def test_post_edit_view_author_get(self, user_client, post_with_group):
        try:
            response = user_client.get(f'/{post_with_group.author.username}/{post_with_group.id}/edit')
        except Exception as e:
            assert False, f'''The page `/<username>/<post_id>/edit/` is not working properly. Error: `{e}`'''
        if response.status_code in (301, 302):
            response = user_client.get(f'/{post_with_group.author.username}/{post_with_group.id}/edit/')
        assert response.status_code != 404, \
            'The page `/<username>/<post_id>/edit/` is not found, check it in *urls.py*'

        post_context = get_field_context(response.context, Post)
        assert post_context is not None, \
            'Check that you passed the post into the context of the page `/<username>/<post_id>/edit/`'

        assert 'form' in response.context, \
            'Check that you passed form into the context of the page `/<username>/<post_id>/edit/`'
        assert len(response.context['form'].fields) == 3, \
            'Check that the form on the page `/<username>/<post_id>/edit/` have a 3 title'
        assert 'group' in response.context['form'].fields, \
            'Check tha the `form` on the page `/<username>/<post_id>/edit/` have a `group` title'
        assert type(response.context['form'].fields['group']) == forms.models.ModelChoiceField, \
            'Check that the `group` title type is `ModelChoiceField`'
        assert not response.context['form'].fields['group'].required, \
            'Check that the `group` title is not required'

        assert 'text' in response.context['form'].fields, \
            'Check that the `form` have a `text` title'
        assert type(response.context['form'].fields['text']) == forms.fields.CharField, \
            'Check tha the `text` title type is `CharField`'
        assert response.context['form'].fields['text'].required, \
            'Check that the `group` title is required'

        assert 'image' in response.context['form'].fields, \
            'Check that the `form` have a `image` title'
        assert type(response.context['form'].fields['image']) == forms.fields.ImageField, \
            'Check that the `image` title type is `ImageField`'

    @staticmethod
    def get_image_file(name, ext='png', size=(50, 50), color=(256, 0, 0)):
        file_obj = BytesIO()
        image = Image.new("RGBA", size=size, color=color)
        image.save(file_obj, ext)
        file_obj.seek(0)
        return File(file_obj, name=name)

    @pytest.mark.django_db(transaction=True)
    def test_post_edit_view_author_post(self, user_client, post_with_group):
        text = 'Post changes check!'
        try:
            response = user_client.get(f'/{post_with_group.author.username}/{post_with_group.id}/edit')
        except Exception as e:
            assert False, f'''The page `/<username>/<post_id>/edit/` is not working properly. Error: `{e}`'''
        url = f'/{post_with_group.author.username}/{post_with_group.id}/edit/' if response.status_code in (301, 302) else f'/{post_with_group.author.username}/{post_with_group.id}/edit'

        image = self.get_image_file('image2.png')
        response = user_client.post(url, data={'text': text, 'group': post_with_group.group_id, 'image': image})

        assert response.status_code in (301, 302), \
            'Check the redirection to the post page after the post changed'
        post = Post.objects.filter(author=post_with_group.author, text=text, group=post_with_group.group).first()
        assert post is not None, \
            'Check the post has changed'
        assert response.url.startswith(f'/{post_with_group.author.username}/{post_with_group.id}'),\
            'Check the redirection to the page `/<username>/<post_id>/`'
