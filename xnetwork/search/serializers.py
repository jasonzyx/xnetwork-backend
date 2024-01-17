from rest_framework import serializers
from .models import Query


# Create your models here.
class QueryTextSerializer(serializers.ModelSerializer):
    class Meta:
        model = Query
        fields = ('user', 'query_text', 'top_k')
