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
from app.utils import procesar_etapas, obtain_cloud_token, fetch_commitments_from_cloud, verificar_etapas, verificar_proyecto
import time, json
from django.views.decorators.http import require_GET, require_POST
from django.views.decorators.csrf import csrf_exempt
from app.models.project import Project
from app.models.etapa import Etapa
from app.models.ong import ONG
from app.models.observation import Observation
from app.services.proyectos import process_offers, ProyectosServiceError
from app.forms import RegistrationForm
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.utils import timezone
from django.db import models
from datetime import timedelta


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
            # Actualizar last_login manualmente
            user.last_login = timezone.now()
            user.save(update_fields=['last_login'])
            return redirect('home')
        else:
            messages.error(request, 'Por favor corrige los errores en el formulario.')
    else:
        form = RegistrationForm()

    return render(request, 'registration/register.html', {'form': form})

@login_required
def alta_proyecto(request):
    if request.method == 'GET':
        """ api = get_bonita_api("walter.bates", "bpm")
        colapa = api.create_bonita_user("franco.colapinto", "Williams_Fw46", "Franco", "colapa@mail.com", "Colapinto", True)
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
            'ong_responsable': User.objects.get(username=ong_responsable),
            'fecha_inicio': fecha_inicio,
            'fecha_fin': fecha_fin,
            'plan_economico': plan_economico,
            'etapas': etapas
        }
         # Validaciones
        errores_proyecto = verificar_proyecto(data)
        errores_etapas = verificar_etapas(data)

        # Si hay errores, NO se guarda y NO se redirige
        if errores_proyecto or errores_etapas:
            contexto = {
                "errores_proyecto": errores_proyecto,
                "errores_etapas": errores_etapas,
                "valores": data,
            }
            return render(request, "alta_proyecto.html", contexto)
        
        project = save_project(data)
        etapas = save_etapas(data, project)
        messages.success(request, 'Proyecto creado exitosamente.')
        
        etapas_ayuda = [
            {
                "nombre": etapa.nombre_etapa,
                "aporte_necesario": etapa.nombre_aporte,
                "cantidad": etapa.cant_aporte_necesario,
                "etapa_back_id": etapa.id,
                "proyecto_back_id": project.id,
                "fecha_inicio": etapa.fecha_inicio,
                "fecha_fin": etapa.fecha_fin,
            }
            for etapa in etapas
            if etapa.requiere_ayuda
        ]
        
        # Llamadas de prueba con manejo de errores
        try:
            api = get_bonita_api("walter.bates", "bpm")#get_bonita_api("franco.colapinto", "Williams_Fw46")
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
            project.case_id = case_id
            project.save()
            print(f"Case Id en proyecto: {project.case_id}")
            
            # Setear variable
            #seteo = api.set_variable_by_case(case_id, "todas_etapas_cubiertas", False, "java.lang.Boolean")
            #print(f"Variable seteada: {seteo}")
            id_back_ong = User.objects.get(username=ong_responsable).id
            proyecto = {
                    "nombre": nombre,
                    "ong_responsable": ong_responsable.username,
                    "ong_back_id": id_back_ong,
                    "proyecto_back_id": project.id, # Obtener el que da la BBDD
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
                bates = api.get_user_id_by_username("walter.bates")
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
    user = request.user
    owner_id = user.id
    
    proyectos = Project.objects.exclude(ong_responsable__id=owner_id).filter(estado='Pendiente').prefetch_related('etapas')
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
            messages.success(request, 'Tus compromisos fueron registrados.')
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
            # Actualizar last_login manualmente
            user.last_login = timezone.now()
            user.save(update_fields=['last_login'])
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
def proyectos_ejecucion_view(request):
    """Vista para gerente: muestra proyectos en ejecución y permite agregar observaciones.
    
    GET: Lista todos los proyectos con estado 'En ejecucion'
    POST: Agrega una observación a un proyecto específico (recibe project_id en el form)
    """
    # POST: crear nueva observación para un proyecto
    if request.method == 'POST':
        project_id = request.POST.get('project_id')
        observacion_text = request.POST.get('observacion', '').strip()
        
        if project_id and observacion_text:
            try:
                proyecto = get_object_or_404(Project, pk=int(project_id))
                # Crear la observación asociada al proyecto
                Observation.objects.create(
                    text=observacion_text,
                    id_project=proyecto
                )
                messages.success(request, f'Observación agregada exitosamente al proyecto "{proyecto.nombre}".')
            except Exception as e:
                messages.error(request, f'Error al crear observación: {e}')
        else:
            messages.warning(request, 'Debe proporcionar el proyecto y el texto de la observación.')
        
        return redirect('proyectos_ejecucion')
    
    # GET: cargar todos los proyectos en ejecución
    proyectos = Project.objects.filter(estado=Project.ESTADO_EN_EJECUCION).prefetch_related('etapas')
    
    return render(request, 'proyectos_ejecucion.html', {'proyectos': proyectos})


@login_required
def projects_view(request):
    """Listado 'Mis Proyectos' — proyectos creados por el usuario actual o en los que colaboró.

    Muestra:
    - Proyectos donde el usuario es originante (ong_responsable == user.id)
    - Proyectos donde el usuario es colaborador (en ongs_colaboradoras)
    """
    user = request.user
    owner_id = user.id

    # Proyectos originados por el usuario
    proyectos_originados = Project.objects.filter(
        ong_responsable__id=owner_id
    ).prefetch_related('etapas', 'observation_set')
    
    # Proyectos en los que colaboró
    proyectos_colaborados = Project.objects.filter(
        ongs_colaboradoras=user
    ).prefetch_related('etapas', 'observation_set')
    
    # Combinar ambos sets y marcar el rol del usuario en cada proyecto
    proyectos_data = []
    
    for p in proyectos_originados:
        proyectos_data.append({
            'proyecto': p,
            'es_originante': True,
        })
    
    for p in proyectos_colaborados:
        # Evitar duplicados (si está en ambos)
        if p.ong_responsable != owner_id:
            proyectos_data.append({
                'proyecto': p,
                'es_originante': False,
            })

    return render(request, 'mis_proyectos.html', {'proyectos_data': proyectos_data})


@login_required
def project_compromises(request, project_id):
    """Muestra los compromisos externos de un proyecto (GET) y permite
    marcar el proyecto como En Ejecucion (POST).

    El acceso está limitado: solo el usuario que creó el proyecto puede
    ver/editar su estado (comparando `ong_responsable` con el nombre del usuario).
    """
    proyecto = get_object_or_404(Project, pk=project_id)
    user = request.user
    owner_id = user.id

    if proyecto.ong_responsable.id != owner_id:
        messages.error(request, 'No tienes permisos para acceder a los compromisos de este proyecto.')
        return redirect('mis_proyectos')

    # POST: marcar como finalizado
    if request.method == 'POST':

        api = get_bonita_api("walter.bates", "bpm")
        activity = api.search_activity_by_case_id(proyecto.case_id)
        if activity:
            #aca hay que controlar que esten todos los compromisos cumplidos antes de pasar a ejecución
            proyecto.estado = Project.ESTADO_EN_EJECUCION if hasattr(Project, 'ESTADO_EN_EJECUCION') else 'En ejecucion'
            proyecto.save()
            messages.success(request, 'Proyecto marcado como Finalizado.')
            #print(f"Actividad encontrada: {activity}")
            # Asigna la tarea a un usuario
            bates = api.get_user_id_by_username("walter.bates")
            api.assign_task(activity, bates)
            # Intentar ejecutar la tarea
            executed = api.execute_user_task(activity, {})
            #print(f"Tarea ejecutada: {executed}")
            messages.info(request, 'Se ha marcado el Plan de Trabajo como Completo')
            return redirect('mis_proyectos')
        else:
            print("No se encontraron actividades pendientes (esto puede ser normal)")
            messages.error(request, 'Ha ocurrido un error al marcar el Plan de Trabajo como completo')

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
        'commitments': commitments["compromisos"],
    })


@login_required
def resolver_observacion(request, observacion_id):
    """Marca una observación como 'Resuelto'.
    
    Solo el dueño del proyecto puede marcar observaciones como resueltas.
    """
    if request.method != 'POST':
        messages.error(request, 'Método no permitido.')
        return redirect('mis_proyectos')
    
    observacion = get_object_or_404(Observation, pk=observacion_id)
    proyecto = observacion.id_project
    
    # Verificar ownership
    user = request.user
    owner_id = user.id
    
    if proyecto.ong_responsable != owner_id:
        messages.error(request, 'No tienes permisos para modificar esta observación.')
        return redirect('mis_proyectos')
    
    # Marcar como resuelto
    observacion.estado = Observation.ESTADO_RESUELTO
    observacion.save()
    
    messages.success(request, f'Observación marcada como resuelta.')
    return redirect('mis_proyectos')


@login_required
@role_required('Gerente')
def tablero_gerencial_view(request):
    """Tablero gerencial para Gerente: integra datos de BD local + Bonita BPM.
    
    Consulta 1: Proyectos abiertos con estado en Bonita
    Consulta 2: Etapas registradas + tareas humanas pendientes
    Consulta 3: KPIs de carga global del sistema
    """
    # Obtener proyectos de BD local
    proyectos_bd = Project.objects.all()
    
    # Inicializar estructura para consulta 1
    proyectos_con_bonita = []
    
    # Inicializar estructura para consulta 2
    etapas_con_tareas = []
    
    # Inicializar estructura para consulta 3 (KPIs)
    kpis = {
        'total_proyectos': proyectos_bd.count(),
        'procesos_bonita_activos': 0,
        'usuarios_activos_mes': 0,
        'compromisos_pendientes': 0,
    }
    
    # Calcular KPIs de BD (independientes de Bonita)
    # KPI 3: Usuarios activos en el mes
    fecha_mes_atras = timezone.now() - timedelta(days=30)
    usuarios_activos = User.objects.filter(last_login__gte=fecha_mes_atras)
    kpis['usuarios_activos_mes'] = usuarios_activos.count()
    
    # Debug: Ver todos los usuarios con last_login
    print(f"DEBUG KPI - Fecha mes atrás: {fecha_mes_atras}")
    print(f"DEBUG KPI - Total usuarios: {User.objects.count()}")
    for u in User.objects.all():
        print(f"DEBUG KPI - Usuario: {u.username}, last_login: {u.last_login}")
    
    # KPI 4: Compromisos pendientes
    etapas_pendientes = Etapa.objects.filter(
        requiere_ayuda=True,
        cant_aporte_actual__lt=models.F('cant_aporte_necesario')
    )
    kpis['compromisos_pendientes'] = etapas_pendientes.count()
    
    # Conectar con Bonita
    print("DEBUG: Iniciando conexión con Bonita")
    try:
        api = get_bonita_api("walter.bates", "bpm")#get_bonita_api("franco.colapinto", "Williams_Fw46")
        print(f"DEBUG: Bonita authenticated: {api.authenticated}")
        
        if api.authenticated:
            # Consulta 1: Obtener casos activos de Bonita
            casos_bonita = api.get_active_cases()
            casos_map = {caso.get('id'): caso for caso in casos_bonita}
            
            # Integrar proyectos BD con casos Bonita
            for proyecto in proyectos_bd:
                caso_bonita = None
                estado_bonita = 'N/A'
                
                if proyecto.case_id and proyecto.case_id in casos_map:
                    caso_bonita = casos_map[proyecto.case_id]
                    estado_bonita = caso_bonita.get('state', 'desconocido')
                
                proyectos_con_bonita.append({
                    'id': proyecto.id,
                    'nombre': proyecto.nombre,
                    'ong_responsable': proyecto.ong_responsable.id,
                    'estado_bd': proyecto.estado,
                    'fecha_inicio': proyecto.fecha_inicio,
                    'fecha_fin': proyecto.fecha_fin,
                    'case_id': proyecto.case_id,
                    'estado_bonita': estado_bonita,
                })
            
            # Consulta 2: Obtener todas las etapas de BD
            etapas_bd = Etapa.objects.select_related('proyecto').all()
            
            # Obtener tareas pendientes de Bonita
            tareas_bonita = api.get_pending_human_tasks()
            
            # Crear mapa de tareas por rootContainerId (case_id)
            tareas_por_caso = {}
            for tarea in tareas_bonita:
                case_id = tarea.get('rootContainerId')
                if case_id not in tareas_por_caso:
                    tareas_por_caso[case_id] = []
                tareas_por_caso[case_id].append(tarea)
            
            # Integrar etapas BD con tareas Bonita
            for etapa in etapas_bd:
                proyecto = etapa.proyecto
                tareas_pendientes = []
                
                if proyecto.case_id:
                    tareas_pendientes = tareas_por_caso.get(proyecto.case_id, [])
                
                etapas_con_tareas.append({
                    'id': etapa.id,
                    'proyecto_nombre': proyecto.nombre,
                    'nombre_etapa': etapa.nombre_etapa,
                    'nombre_aporte': etapa.nombre_aporte,
                    'cant_necesario': etapa.cant_aporte_necesario,
                    'cant_actual': etapa.cant_aporte_actual,
                    'requiere_ayuda': etapa.requiere_ayuda,
                    'tareas_pendientes': len(tareas_pendientes),
                    'tareas_detalle': [
                        {
                            'nombre': t.get('name', 'Sin nombre'),
                            'id': t.get('id'),
                            'estado': t.get('state', 'N/A'),
                        }
                        for t in tareas_pendientes
                    ],
                })
            
            # KPI 2: Procesos Bonita activos (casos activos)
            kpis['procesos_bonita_activos'] = len(casos_bonita)
            
        else:
            print("DEBUG: No se pudo autenticar con Bonita")
            messages.warning(request, 'No se pudo autenticar con Bonita BPM.')
    
    except Exception as e:
        print(f"DEBUG: Error al conectar con Bonita: {str(e)}")
        messages.error(request, f'Error al conectar con Bonita: {str(e)}')
    
    return render(request, 'tablero_gerencial.html', {
        'proyectos': proyectos_con_bonita,
        'etapas': etapas_con_tareas,
        'kpis': kpis,
    })
    
    
@login_required
def terminar_compromiso(request, compromiso_id, proyecto_id):
    """Cumple un compromiso una vez que se haya aportado al proyecto"""
    id_compromiso = int(compromiso_id)
    
    proyecto = get_object_or_404(Project, pk=proyecto_id)
    user = request.user
    owner_id = user.id

    if proyecto.ong_responsable.id != owner_id:
        messages.error(request, 'No tienes permisos para acceder a los compromisos de este proyecto.')
        return redirect('mis_proyectos')
    
    api = get_bonita_api("walter.bates", "bpm")
    activity = api.search_activity_by_case_id(proyecto.case_id)
    if activity:
        #print(f"Actividad encontrada: {activity}")
        # Asigna la tarea a un usuario
        bates = api.get_user_id_by_username("walter.bates")
        api.assign_task(activity, bates)
        # Intentar ejecutar la tarea
        json_finalizar_compromiso = {
            "id_compromiso": id_compromiso,
            "cumplido": True
        }
        
        payload = {
            "json_finalizar_compromiso": json_finalizar_compromiso
        }
        
        executed = api.execute_user_task(activity, payload)
        #print(f"Tarea ejecutada: {executed}")
        messages.info(request, 'Se ha marcado el compromiso como cumplido')
    else:
        print("No se encontraron actividades pendientes (esto puede ser normal)")
        messages.error(request, 'Ha ocurrido un error al marcar el compromiso como cumplido')
    
    return redirect('mis_proyectos')


@csrf_exempt
@require_POST
def recibir_respuesta_api(request):
    body = request.body                     # esto es bytes
    body_str = body.decode('utf-8')         # lo convertís a str
    body_json = json.loads(body_str)              # lo convertís a dict de Python

    etapas_cumplidas = body_json.get("etapas_cubiertas")
    
    if etapas_cumplidas:
        proyecto_id = body_json.get("proyecto_id")
        proyecto = Project.objects.get(id=proyecto_id)
        proyecto.estado = Project.ESTADO_FINALIZADO
        proyecto.save()
        print(f"Estado proyecto: {proyecto.estado}")
    return JsonResponse({"status": "ok"}, status=200)
