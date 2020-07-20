from io import BytesIO

import pytest
from PIL import Image
from django import forms
from django.core.files.base import File
from posts.models import Post


class TestNewView:

    @pytest.mark.django_db(transaction=True)
    def test_new_view_get(self, user_client):
        try:
            response = user_client.get('/new')
        except Exception as e:
            assert False, f'''The page `/new` is not working properly. Error: `{e}`'''
        if response.status_code in (301, 302):
            response = user_client.get('/new/')
        assert response.status_code != 404, 'The `/new/` page is not found, check it in *urls.py*'
        assert 'form' in response.context, 'Check that you passed the `form` variable into the context of the `/new/` page'
        assert len(response.context['form'].fields) == 3, 'Check that the `form` on the `/new/` page have a 3 title'
        assert 'group' in response.context['form'].fields, \
            'Check that the `form` on the `new` page have a `group` title'
        assert type(response.context['form'].fields['group']) == forms.models.ModelChoiceField, \
            'Check that the `form` on the `new` page have a `group` title with `ModelChoiceField` type'
        assert not response.context['form'].fields['group'].required, \
            'Check that the `group` title is not required'

        assert 'text' in response.context['form'].fields, \
            'Check that the `form` on the `new` page have a `text` title'
        assert type(response.context['form'].fields['text']) == forms.fields.CharField, \
            'Check that the `form` on the `new` page have a `text` title with `CharField` type'
        assert response.context['form'].fields['text'].required, \
            'Check that the `text` title is required'

        assert 'image' in response.context['form'].fields, \
            'Check that the `form` on the `new` page have a `image` title'
        assert type(response.context['form'].fields['image']) == forms.fields.ImageField, \
            'Check that the `form` on the `new` page have a `image` title with `ImageField` type'

    @staticmethod
    def get_image_file(name, ext='png', size=(50, 50), color=(256, 0, 0)):
        file_obj = BytesIO()
        image = Image.new("RGBA", size=size, color=color)
        image.save(file_obj, ext)
        file_obj.seek(0)
        return File(file_obj, name=name)

    @pytest.mark.django_db(transaction=True)
    def test_new_view_post(self, user_client, user, group):
        text = 'New post check!'
        try:
            response = user_client.get('/new')
        except Exception as e:
            assert False, f'''The `/new` page is not working properly. Error: `{e}`'''
        url = '/new/' if response.status_code in (301, 302) else '/new'

        image = self.get_image_file('image.png')
        response = user_client.post(url, data={'text': text, 'group': group.id, 'image': image})

        assert response.status_code in (301, 302), \
            'Check the redirection to the homepage after the post creation'
        post = Post.objects.filter(author=user, text=text, group=group).first()
        assert post is not None, 'Check that the post is saved'
        assert response.url == '/', 'Check the redirection to the homepage `/`'

        text = 'New post check 2!'
        image = self.get_image_file('image2.png')
        response = user_client.post(url, data={'text': text, 'image': image})
        assert response.status_code in (301, 302), \
            'Check the redirection to the homepage after the post creation'
        post = Post.objects.filter(author=user, text=text, group__isnull=True).first()
        assert post is not None, 'Check that the post is saved'
        assert response.url == '/', 'Check the redirection to the homepage `/`'

        response = user_client.post(url)
        assert response.status_code == 200, \
            'Check that on-page `/new/` you are outputting errors if the form `form` is not completed correctly'
