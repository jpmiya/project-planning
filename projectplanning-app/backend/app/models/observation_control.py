from django.db import models
from django.contrib.auth.models import User


class ObservacionControl(models.Model):
    mes = models.IntegerField()  # 1 a 12
    anio = models.IntegerField()
    usuario = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='observaciones'
    )
    cantidad_intentos = models.IntegerField(default=0)
    
    class Meta:
        unique_together = ('mes', 'anio', 'usuario')

