from django.db import models
from api_projectplanning.models.proyecto import Project


class Etapa(models.Model):
    nombre = models.CharField(max_length=255)
    aporte_necesario = models.TextField()
    cantidad = models.IntegerField(default=0)
    etapa_back_id = models.IntegerField(primary_key=True) # Id de etapa en la aplicación base
    proyecto_back = models.ForeignKey(
        Project, 
        on_delete=models.CASCADE, 
        db_column='id_proyecto_back', 
        related_name='etapas'
    ) # Id de proyecto al que pertenece en la aplicación base
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()

    def __str__(self):
        return self.nombre