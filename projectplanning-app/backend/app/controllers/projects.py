from django.db import models
from datetime import datetime

from app.models.etapa import Etapa
from app.models.project import Project


def save_project(data):
    etapas_creadas = []
    
    for nombre_etapa, info_etapa in data['etapas'].items():
        # Convertir string de ayuda a booleano
        requiere_ayuda = info_etapa['ayuda'].lower() == 'true'
        
        etapa = Etapa.objects.create(
            nombre=nombre_etapa,  # La clave del diccionario es el nombre
            fecha_inicio=info_etapa['inicio'],
            fecha_fin=info_etapa['fin'], 
            requiere_ayuda=requiere_ayuda  # Convertir string a booleano
        )
        etapas_creadas.append(etapa)
    
    project = Project(
        nombre=data['nombre'],        
        ong_responsable=data['ong_responsable'],
        fecha_inicio=data['fecha_inicio'],
        fecha_fin=data['fecha_fin'],
        plan_economico=data['plan_economico']
    )
    project.save()
    
    project.etapas.set(etapas_creadas)