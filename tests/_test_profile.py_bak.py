import pytest

from django.core.paginator import Paginator, Page
from django.contrib.auth import get_user_model


def get_field_context(context, field_type):
    for field in context.keys():
        if field not in ('user', 'request') and type(context[field]) == field_type:
            return context[field]
    return


class TestProfileView:

    @pytest.mark.django_db(transaction=True)
    def test_profile_view_get(self, client, post_with_group):
        try:
            response = client.get(f'/{post_with_group.author.username}')
        except Exception as e:
            assert False, f'''`/<username>/` page is not working properly. Error: `{e}`'''
        if response.status_code in (301, 302):
            response = client.get(f'/{post_with_group.author.username}/')
        assert response.status_code != 404, '`/<username>/` page is not found, check it in *urls.py*'

        profile_context = get_field_context(response.context, get_user_model())
        assert profile_context is not None, 'Check that you put the author in the context of the page `/<username>/`'

        page_context = get_field_context(response.context, Page)
        assert page_context is not None, \
            "Check that you passed the author's articles into the context of the page `/<username>/`"
        assert len(page_context.object_list) == 1, \
            "Check that the author's correct articles are in the context of the `/<username>/' page"

        paginator_context = get_field_context(response.context, Paginator)
        assert paginator_context is not None, \
            'Check that you passed the paginator to the context of the page `/<username>/` of the `Paginator` type'

        new_user = get_user_model()(username='new_user_87123478')
        new_user.save()
        try:
            new_response = client.get(f'/{new_user.username}')
        except Exception as e:
            assert False, f'''`/<username>/` page is not working properly. Error: `{e}`'''
        if new_response.status_code in (301, 302):
            new_response = client.get(f'/{new_user.username}/')

        page_context = get_field_context(new_response.context, Page)
        assert page_context is not None, \
            "Check that you passed the author's articles into the context of the page `/<username>/` of the`Page` type'"
        assert len(page_context.object_list) == 0, \
            "Check that the author's correct articles are in the context of the `/<username>/' page"
