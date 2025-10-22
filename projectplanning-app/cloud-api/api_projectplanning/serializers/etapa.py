from rest_framework import serializers
from api_projectplanning.models.etapa import Etapa
from datetime import datetime

class EtapaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Etapa
        fields = [
            'nombre', 
            'aporte_necesario', 
            'cantidad', 
            'id_back_etapa', 
            'id_proyecto_back',
            'fecha_inicio', 
            'fecha_fin', 
            'proyecto_cloud'
        ]
        
        
    def validate_fecha_fin(self, value):
        fecha_inicio_str = self.initial_data.get('fecha_inicio')
        if fecha_inicio_str:
            fecha_inicio = datetime.strptime(fecha_inicio_str, "%Y-%m-%d").date()
            if value < fecha_inicio:
                raise serializers.ValidationError("La fecha_fin no puede ser anterior a fecha_inicio")
        return value
    
    
    def validate_cantidad(self, value):
        if value <= 0:
            raise serializers.ValidationError("La cantidad del aporte debe ser mayor a 0")
        return value
    

