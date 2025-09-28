from django.db import models
from models.proyecto import Proyecto

class Etapa(models.Model):
    id = models.AutoField(primary_key=True)
    nombre_etapa = models.CharField(max_length=50)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    disponible_para_ayudar = models.BooleanField(default=False)
    proyecto = models.ForeignKey(Proyecto, on_delete = models.CASCADE, related_name='etapas')
    
    def __str__(self):
        return "Etapa " + self.nombre_etapa
    