from django.db import models
from models.ong import ONG

class Proyecto(models.Model):
    id = models.AutoField(primary_key=True)
    nombre_proyecto = models.CharField(max_length=50)
    ong_originante = models.ForeignKey(ONG, on_delete = models.CASCADE, related_name='proyectos')
    case_id = models.CharField() # Es el id del proyecto en Bonita
    
    def __str__(self):
        return "Proyecto " + self.nombre_proyecto + " de la ONG " + self.ong_originante.nombre_ong