from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import KeyValue
from .serializers import KeyValueSerializer
from django.shortcuts import get_object_or_404

class KeyValueDetail(APIView):
    def get(self, request, key):
        kv = get_object_or_404(KeyValue, key=key)
        serializer = KeyValueSerializer(kv)
        return Response(serializer.data)

    def put(self, request, key):
        kv, created = KeyValue.objects.get_or_create(key=key)
        serializer = KeyValueSerializer(kv, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, key):
        kv = get_object_or_404(KeyValue, key=key)
        kv.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
