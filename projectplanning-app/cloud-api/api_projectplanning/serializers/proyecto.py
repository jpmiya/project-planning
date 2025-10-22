from rest_framework import serializers
from api_projectplanning.models.proyecto import Project
from datetime import datetime

class ProyectoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = [
            'nombre', 
            'ong_responsable', 
            'id_back_ong', 
            'id_back_proyecto', 
            'fecha_inicio', 
            'fecha_fin', 
            'case_id'
        ]
        
        
    def validate_fecha_fin(self, value):
        fecha_inicio_str = self.initial_data.get('fecha_inicio')
        if fecha_inicio_str:
            fecha_inicio = datetime.strptime(fecha_inicio_str, "%Y-%m-%d").date()
            if value < fecha_inicio:
                raise serializers.ValidationError("La fecha_fin no puede ser anterior a fecha_inicio")
        return value