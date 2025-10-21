from rest_framework import serializers
from api_projectplanning.models.compromiso import Compromiso
from datetime import date


class CompromisoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Compromiso
        fields = [
            'etapa_cloud', 
            'id_ong_coolaboradora',
            'id_etapa_back', 
            'aporte', 
            'es_total', 
            'cantidad',
            'fecha_compromiso',
            'cumplido'
        ]
        
        
    def validate_cantidad(self, value):
        if value <= 0:
            raise serializers.ValidationError("La cantidad del aporte debe ser mayor a 0")
        return value
    
    
    def validate_fecha_compromiso(self, value):
        if value < date.today():
            raise serializers.ValidationError("La fecha de compromiso debe ser la actual")
        return value
    

class CumplidoSerializer(serializers.Serializer):
    id_compromiso = serializers.IntegerField()
    cumplido = serializers.BooleanField()


class GetCompromisosSerializer(serializers.Serializer):
    id_proyecto_back = serializers.CharField()