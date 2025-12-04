from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import generics

from django.http import HttpRequest
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404

from .models import Follower
from .serializers import (
    FollowSerializer, 
    AvatarSerializer,
    ChangePasswordSerializer
)


User = get_user_model()


class FollowToUserAPIView(APIView):
    """APIView для подписки на пользователя"""

    def post(self, request: HttpRequest, *args, **kwargs):
        user_to_follow = get_object_or_404(
            User,
            pk=kwargs['id']
        )
        current_user = request.user

        is_subscribed = Follower.objects.filter(
            subscriber=current_user,
            subscribed=user_to_follow
        ).exists()

        if (
            current_user == user_to_follow
            or is_subscribed
        ):
            return Response(
                data={
                    'detail': 'Ошибка подписки'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        Follower.objects.create(
            subscriber=current_user,
            subscribed=user_to_follow
        )
        serializer = FollowSerializer(
            user_to_follow
        )
        return Response(
            data=serializer.data,
            status=status.HTTP_201_CREATED
        )
    
    def delete(self, request: HttpRequest, *args, **kwargs):
        user_to_unfollow = get_object_or_404(
            User,
            pk=kwargs['id']
        )
        current_user = request.user

        follow = Follower.objects.filter(
            subscriber=current_user,
            subscribed=user_to_unfollow
        ).first()

        if not follow:
            return Response(
                data={
                    'detail': 'Ошибка отписки'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        follow.delete()
        return Response(
            status=status.HTTP_204_NO_CONTENT
        )
    

class FollowListAPIView(generics.ListAPIView):
    """APIView для вывода подписок"""

    serializer_class = FollowSerializer

    def get_queryset(self):
        current_user = self.request.user
        return User.objects.filter(
            subscribers__subscriber=current_user
        )
    

class AvatarAPIView(APIView):
    """APIView для обновления аватара пользователя"""

    def put(self, request: HttpRequest, *args, **kwargs):
        current_user = request.user
        current_user.avatar.delete(save=False)
        serializer = AvatarSerializer(
            current_user,
            data=request.data,
            partial=True,
            context={'request': request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(
                data=serializer.data,
                status=status.HTTP_200_OK
            )
        return Response(
            data=serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )
    
    def delete(self, request: HttpRequest, *args, **kwargs):
        current_user = request.user

        if current_user.avatar:
            current_user.avatar.delete()
        
        return Response(
            status=status.HTTP_204_NO_CONTENT
        )


class ChangePasswordAPIView(APIView):
    """APIView для смены пароля пользователя"""

    def post(self, request: HttpRequest, *args, **kwargs):
        serializer = ChangePasswordSerializer(
            data=request.data,
            context={'request': request}
        )
        user = request.user

        if serializer.is_valid():
            if isinstance(user, User):
                user.set_password(
                    serializer.validated_data.get('new_password')
                )
                user.save()
                return Response(status=status.HTTP_204_NO_CONTENT)
            
        return Response(
            data=serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )
