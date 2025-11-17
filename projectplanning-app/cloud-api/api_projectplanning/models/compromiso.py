from django.db import models
from api_projectplanning.models.etapa import Etapa


class Compromiso(models.Model):
    nombre_ong_coolaboradora = models.CharField(max_length=255)
    ong_coolaboradora_id = models.IntegerField(null=False)
    etapa_back = models.ForeignKey(
        Etapa, 
        on_delete=models.CASCADE, 
        related_name='compromisos'
    )
    aporte = models.CharField(max_length=255)  # Qué aporta (dinero, materiales, horas, etc)
    cantidad = models.IntegerField(null=True, blank=True)
    fecha_compromiso = models.DateField(auto_now_add=True)
    cumplido = models.BooleanField(default=False)