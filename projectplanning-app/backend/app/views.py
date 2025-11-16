from os import getenv
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
import requests
from app.decorators import role_required
from app.controllers.projects import save_project, save_etapas
from app.api.bonita import get_bonita_api 
from app.utils import procesar_etapas, obtain_cloud_token, fetch_commitments_from_cloud
import time, json
from django.views.decorators.http import require_GET, require_POST
from django.views.decorators.csrf import csrf_exempt
from app.models.project import Project
from app.models.etapa import Etapa
from app.models.ong import ONG
from app.services.proyectos import process_offers, ProyectosServiceError
from app.forms import RegistrationForm
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth.models import User
from django.http import HttpResponse


# Create your views here.
@login_required
def home(request):
    return render(request, 'home.html')


def register(request):
    """Registrar un nuevo usuario usando el formulario estándar de Django.

    - GET: muestra el formulario
    - POST: valida y crea el usuario, inicia sesión y redirige a `home`
    """
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f'Usuario {user.username} creado exitosamente. Ya estás conectado.')
            # Iniciar sesión automáticamente
            auth_login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Por favor corrige los errores en el formulario.')
    else:
        form = RegistrationForm()

    return render(request, 'registration/register.html', {'form': form})

@login_required
def alta_proyecto(request):
    if request.method == 'GET':
        """api = get_bonita_api("walter.bates", "bpm")
        role_id = api.get_role_id("ONG-Coolaboradora")
        group_id = api.get_group_id("Project-Planning")
        user_id = api.get_user_id_by_username("franco.colapinto")
        api.create_membership(user_id, role_id, group_id)"""
        return render(request, 'alta_proyecto.html')
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        ong_responsable = request.user
        fecha_inicio = request.POST.get('fecha_inicio')
        fecha_fin = request.POST.get('fecha_fin')
        plan_economico = request.POST.get('plan_economico')
        etapas = procesar_etapas(request)
        data = {
            'nombre': nombre,
            'ong_responsable': User.objects.get(username= ong_responsable).id,
            'fecha_inicio': fecha_inicio,
            'fecha_fin': fecha_fin,
            'plan_economico': plan_economico,
            'etapas': etapas
        }
        project = save_project(data)
        etapas = save_etapas(data, project)
        messages.success(request, 'Proyecto creado exitosamente.')
        
        etapas_ayuda = [
            {
                "id_back_etapa": etapa.id,
                "nombre": etapa.nombre_etapa,
                "aporte_necesario": etapa.nombre_aporte,
                "cantidad": etapa.cant_aporte_necesario,
                "fecha_inicio": etapa.fecha_inicio,
                "fecha_fin": etapa.fecha_fin,
                "id_proyecto_back": project.id
            }
            for etapa in etapas
            if etapa.requiere_ayuda
        ]
        
        # Llamadas de prueba con manejo de errores
        try:
            api = get_bonita_api("franco.colapinto", "Williams_Fw46")
            if not api.authenticated:
                messages.warning(request, 'No se pudo conectar a Bonita. Revisa la configuración.')
                return redirect('home')
            
            print("=== INICIANDO PROCESO BONITA ===")
            process_id = api.get_process_id("Project-Planning")
            if not process_id:
                messages.error(request, 'No se encontró el proceso "Project-Planning" en Bonita.')
                return redirect('home')
            print(f"Process ID encontrado: {process_id}")
            
            case_id = api.initiate_project_by_id(process_id)
            if not case_id:
                messages.error(request, 'No se pudo iniciar el proceso en Bonita.')
                return redirect('home')
            
            print(f"Case ID creado: {case_id}")
            
            # Setear variable
            #seteo = api.set_variable_by_case(case_id, "todas_etapas_cubiertas", False, "java.lang.Boolean")
            #print(f"Variable seteada: {seteo}")
            id_back_ong = User.objects.get(username=ong_responsable).id
            proyecto = {
                    "id_back_proyecto": project.id, # Obtener el que da la BBDD
                    "nombre": nombre,
                    "ong_responsable": ong_responsable.first_name,
                    "id_back_ong": id_back_ong,
                    "fecha_inicio": fecha_inicio,
                    "fecha_fin": fecha_fin,
                    "case_id": case_id,
                    #"etapas": json.dumps(etapas_ayuda)
                }
            
            # payload_json = json.dumps(payload)
            
            #seteo = api.set_variable_by_case(case_id, "proyecto_case", payload_json, "java.lang.String")
            #print(f"Variable seteada: {seteo}")
            
            #seteo = api.set_variable_by_case(case_id, "etapas", json.dumps(etapas_ayuda), "java.lang.String")
            #print(f"Variable seteada: {seteo}")
            
            messages.info(request, f'Proceso Bonita iniciado con Case ID: {case_id}')
            
            # Buscar actividades
            time.sleep(1) # Esto es porque si le preguntas ni bien creas el proceso, a veces encuentra ya veces no, dejamos que lo guarde bien y despues consultamos 
            activity = api.search_activity_by_case_id(case_id)
            if activity:
                print(f"Actividad encontrada: {activity}")
                # Asigna la tarea a un usuario
                bates = api.get_user_id_by_username("franco.colapinto")
                api.assign_task(activity, bates)
                # Intentar ejecutar la tarea
                payload = {
                    "proyecto": proyecto,
                    "etapas": etapas_ayuda
                }
                executed = api.execute_user_task(activity, payload)
                print(f"Tarea ejecutada: {executed}")
            else:
                print("No se encontraron actividades pendientes (esto puede ser normal)")
            
            
        except Exception as e:
            print(f"ERROR en proceso Bonita: {e}")
            messages.error(request, f'Error en Bonita: {str(e)}')
        
        return redirect('home')
    
