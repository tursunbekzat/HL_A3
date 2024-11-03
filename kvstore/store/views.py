from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import KeyValue
from .serializers import KeyValueSerializer
from django.shortcuts import get_object_or_404
import requests
from django.conf import settings
import logging
logger = logging.getLogger(__name__)

class KeyValueDetail(APIView):

    def get(self, request, key):
        R = 2  # Read quorum
        responses = []
        timestamps = []
        data = None

        # Attempt to read from local node
        try:
            kv = KeyValue.objects.get(key=key)
            responses.append({'value': kv.value, 'timestamp': kv.timestamp})
        except KeyValue.DoesNotExist:
            pass

        # Read from peer nodes
        for node in settings.PEER_NODES:
            try:
                url = f"{node}/api/kv/{key}/"
                response = requests.get(url, timeout=2)
                if response.status_code == 200:
                    resp_data = response.json()
                    responses.append({'value': resp_data['value'], 'timestamp': resp_data['timestamp']})
                if len(responses) >= R:
                    break
            except requests.exceptions.RequestException:
                continue

        if len(responses) >= R:
            # Select the value with the latest timestamp
            latest = max(responses, key=lambda x: x['timestamp'])
            return Response({'key': key, 'value': latest['value'], 'timestamp': latest['timestamp']})
        else:
            return Response({'error': 'Read quorum not achieved'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)


    def put(self, request, key):
        logger.info(f"Node {request.get_host()}: Received PUT request for key '{key}'.")
        # Update local node
        kv, _ = KeyValue.objects.get_or_create(key=key)
        serializer = KeyValueSerializer(kv, data=request.data)
        if serializer.is_valid():
            serializer.save()
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Quorum variables
        W = 2  # Write quorum
        success_count = 1  # Local write is successful
        data = serializer.data

        # Prepare data for forwarding
        payload = {
            'value': data['value'],
        }
        headers = {'Content-Type': 'application/json'}

        # Forward write to peer nodes
        for node in settings.PEER_NODES:
            try:
                url = f"{node}/api/kv/{key}/"
                response = requests.put(url, json=payload, headers=headers, timeout=2)
                if response.status_code == 200:
                    success_count += 1
                if success_count >= W:
                    break
            except requests.exceptions.RequestException:
                continue

        if success_count >= W:
            return Response(data, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Write quorum not achieved'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)


    def delete(self, request, key):
        kv = get_object_or_404(KeyValue, key=key)
        kv.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
