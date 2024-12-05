from django.db import models

# Create your models here.

class ProxyIotModel(models.Model):
    pairing_code = models.CharField(max_length=255)
    pairing_uuid = models.CharField(max_length=255)
    token = models.JSONField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.pairing_code} - {self.pairing_uuid}"
