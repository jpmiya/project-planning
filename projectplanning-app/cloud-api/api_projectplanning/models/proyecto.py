from django.db import models

class Project(models.Model):
    # El ID del back será la PK
    id = models.IntegerField(primary_key=True)  # id_back_proyecto
    nombre = models.CharField(max_length=255)
    ong_responsable = models.CharField(max_length=255)
    id_back_ong = models.IntegerField(null=False)  # id de la ONG en el back
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    case_id = models.CharField(max_length=255, null=False, unique=True)  # ID de Bonita

    def __str__(self):
        return self.nombre