from django.urls import path
from . import views

urlpatterns = [
    # main page
    path("", views.index, name="index"),
    # new post page
    path("new/", views.new_post, name="new_post"),
    # follow index page
    path('follow/', views.follow_index, name="follow_index"),
    # group page
    path("group/<slug:slug>/", views.group_posts, name="group_posts"),
    # user profile
    path("<username>/", views.profile, name="profile"),
    # profile follow and unfollow
    path("<username>/follow", views.profile_follow, name="profile_follow"),
    path(
        "<username>/unfollow", views.profile_unfollow,
        name="profile_unfollow"
    ),
    # view users posts
    path("<username>/<int:post_id>/", views.post_view, name="post"),
    path(
        "<username>/<int:post_id>/edit/", views.post_edit, name="post_edit"
    ),
    path(
        "<username>/<int:post_id>/delete/", views.post_delete,
        name="post_delete"
    ),
    # comments
    path(
        "<username>/<int:post_id>/comment", views.add_comment,
        name="add_comment"
    )
]
