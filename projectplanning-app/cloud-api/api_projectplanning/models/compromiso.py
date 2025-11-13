from django.db import models
from models.etapa import Etapa


class Compromiso(models.Model):
    id_etapa = models.ForeignKey(Etapa, on_delete=models.CASCADE, related_name='compromisos')
    nombre_ong_coolaboradora = models.CharField(max_length=255)
    id_ong_coolaboradora = models.IntegerField(null=False)  # ID de ONG en el back
    aporte = models.CharField(max_length=255)
    cantidad = models.IntegerField(null=True, blank=True)
    fecha_compromiso = models.DateField(auto_now_add=True)
    cumplido = models.BooleanField(default=False)

    def __str__(self):
        return f"Compromiso de {self.nombre_ong_coolaboradora} para {self.etapa.nombre}"