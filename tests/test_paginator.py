import pytest

from django.core.paginator import Paginator, Page


class TestGroupPaginatorView:

    @pytest.mark.django_db(transaction=True)
    def test_group_paginator_view_get(self, client, post_with_group):
        try:
            response = client.get(f'/group/{post_with_group.group.slug}')
        except Exception as e:
            assert False, f'''The page `/group/<slug>/` is not working properly. Error: `{e}`'''
        if response.status_code in (301, 302):
            response = client.get(f'/group/{post_with_group.group.slug}/')
        assert response.status_code != 404, 'The page `/group/<slug>/` is not found, check it in *urls.py*'

        assert 'paginator' in response.context, \
            'Check that you passed the `paginator` variable into the context of the `/group/<slug>/` page'
        assert type(response.context['paginator']) == Paginator, \
            'Check that the `paginator` variable type `Paginator` on the `/group/<slug>/` page'
        assert 'page' in response.context, \
            'Check that you passed the `page` variable into the context of the `/group/<slug>/` page'
        assert type(response.context['page']) == Page, \
            'Check tha the `page` variable on the page `/group/<slug>/` is a `Page` type'

    @pytest.mark.django_db(transaction=True)
    def test_index_paginator_view_get(self, client, post_with_group):
        response = client.get(f'/')
        assert response.status_code != 404, 'The page `/` is not found, check it in *urls.py*'
        assert 'paginator' in response.context, \
            'Check that you passed the `paginator` variable into the context of the `/` page'
        assert type(response.context['paginator']) == Paginator, \
            'Check that the `paginator` variable type `Paginator` on the `/` page'
        assert 'page' in response.context, \
            'Check that you passed the `page` variable into the context of the `/` page'
        assert type(response.context['page']) == Page, \
            'Check tha the `page` variable on the page `/` is a `Page` type'
