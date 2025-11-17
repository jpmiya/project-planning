from django.db import models

class Project(models.Model):
    nombre = models.CharField(max_length=255)
    ong_responsable = models.CharField(max_length=255)
    ong_back_id = models.IntegerField() # Id de la ong en la aplicación base
    proyecto_back_id = models.IntegerField(primary_key=True) # Id del proyecto en la aplicación base
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    case_id = models.IntegerField(unique=True)  # Clave en Bonita

    def __str__(self):
        return self.nombre