from django.db import models


class Etapa(models.Model):
    nombre = models.CharField(max_length=255)
    aporte_necesario = models.TextField()
    cantidad = models.IntegerField(default=0)
    id_back_etapa = models.CharField(max_length=255, null=False) # Id de etapa en la aplicación base
    id_proyecto_back = models.CharField(max_length=255, null=False) # Id de proyecto al que pertenece en la aplicación base
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    proyecto_cloud = models.ForeignKey("Project", on_delete=models.CASCADE, related_name="etapas")

    def __str__(self):
        return self.nombre