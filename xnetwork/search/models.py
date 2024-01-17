from django.db import models
from django.contrib.auth.models import User


class Query(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    query_text = models.TextField(blank=True, null=True)
    top_k = models.IntegerField(default=10)

