from django.urls import path

from .views import (
    FollowToUserAPIView, FollowListAPIView,
    AvatarAPIView, ChangePasswordAPIView
)


urlpatterns = [
    path(
        '<int:id>/subscribe/',
        FollowToUserAPIView.as_view(),
        name='follow_to_user'
    ),
    path('subscriptions/', FollowListAPIView.as_view()),
    path('me/avatar/', AvatarAPIView.as_view()),
    path('set_password/', ChangePasswordAPIView.as_view())
]
