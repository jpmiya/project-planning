from django.db import models


class Etapa(models.Model):
    nombre_etapa = models.CharField(max_length=255)
    nombre_aporte = models.CharField(max_length=255)
    cant_aporte_necesario = models.IntegerField()
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    requiere_ayuda = models.BooleanField(default=False)
    cloud_id = models.IntegerField(null=True, blank=True)
    # Seguro hay que agregar el proyecto al que pertenece

    def __str__(self):
        return self.nombre_aporte

