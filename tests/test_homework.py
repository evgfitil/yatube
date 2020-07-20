import re
import tempfile

import pytest
from django.contrib.admin.sites import site
from django.contrib.auth import get_user_model
from django.db.models import fields

try:
    from posts.models import Post
except ImportError:
    assert False, 'The Post model is not found'

try:
    from posts.models import Group
except ImportError:
    assert False, 'The Group model is not found'


def search_field(fields, attname):
    for field in fields:
        if attname == field.attname:
            return field
    return None


def search_refind(execution, user_code):
    """Поиск запуска"""
    for temp_line in user_code.split('\n'):
        if re.search(execution, temp_line):
            return True
    return False


class TestPost:

    def test_post_model(self):
        model_fields = Post._meta.fields
        text_field = search_field(model_fields, 'text')
        assert text_field is not None, 'Add the `text` attribute of the `Post` model'
        assert type(text_field) == fields.TextField, \
            'The `text` attribute of the `Post` model must be an `TextField`'

        pub_date_field = search_field(model_fields, 'pub_date')
        assert pub_date_field is not None, 'Add the `pub_date` attribute of the `Post` model'
        assert type(pub_date_field) == fields.DateTimeField, \
            'The `pub_date` attribute of the `Post` model must be an `DateTimeField`'
        assert pub_date_field.auto_now_add, 'The `pub_date` attribute of the `Post` model must be an `auto_now_add`'

        author_field = search_field(model_fields, 'author_id')
        assert author_field is not None, 'Add the user who created the event `author` of the `Post` model'
        assert type(author_field) == fields.related.ForeignKey, \
            'The `author` attribute of the `Post` model must be an `ForeignKey`'
        assert author_field.related_model == get_user_model(), \
            'The `author` attribute of the `Post` model must be a refference to the `User` model'

        group_field = search_field(model_fields, 'group_id')
        assert group_field is not None, 'Add the `group` attribute to a `Post` model'
        assert type(group_field) == fields.related.ForeignKey, \
            'The `group` attribute of the `Post` model must be an `ForeignKey`'
        assert group_field.related_model == Group, \
            'The `group` attribute of the `Post` model must be a refference to the `Group` model'
        assert group_field.blank, \
            'The `group` attribute of the `Post` model should have a `blank=True`'
        assert group_field.null, \
            'The `group` attribute of the `Post` model should have a `null=True`'

        image_field = search_field(model_fields, 'image')
        assert image_field is not None, 'Add the `image` attribute to a `Post` model'
        assert type(image_field) == fields.files.ImageField, \
            'The `image` attribute of the `Post` model must be an `ImageField`'
        assert image_field.upload_to == 'posts/', \
            "The `image` attribute of the `Post` model should have a `upload_to='posts/'`"

    @pytest.mark.django_db(transaction=True)
    def test_post_create(self, user):
        text = 'Test post'
        author = user

        assert Post.objects.all().count() == 0

        image = tempfile.NamedTemporaryFile(suffix=".jpg").name
        post = Post.objects.create(text=text, author=author, image=image)
        assert Post.objects.all().count() == 1
        assert Post.objects.get(text=text, author=author).pk == post.pk

    def test_post_admin(self):
        admin_site = site

        assert Post in admin_site._registry, 'Register the model `Post` in the admin panel'

        admin_model = admin_site._registry[Post]

        assert 'text' in admin_model.list_display, \
            'Add the `text` in PostAdmin'
        assert 'pub_date' in admin_model.list_display, \
            'Add the `pub_date` in PostAdmin'
        assert 'author' in admin_model.list_display, \
            'Add the `author` in PostAdmin'

        assert 'text' in admin_model.search_fields, \
            'Add the `text` in PostAdmin search field'

        assert 'pub_date' in admin_model.list_filter, \
            'Add the `pub_date` in PostAdmin filters'

        assert hasattr(admin_model, 'empty_value_display'), \
            'Add the default value `-empty-` for the blank field'
        assert admin_model.empty_value_display == '-empty-', \
            'Add the default value `-empty-` for the blank field'


class TestGroup:

    def test_group_model(self):
        model_fields = Group._meta.fields
        title_field = search_field(model_fields, 'title')
        assert title_field is not None, 'Add the `title` attribute of the `Group` model'
        assert type(title_field) == fields.CharField, \
            'The `title` attribute of the `Group` model must be an `CharField`'
        assert title_field.max_length == 200, 'The `title` attribute of the `Group` model should have max lenght 200'

        slug_field = search_field(model_fields, 'slug')
        assert slug_field is not None, 'Add the `slug` attribute of the `Group` model'
        assert type(slug_field) == fields.SlugField, \
            'The `slug` attribute of the `Group` model should be an `SlugField`'
        assert slug_field.unique, 'The `slug` attribute of the `Group` model must be unique'

        description_field = search_field(model_fields, 'description')
        assert description_field is not None, 'Add the `description` attribute of the `Group` model'
        assert type(description_field) == fields.TextField, \
            'The `description` attribute of the `Group` model must be an `TextField`'

    @pytest.mark.django_db(transaction=True)
    def test_group_create(self, user):
        text = 'Test post'
        author = user

        assert Post.objects.all().count() == 0

        post = Post.objects.create(text=text, author=author)
        assert Post.objects.all().count() == 1
        assert Post.objects.get(text=text, author=author).pk == post.pk

        title = 'Test group'
        slug = 'test-link'
        description = 'Test group description'

        assert Group.objects.all().count() == 0
        group = Group.objects.create(title=title, slug=slug, description=description)
        assert Group.objects.all().count() == 1
        assert Group.objects.get(slug=slug).pk == group.pk

        post.group = group
        post.save()
        assert Post.objects.get(text=text, author=author).group == group


class TestGroupView:

    @pytest.mark.django_db(transaction=True)
    def test_group_view(self, client, post_with_group):
        try:
            response = client.get(f'/group/{post_with_group.group.slug}')
        except Exception as e:
            assert False, f'''The page `/group/<slug>/` is not working properly. Error: `{e}`'''
        if response.status_code in (301, 302):
            response = client.get(f'/group/{post_with_group.group.slug}/')
        if response.status_code == 404:
            assert False, 'The page `/group/<slug>/` is not found, check it in *urls.py*'

        if response.status_code != 200:
            assert False, 'The page `/group/<slug>/` is not working properly'