#@login_required
@csrf_exempt
@require_GET
def obtener_destinatarios(request):
    # Mail fijo, despues hacemos la busqueda
    emails = list(User.objects.values_list('username', flat=True))
    return JsonResponse(emails, safe=False)


@csrf_exempt
@require_POST
def set_cloud_project_id(request):
    # Mail fijo, despues hacemos la busqueda
    cloud_id = request.POST.get('cloud_id')
    project_id = request.POST.get('project_id')
    Project.objects.get(project_id).cloud_id = cloud_id
    return HttpResponse(status=200)

@login_required
def pedidos_view(request):
    """Muestra un listado de proyectos (pedidos) con botón para ver etapas."""
    proyectos = Project.objects.all().prefetch_related('etapas')
    return render(request, 'pedidos.html', {'proyectos': proyectos})

@login_required
def ver_etapas(request, project_id):
    """Muestra las etapas de un proyecto, y recibe compromisos."""
    proyecto = get_object_or_404(Project, pk=project_id)
    etapas = proyecto.etapas.all()
    if request.method == 'POST':
        seleccionadas = request.POST.getlist('ayuda')  # lista de ids de etapas seleccionadas

        if not seleccionadas:
            messages.info(request, 'No enviaste aportes.')
            return redirect('pedidos')

        try:
            result = process_offers(proyecto, seleccionadas, request.POST, user=request.user if request.user.is_authenticated else None)
            messages.success(request, 'Tus compromisos fueron enviados a Bonita.')
        except ProyectosServiceError as pse:
            messages.error(request, str(pse))
            return redirect('ver_etapas', project_id=project_id)
        except Exception as e:
            messages.error(request, f'Error procesando los compromisos: {e}')
            return redirect('ver_etapas', project_id=project_id)

        return redirect('pedidos')

    return render(request, 'etapas.html', {
        'proyecto': proyecto,
        'etapas': etapas,
    })


def custom_login_view(request):
    """Vista de login usando AuthenticationForm de Django."""
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)
            messages.success(request, f'¡Bienvenido {user.profile.full_name}!')
            next_url = request.GET.get('next', 'home')
            return redirect(next_url)
        else:
            messages.error(request, 'Credenciales incorrectas.')
    else:
        form = AuthenticationForm()

    return render(request, 'registration/login.html', {'form': form})

@login_required
def custom_logout_view(request):
    """Logout simple y redirect a home."""
    auth_logout(request)
    messages.info(request, 'Has cerrado sesión exitosamente.')
    return redirect('login')

@role_required('Gerente')
def gerente_view(request):
    """Vista para acciones de gerente. Si se pasa ?project=<id> muestra el proyecto seleccionado."""
    project_id = request.GET.get('project')
    proyecto = None
    if project_id:
        try:
            proyecto = get_object_or_404(Project, pk=int(project_id))
        except Exception:
            proyecto = None

    # Por ahora renderizamos la plantilla con el proyecto (o None)
    return render(request, 'gerente.html', {'proyecto': proyecto})


@login_required
def projects_view(request):
    """Listado 'Mis Proyectos' — proyectos creados por el usuario actual.

    Se determina pertenencia comparando `Project.ong_responsable` con
    `request.user.profile.full_name` o `request.user.first_name` para mantener
    compatibilidad con datos existentes.
    """
    user = request.user
    # The project.ong_responsable field stores the creating user's id (as string or int).
    owner_id_str = str(user.id)

    proyectos = Project.objects.filter(ong_responsable__in=[owner_id_str]).prefetch_related('etapas')

    return render(request, 'mis_proyectos.html', {'proyectos': proyectos})


@login_required
def project_compromises(request, project_id):
    """Muestra los compromisos externos de un proyecto (GET) y permite
    marcar el proyecto como Finalizado (POST).

    El acceso está limitado: solo el usuario que creó el proyecto puede
    ver/editar su estado (comparando `ong_responsable` con el nombre del usuario).
    """
    proyecto = get_object_or_404(Project, pk=project_id)
    user = request.user
    owner_id_str = str(user.id)

    if str(proyecto.ong_responsable) != owner_id_str:
        messages.error(request, 'No tienes permisos para acceder a los compromisos de este proyecto.')
        return redirect('mis_proyectos')

    # POST: marcar como finalizado
    if request.method == 'POST':
        proyecto.estado = Project.ESTADO_FINALIZADO if hasattr(Project, 'ESTADO_FINALIZADO') else 'Finalizado'
        proyecto.save()
        messages.success(request, 'Proyecto marcado como Finalizado.')
        return redirect('mis_proyectos')

    # GET: intentar obtener compromisos desde la API cloud si existe (cliente externo)
    commitments = []
    api_error = None
    try:
        commitments = fetch_commitments_from_cloud(proyecto.id)
    except Exception as e:
        api_error = str(e)

    if api_error:
        messages.info(request, f'No se pudieron obtener los compromisos remotos: {api_error}')

    return render(request, 'compromisos.html', {
        'proyecto': proyecto,
        'commitments': commitments,
    })