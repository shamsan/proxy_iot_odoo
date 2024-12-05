# serializers.py
from rest_framework import serializers
from .models import ProxyIotModel

class ProxyIotModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProxyIotModel
        fields = ['pairing_code', 'pairing_uuid', 'token','created_at']