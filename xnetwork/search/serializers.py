from rest_framework import serializers
from .models import Query, ChatSession


# Create your models here.
class QueryTextSerializer(serializers.ModelSerializer):
    class Meta:
        model = Query
        fields = ('user', 'query_text', 'top_k')


class ChatSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatSession
        fields = ['user', 'session_id', 'conversation_history']
