from django.urls import path
from .views import KeyValueDetail

urlpatterns = [
    path('kv/<str:key>/', KeyValueDetail.as_view(), name='keyvalue-detail'),
]
