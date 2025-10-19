from django.db import models


class Compromiso(models.Model):
    etapa_cloud = models.ForeignKey('Etapa', on_delete=models.CASCADE, related_name='compromisos')
    nombre_ong_coolaboradora = models.CharField(max_length=255)
    id_ong_coolaboradora = models.CharField(max_length=255, null=False)
    id_etapa_back = models.CharField(max_length=255, null=False)
    aporte = models.CharField(max_length=255)  # Qué aporta (dinero, materiales, horas, etc)
    es_total = models.BooleanField(default=False)
    cantidad = models.IntegerField(null=True, blank=True)
    fecha_compromiso = models.DateField(auto_now_add=True)
    cumplido = models.BooleanField(default=False)

    def __str__(self):
        return f"Compromiso de {self.nombre_ong_coolaboradora} para {self.etapa.nombre}"