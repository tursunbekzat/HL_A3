from rest_framework import serializers
from .models import KeyValue

class KeyValueSerializer(serializers.ModelSerializer):
    class Meta:
        model = KeyValue
        fields = ['key', 'value', 'timestamp']
