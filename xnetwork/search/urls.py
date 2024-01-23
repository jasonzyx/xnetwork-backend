from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SearchAPIViewSet, ChatSessionViewSet

router = DefaultRouter()
router.register('search_api', SearchAPIViewSet, basename='search_api')
router.register('chat_api', ChatSessionViewSet, basename='chat_api')

urlpatterns = [
    # ... your other URL patterns ...
    path('', include(router.urls)),
]
