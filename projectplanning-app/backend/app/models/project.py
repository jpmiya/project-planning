from django.db import models

class Project(models.Model):
    nombre = models.CharField(max_length=255)
    ong_responsable = models.CharField(max_length=255) #models.ForeignKey('Organization', on_delete=models.CASCADE)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    plan_economico = models.TextField()
    case_id = models.IntegerField(null=True, blank=True) # Clave en bonita del caso de proceso
    
    # Estado del proyecto: Pendiente | En ejecucion | Finalizado
    ESTADO_PENDIENTE = 'Pendiente'
    ESTADO_EN_EJECUCION = 'En ejecucion'
    ESTADO_FINALIZADO = 'Finalizado'

    ESTADO_CHOICES = [
        (ESTADO_PENDIENTE, 'Pendiente'),
        (ESTADO_EN_EJECUCION, 'En ejecucion'),
        (ESTADO_FINALIZADO, 'Finalizado'),
    ]

    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default=ESTADO_PENDIENTE)

    def __str__(self):
        return self.nombre
    
    
    def get_back_id(self) -> int:
        return self.id