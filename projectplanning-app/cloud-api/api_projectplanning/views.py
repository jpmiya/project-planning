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
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.decorators import api_view
from rest_framework.response import Response


# Create your views here.
@swagger_auto_schema(
    method='post',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['username', 'password'],
        properties={
            'username': openapi.Schema(type=openapi.TYPE_STRING),
            'password': openapi.Schema(type=openapi.TYPE_STRING),
        }
    ),
    responses={
        200: "Token generado correctamente",
        401: "Credenciales inválidas",
        400: "Solicitud incorrecta"
    }
)
@api_view(['POST'])
@csrf_exempt
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


@swagger_auto_schema(
    method='post',
    manual_parameters=[
        openapi.Parameter(
            'Authorization',
            in_=openapi.IN_HEADER,
            description="Token JWT. Formato: Bearer <token>",
            type=openapi.TYPE_STRING
        )
    ],
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['nombre', 'aporte_necesario', 'cantidad', 'id_back_etapa', 'id_proyecto_back', 'fecha_inicio', 'fecha_fin', 'proyecto_cloud'],
        properties={
            'nombre': openapi.Schema(type=openapi.TYPE_STRING),
            'aporte_necesario': openapi.Schema(type=openapi.TYPE_STRING),
            'cantidad': openapi.Schema(type=openapi.TYPE_INTEGER),
            'id_back_etapa': openapi.Schema(type=openapi.TYPE_STRING),
            'id_proyecto_back': openapi.Schema(type=openapi.TYPE_STRING),
            'fecha_inicio': openapi.Schema(type=openapi.TYPE_STRING, format="date"),
            'fecha_fin': openapi.Schema(type=openapi.TYPE_STRING, format="date"),
            'proyecto_cloud': openapi.Schema(type=openapi.TYPE_INTEGER)
        }
    ),
    responses={201: "Etapa guardada", 400: "Datos inválidos"}
)
@api_view(['POST'])
@csrf_exempt
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


@swagger_auto_schema(
    method='post',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['nombre', 'ong_responsable', 'id_back_ong', 'fecha_inicio', 'fecha_fin', 'case_id'],
        properties={
            'nombre': openapi.Schema(type=openapi.TYPE_STRING),
            'ong_responsable': openapi.Schema(type=openapi.TYPE_STRING),
            'id_back_ong': openapi.Schema(type=openapi.TYPE_STRING),
            'fecha_inicio': openapi.Schema(type=openapi.TYPE_STRING, format='date'),
            'fecha_fin': openapi.Schema(type=openapi.TYPE_STRING, format='date'),
            'case_id': openapi.Schema(type=openapi.TYPE_STRING),
        }
    ),
    responses={201: "Proyecto creado correctamente"}
)
@api_view(['POST'])
@csrf_exempt
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
    """{
        "nombre": "Plan de Reforestación",
        "ong_responsable": "EcoVida",
        "id_back_ong": "123",
        "id_back_proyecto": "123",
        "fecha_inicio": "2025-10-20",
        "fecha_fin": "2025-12-31",
        "case_id": "123"
    }
    """
    
    
@swagger_auto_schema(
    method='post',
    manual_parameters=[
        openapi.Parameter(
            'Authorization',
            in_=openapi.IN_HEADER,
            description="Token JWT. Formato: Bearer <token>",
            type=openapi.TYPE_STRING
        )
    ],
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['etapa_cloud', 'nombre_ong_coolaboradora', 'id_ong_coolaboradora', 'id_etapa_back', 'aporte', 'cantidad'],
        properties={
            'etapa_cloud': openapi.Schema(type=openapi.TYPE_INTEGER),
            'nombre_ong_coolaboradora': openapi.Schema(type=openapi.TYPE_STRING),
            'id_ong_coolaboradora': openapi.Schema(type=openapi.TYPE_STRING),
            'id_etapa_back': openapi.Schema(type=openapi.TYPE_STRING),
            'aporte': openapi.Schema(type=openapi.TYPE_STRING),
            'es_total': openapi.Schema(type=openapi.TYPE_BOOLEAN),
            'cantidad': openapi.Schema(type=openapi.TYPE_INTEGER),
            'cumplido': openapi.Schema(type=openapi.TYPE_BOOLEAN),
        }
    ),
    responses={201: "Compromiso guardado", 400: "Datos inválidos"}
)
@api_view(['POST'])
@csrf_exempt
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
    

@swagger_auto_schema(
    method='post',
    manual_parameters=[
        openapi.Parameter(
            'Authorization',
            in_=openapi.IN_HEADER,
            description="Token JWT. Formato: Bearer <token>",
            type=openapi.TYPE_STRING
        )
    ],
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['id_compromiso', 'cumplido'],
        properties={
            'id_compromiso': openapi.Schema(type=openapi.TYPE_INTEGER),
            'cumplido': openapi.Schema(type=openapi.TYPE_BOOLEAN),
        }
    ),
    responses={200: "Estado actualizado", 404: "Compromiso no encontrado"}
)
@api_view(['POST'])
@csrf_exempt
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
  
  
@swagger_auto_schema(
    method='get',
    manual_parameters=[
        openapi.Parameter(
            'Authorization', openapi.IN_HEADER,
            description="Bearer token (formato: Bearer <token>)",
            type=openapi.TYPE_STRING,
            required=True
        ),
        openapi.Parameter(
            'id_proyecto_back',
            openapi.IN_QUERY,
            description="ID del proyecto en el backend",
            type=openapi.TYPE_STRING,
            required=True
        )
    ],
    responses={
        200: openapi.Response(description="Lista de compromisos"),
        400: "id_proyecto_back faltante",
        401: "No autorizado"
    }
)
@api_view(['GET'])
@csrf_exempt
@require_jwt
def get_commitments_by_project_id(request):
    id_proyecto_back = request.GET.get('id_proyecto_back')

    if not id_proyecto_back:
        return JsonResponse({"error": "Falta id_proyecto_back"}, status=400)

    try:
        compromisos = Compromiso.objects.filter(
            etapa_cloud__proyecto_cloud__id_back_proyecto=id_proyecto_back
        )

        if not compromisos.exists():
            return JsonResponse(
                {"compromisos": [], "aviso": "No hay compromisos para este proyecto"},
                status=200
            )

        data = [
            {
                "id": compromiso.id,
                "nombre_ong": compromiso.nombre_ong_coolaboradora,
                "aporte": compromiso.aporte,
                "cantidad": compromiso.cantidad,
                "cumplido": compromiso.cumplido,
            }
            for compromiso in compromisos
        ]

        return JsonResponse(
            {"compromisos": data, "aviso": "Se encontraron compromisos"}, status=200
        )

    except Exception as e:
        return JsonResponse(
            {"error": f"Error al obtener compromisos: {str(e)}"}, status=500
        ) 
    """
    http://127.0.0.1:8000/api/v1/get_commitments_by_project_id?id_proyecto_back=numero
    {
    "id_proyecto_back": "1"
    }
    """