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