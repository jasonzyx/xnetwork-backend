# views.py
from rest_framework import viewsets
from django.contrib.auth.models import User
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from .models import Post, Comment, Like, FriendRequest, Friend
from .serializers import PostSerializer, CommentSerializer, LikeSerializer, FriendRequestSerializer, FriendSerializer
from .serializers import UserSerializer
from django.contrib.auth import authenticate, login
from django.http import JsonResponse


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

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
