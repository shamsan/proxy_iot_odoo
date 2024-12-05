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
        params = request.data.get('params')
        pairing_code = params.get('pairing_code')
        pairing_uuid = params.get('pairing_uuid')

        # التحقق من أن القيم موجودة
        if not pairing_code and not pairing_uuid:
            pairing_code = self.generate_pairing_code()
            pairing_uuid = self.generate_pairing_uuid()
            ProxyIotModel.objects.create(
                pairing_code=pairing_code,
                pairing_uuid=pairing_uuid,
            )
            return Response({'result': {'pairing_code':pairing_code, 'pairing_uuid': pairing_uuid}}, status=status.HTTP_200_OK)

        record_data = ProxyIotModel.objects.filter(pairing_code=pairing_code, pairing_uuid=pairing_uuid).first()
        if record_data:
            if record_data.created_at < timezone.now() - timedelta(minutes=5):
                ProxyIotModel.objects.filter(pairing_code=pairing_code, pairing_uuid=pairing_uuid).delete()
                pairing_code = self.generate_pairing_code()
                pairing_uuid = self.generate_pairing_uuid()
                ProxyIotModel.objects.create(
                    pairing_code=pairing_code,
                    pairing_uuid=pairing_uuid,
                )
                return Response({'result': {'pairing_code':pairing_code, 'pairing_uuid': pairing_uuid}}, status=status.HTTP_200_OK)
        
        if record_data.token:
            token = record_data.token
            data = {
                'url':token['url'],
                'token':token['token'],
                'db_uuid':token['db_uuid'],
                'enterprise_code':token['enterprise_code'],
            }
            return Response({'result': data}, status=status.HTTP_200_OK)
        return Response({'result': {'pairing_code':pairing_code, 'pairing_uuid': pairing_uuid}}, status=status.HTTP_200_OK)
    
    def generate_pairing_code(self):
        # توليد كود اقتران عشوائي مكون من 6 حروف وأرقام
        characters = string.ascii_uppercase + string.digits
        pairing_code = ''.join(random.choice(characters) for _ in range(6))
        return pairing_code
    
    def generate_pairing_uuid(self):
        # توليد UUID فريد
        pairing_uuid = str(uuid.uuid1())
        return pairing_uuid  

class StoreHostDataView(APIView):
    def post(self, request):
        print(request.data,"BBBBBBBBBBBBBBNNNNNNNNNNNNBBBBBBBBBBBBBBB")
        params = request.data.get('params')
        pairing_code = params.get('pairing_code', False)
        db_uuid = params.get('db_uuid', '')
        database_url = params.get('database_url', False)
        enterprise_code = params.get('enterprise_code', False)
        token = params.get('token', '')
        data = {
            'url':database_url,
            'token':token,
            'db_uuid':db_uuid,
            'enterprise_code':enterprise_code,
        }
        if ProxyIotModel.objects.filter(pairing_code=pairing_code).first():
            ProxyIotModel.objects.filter(pairing_code=pairing_code).update(token=data)
            return Response({'result': 'ok'}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Pairing code not found'}, status=status.HTTP_404_NOT_FOUND) 

class RetrieveHostDataView(APIView):
    def get(self, request, pairing_code):
        try:
            host_data = ProxyIotModel.objects.get(pairing_code=pairing_code)
            return Response({'pairing_uuid': host_data.pairing_uuid, 'token': host_data.token}, status=status.HTTP_200_OK)
        except ProxyIotModel.DoesNotExist:
            return Response({'error': 'Pairing code not found'}, status=status.HTTP_404_NOT_FOUND)

            