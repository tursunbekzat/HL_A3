from django.db import models

class KeyValue(models.Model):
    key = models.CharField(max_length=255, unique=True)
    value = models.TextField()
    timestamp = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.key}: {self.value}"
