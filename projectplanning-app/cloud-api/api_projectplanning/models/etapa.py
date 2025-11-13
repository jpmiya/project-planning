from django.db import models
from .proyecto import Project


class Etapa(models.Model):
    # ID del back será la PK
    id = models.IntegerField(primary_key=True)  # id_back_etapa
    nombre = models.CharField(max_length=255)
    aporte_necesario = models.TextField()
    cantidad = models.IntegerField(default=0)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()

    # Relación directa con el proyecto (por su ID de back)
    proyecto = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='etapas')

    def __str__(self):
        return self.nombre