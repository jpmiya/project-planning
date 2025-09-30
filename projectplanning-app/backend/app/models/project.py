from django.db import models

class Project(models.Model):
    nombre = models.CharField(max_length=255)
    ong_responsable = models.CharField(max_length=255) #models.ForeignKey('Organization', on_delete=models.CASCADE)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    plan_economico = models.TextField()
    etapas = models.ManyToManyField('Etapa', blank=True)

    def __str__(self):
        return self.nombre