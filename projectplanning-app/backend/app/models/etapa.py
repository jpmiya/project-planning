from django.db import models


class Etapa(models.Model):
    nombre = models.CharField(max_length=255)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    requiere_ayuda = models.BooleanField(default=False)
    # Seguro hay que agregar el proyecto al que pertenece

    def __str__(self):
        return self.nombre

