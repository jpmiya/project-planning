from django.db import models
from django.contrib.auth.models import User

class Project(models.Model):
    nombre = models.CharField(max_length=255)
    ong_responsable = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='proyectos'
    )
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    plan_economico = models.TextField()
    case_id = models.IntegerField(null=True, blank=True) # Clave en bonita del caso de proceso
    
    # ONGs colaboradoras que aportaron/ayudaron en este proyecto
    ongs_colaboradoras = models.ManyToManyField(
        User,
        related_name='proyectos_colaborados',
        blank=True,
        help_text='ONGs que han colaborado/aportado en este proyecto'
    )
    
    # Estado del proyecto: Pendiente | En ejecucion | Finalizado
    ESTADO_PENDIENTE = 'Pendiente'
    ESTADO_CUBIERTO = 'Cubierto'
    ESTADO_EN_EJECUCION = 'En ejecucion'
    ESTADO_FINALIZADO = 'Finalizado'

    ESTADO_CHOICES = [
        (ESTADO_PENDIENTE, 'Pendiente'),
        (ESTADO_CUBIERTO, 'Cubierto'),
        (ESTADO_EN_EJECUCION, 'En ejecucion'),
        (ESTADO_FINALIZADO, 'Finalizado'),
    ]

    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default=ESTADO_PENDIENTE)

    def __str__(self):
        return self.nombre
    
    
    def get_back_id(self) -> int:
        return self.id