from django.db import models
from .project import Project

class Etapa(models.Model):
    nombre = models.CharField(max_length=50)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    disponible_para_ayudar = models.BooleanField(default=False)
    proyecto = models.ForeignKey(Project, on_delete = models.CASCADE, related_name='etapas')
    
    def __str__(self):
        return "Etapa " + self.nombre_etapa
    