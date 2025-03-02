from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now  # ✅ Import timezone

class Summary(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # ✅ Link to user
    text = models.TextField()
    embedding_id = models.CharField(max_length=100, unique=True)
    category = models.CharField(max_length=50, blank=True)  # ✅ Allow category filtering
    created_at = models.DateTimeField(default = now)  # ✅ Temporarily allow NULL

    def __str__(self):
        return self.text[:50]
