from rest_framework.routers import DefaultRouter
from .views import PostViewSet, UserViewSet, CommentViewSet, LikeViewSet, FriendRequestViewSet, FriendViewSet

router = DefaultRouter()
router.register('posts', PostViewSet)
router.register('users', UserViewSet)
router.register('comments', CommentViewSet)
router.register('likes', LikeViewSet)
router.register('friends', FriendViewSet)
router.register('friend_request', FriendRequestViewSet)


# Do the same for the Comment, Like, FriendRequest, and Friend models

urlpatterns = router.urls
