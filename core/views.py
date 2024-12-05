# proxy/views.py
import random
import string
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import ProxyIotModel
from .serializers import ProxyIotModelSerializer
import uuid
from django.utils import timezone
from datetime import timedelta

class GenerateVerificationCodeView(APIView):
    def post(self, request):
        params = request.data.get('params', {})
        pairing_code = params.get('pairing_code')
        pairing_uuid = params.get('pairing_uuid')
        print(pairing_code, "pairing_codepairing_codepairing_code", pairing_uuid)

        if not pairing_code and not pairing_uuid:
            return self.create_new_pairing(self.generate_pairing_code(), self.generate_pairing_uuid())

        return self.handle_existing_pairing(pairing_code, pairing_uuid)

    def create_new_pairing(self, pairing_code, pairing_uuid):
        proxy_iot_instance = ProxyIotModel(pairing_code=pairing_code, pairing_uuid=pairing_uuid)
        proxy_iot_instance.save()
        serializer = ProxyIotModelSerializer(proxy_iot_instance)
        return Response({'result': serializer.data}, status=status.HTTP_200_OK)

    def handle_existing_pairing(self, pairing_code, pairing_uuid):
        record_data = ProxyIotModel.objects.filter(pairing_code=pairing_code, pairing_uuid=pairing_uuid).first()
        
        if record_data:
            if self.is_record_expired(record_data):
                # حذف السجل عند انتهاء الصلاحية
                record_data.delete()
                # إنشاء pairing_code جديد
                return self.create_new_pairing(self.generate_pairing_code(), self.generate_pairing_uuid)
            return self.return_existing_token(record_data)

        return Response({'result': {'pairing_code': pairing_code, 'pairing_uuid': pairing_uuid}}, status=status.HTTP_200_OK)

    def is_record_expired(self, record_data):
        return record_data.created_at < timezone.now() - timedelta(minutes=5)

    def return_existing_token(self, record_data):
        if record_data.token:
            return Response({'result': record_data.token}, status=status.HTTP_200_OK)
        return Response({'result': {'pairing_code': record_data.pairing_code, 'pairing_uuid': record_data.pairing_uuid}}, status=status.HTTP_200_OK)

    def generate_pairing_code(self):
        characters = string.ascii_uppercase + string.digits
        return ''.join(random.choice(characters) for _ in range(6))

    def generate_pairing_uuid(self):
        return str(uuid.uuid1())

class StoreHostDataView(APIView):
    def post(self, request):
        print("TTTTTTTTTTTTTTTTTTTTTTYYYYYYYYYYYYY")
        params = request.data.get('params', {})
        pairing_code = params.get('pairing_code')
        db_uuid = params.get('db_uuid', '')
        database_url = params.get('database_url', '')
        enterprise_code = params.get('enterprise_code', '')
        token = params.get('token', '')

        if not pairing_code:
            return Response({'error': 'Pairing code is required'}, status=status.HTTP_400_BAD_REQUEST)

        instance = ProxyIotModel.objects.filter(pairing_code=pairing_code).first()
        if instance:
            data = {
                'url': database_url,
                'token': token,
                'db_uuid': db_uuid,
                'enterprise_code': enterprise_code,
            }
            serializer = ProxyIotModelSerializer(instance, data={'token': data}, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({'result': 'ok'}, status=status.HTTP_200_OK)
            return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({'error': 'Pairing code not found'}, status=status.HTTP_404_NOT_FOUND)

# class RetrieveHostDataView(APIView):
#     def get(self, request, pairing_code):
#         try:
#             host_data = ProxyIotModel.objects.get(pairing_code=pairing_code)
#             return Response({'pairing_uuid': host_data.pairing_uuid, 'token': host_data.token}, status=status.HTTP_200_OK)
#         except ProxyIotModel.DoesNotExist:
#             return Response({'error': 'Pairing code not found'}, status=status.HTTP_404_NOT_FOUND)



