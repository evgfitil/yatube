from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from rest_framework.routers import DefaultRouter

from .views import CommentViewSet, FollowViewSet, GroupViewSet, PostViewSet


v1_router = DefaultRouter()
v1_router.register('posts', PostViewSet, basename='posts')
v1_router.register('group', GroupViewSet, basename='groups')
v1_router.register('follow', FollowViewSet, basename='follows')
v1_router.register(
    r'^posts/(?P<post_id>\d+)/comments',
    CommentViewSet,
    basename='comment'
)


urlpatterns = [
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('', include(v1_router.urls))
]
