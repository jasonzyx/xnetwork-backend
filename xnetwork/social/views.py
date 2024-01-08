# views.py
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.http import JsonResponse
from rest_framework import status
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Post, Comment, Like, FriendRequest, Friend, Profile
from .serializers import PostSerializer, CommentSerializer, LikeSerializer, FriendRequestSerializer, FriendSerializer, \
    ProfileSerializer
from .serializers import UserSerializer
from django.contrib.auth.hashers import check_password


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    @action(detail=True, methods=['post'], url_path='update-profile')
    def update_profile(self, request, pk=None):
        user = self.get_object()
        user_serializer = UserSerializer(user, data=request.data, partial=True)

        if user_serializer.is_valid():
            user_serializer.save()

            profile_data = request.data.get('profile')
            if profile_data:
                profile, created = Profile.objects.get_or_create(user=user)
                profile_serializer = ProfileSerializer(profile, data=profile_data, partial=True)

                if profile_serializer.is_valid():
                    profile_serializer.save()
                    return Response({
                        'user': user_serializer.data,
                        'profile': profile_serializer.data
                    })
                else:
                    return Response(profile_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response(user_serializer.data)
        else:
            print("serializer error: ")
            print(user_serializer.errors)
            # Return a response if user_serializer is not valid
            return Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'], url_path='change-password')
    def change_password(self, request, pk=None):
        user = self.get_object()
        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')

        if not check_password(old_password, user.password):
            return Response({'old_password': ['Wrong password.']}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(new_password)
        user.save()
        return Response({'message': 'Password updated successfully'})

    @action(methods=['post'], detail=False)
    def login(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return JsonResponse({'message': 'Login successful'})
        else:
            return JsonResponse({'message': 'Invalid username or password'}, status=401)

    @action(detail=False, methods=['post'], url_path='register')
    def register(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']
            password = serializer.validated_data['password']

            # Create a new user
            user = User.objects.create_user(username=username, password=password)

            return JsonResponse({'message': 'User created successfully'})
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer


class LikeViewSet(viewsets.ModelViewSet):
    queryset = Like.objects.all()
    serializer_class = LikeSerializer


class FriendRequestViewSet(viewsets.ModelViewSet):
    queryset = FriendRequest.objects.all()
    serializer_class = FriendRequestSerializer

    @action(detail=True, methods=['post'])
    def accept(self, request, pk=None):
        friend_request = self.get_object()
        # Create new Friends instances for each direction of the friendship
        Friend.objects.create(user=friend_request.from_user, friend=friend_request.to_user)
        Friend.objects.create(user=friend_request.to_user, friend=friend_request.from_user)
        # Delete the friend request
        friend_request.delete()
        return Response('Friend request accepted')

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        friend_request = self.get_object()
        friend_request.delete()
        return Response('Friend request rejected')


class FriendViewSet(viewsets.ModelViewSet):
    queryset = Friend.objects.all()
    serializer_class = FriendSerializer
