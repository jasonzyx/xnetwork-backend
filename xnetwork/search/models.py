from django.db import models
from django.contrib.auth.models import User
import uuid


class Query(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    query_text = models.TextField(blank=True, null=True)
    top_k = models.IntegerField(default=10)


class ChatSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    session_id = models.CharField(max_length=100, unique=True, default=uuid.uuid4)
    conversation_history = models.TextField()

    def __str__(self):
        return self.session_id

    def save(self, *args, **kwargs):
        if not self.session_id:
            # Generate a new session_id if it's not set yet
            self.session_id = str(uuid.uuid4())
        super(ChatSession, self).save(*args, **kwargs)
