from django.db import models

class Project(models.Model):
    nombre = models.CharField(max_length=255)
    ong_responsable = models.CharField(max_length=255)
    id_back_ong = models.CharField(max_length=255, null=False) # Id de la ong en la aplicación base
    id_back_proyecto = models.CharField(max_length=255, null=False, unique=True) # Id del proyecto en la aplicación base
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    case_id = models.CharField(max_length=255, null=False, unique=True)  # Clave en Bonita

    def __str__(self):
        return self.nombre