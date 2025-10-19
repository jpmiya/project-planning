import datetime
import json
from django.http import JsonResponse
from django.shortcuts import render, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import jwt
from django.contrib.auth import authenticate
from api_core.settings import SECRET_KEY
from api_projectplanning.decorators import require_jwt
from api_projectplanning.serializers.etapa import EtapaSerializer
from api_projectplanning.serializers.proyecto import ProyectoSerializer
from api_projectplanning.serializers.compromiso import CompromisoSerializer, CumplidoSerializer
from api_projectplanning.models.compromiso import Compromiso


# Create your views here.

@csrf_exempt
@require_http_methods(["POST"])
def authenticate_user(request):
    try:
        data = json.loads(request.body.decode('utf-8'))
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return JsonResponse({'error': 'Faltan credenciales'}, status=400)

        # Valida contra la tabla User de Django
        user = authenticate(username=username, password=password)
        if user is None:
            return JsonResponse({'error': 'Credenciales inválidas'}, status=401)

        # Si es válido → generar el token
        now = datetime.datetime.now(datetime.timezone.utc)
        payload = {
            'id': user.id,
            'username': user.username,
            'exp': now + datetime.timedelta(hours=2),
            'iat': now
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')

        return JsonResponse({
            'token': token,
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
            }
        }, status=200)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@csrf_exempt
@require_jwt
def prueba(request):
    return JsonResponse({'data': 'joya'}, status=200)


@csrf_exempt
@require_http_methods(["POST"])
@require_jwt
def save_etapa(request):
    try:
        payload = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "JSON inválido"}, status=400)
    
    serializer = EtapaSerializer(data=payload)
    if serializer.is_valid():
        etapa = serializer.save()
        return JsonResponse({"id_etapa_cloud": etapa.id, "mensaje": "Etapa guardada"}, status=201)
    else:
        return JsonResponse(serializer.errors, status=400)
    """
    {
        "nombre": "Plantación Inicial",
        "aporte_necesario": "Arboles",
        "cantidad": 100,
        "id_back_etapa": "123",
        "id_proyecto_back": "001", 
        "fecha_inicio": "2025-10-21",
        "fecha_fin": "2025-11-10",
        "proyecto_cloud": 1
    }
    """

@csrf_exempt
@require_http_methods(["POST"])
@require_jwt
def save_proyecto(request):
    try:
        payload = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "JSON inválido"}, status=400)
    
    serializer = ProyectoSerializer(data=payload)
    if serializer.is_valid():
        proyecto = serializer.save()
        return JsonResponse({"id_proyecto_cloud": proyecto.id, "mensaje": "Proyecto guardado"}, status=201)
    else:
        return JsonResponse(serializer.errors, status=400)
    """
    {
        "nombre": "Plan de Reforestación",
        "ong_responsable": "EcoVida",
        "id_back_ong": "123",
        "id_back_proyecto": "123",
        "fecha_inicio": "2025-10-20",
        "fecha_fin": "2025-12-31",
        "case_id": "123"
    }
    """
    
@csrf_exempt
@require_http_methods(["POST"])
@require_jwt
def save_compromiso(request):
    try:
        payload = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "JSON inválido"}, status=400)
    
    serializer = CompromisoSerializer(data=payload)
    if serializer.is_valid():
        # Habra que verificar aca que el compromiso no es necesario? Es decir, si preciso 40 voluntarios
        # por ejemplo, y ya lo tengo, y me llega otro compromiso, debería bocharlo o ya se controla desde el back?
        compromiso = serializer.save()
        return JsonResponse({"id_compromiso_cloud": compromiso.id, "mensaje": "Compromiso guardado"}, status=201)
    else:
        return JsonResponse(serializer.errors, status=400)
    """
    {
        "etapa_cloud": 1,
        "nombre_ong_coolaboradora": "Fundación Manos Verdes",
        "id_ong_coolaboradora": "345",
        "id_etapa_back": "12",
        "aporte": "Voluntariado",
        "es_total": false,
        "cantidad": 10,
        "cumplido": false
    }
    """
    

@csrf_exempt
@require_http_methods(["POST"])
@require_jwt
def mark_cumplido_fulfilled(request):
    try:
        payload = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "JSON inválido"}, status=400)
    
    serializer = CumplidoSerializer(data=payload)
    if serializer.is_valid():
        id_compromiso = serializer.validated_data["id_compromiso"]
        cumplido = serializer.validated_data["cumplido"]

        try:
            compromiso = Compromiso.objects.get(id=id_compromiso)
        except Compromiso.DoesNotExist:
            return JsonResponse({"error": "Compromiso no encontrado"}, status=404)

        compromiso.cumplido = cumplido
        compromiso.save()
        return JsonResponse({"mensaje": "Estado de compromiso actualizado correctamente"}, status=200)

    return JsonResponse(serializer.errors, status=400)
"""
{
  "id_compromiso": 1,
  "cumplido": true
}
"""