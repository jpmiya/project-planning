from django.db import models

class Observation (models.Model):
    text = models.CharField(max_length=500)
    id_project = models.ForeignKey('Project', on_delete=models.CASCADE)
    ESTADO_PENDIENTE = 'Pendiente'
    ESTADO_RESUELTO = 'Resuelto'

    ESTADO_CHOICES = [
        (ESTADO_PENDIENTE, 'Pendiente'),
        (ESTADO_RESUELTO, 'Resuelto'),
    ]

    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default=ESTADO_PENDIENTE)
    
    def __str__(self):
        return "Observation " + self.text