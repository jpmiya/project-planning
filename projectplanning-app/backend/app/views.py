from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from app.utils import procesar_etapas
from app.controllers.projects import save_project
from app.api.bonita import get_bonita_api 
import time, json
from django.views.decorators.http import require_GET
from django.views.decorators.csrf import csrf_exempt
from app.models.project import Project
from app.models.etapa import Etapa
from django.db import transaction


# Create your views here.
def home(request):
    return render(request, 'home.html')

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
        ong_responsable = request.POST.get('ong')
        fecha_inicio = request.POST.get('fecha_inicio')
        fecha_fin = request.POST.get('fecha_fin')
        plan_economico = request.POST.get('plan_economico')
        etapas = procesar_etapas(request)
        data = {
            'nombre': nombre,
            'ong_responsable': ong_responsable,
            'fecha_inicio': fecha_inicio,
            'fecha_fin': fecha_fin,
            'plan_economico': plan_economico,
            'etapas': etapas
        }
        save_project(data)
        messages.success(request, 'Proyecto creado exitosamente.')
        
        etapas_ayuda = [
            {
                "id_etapa": str(1),  # buscarlo a la BBDD
                "nombre_etapa": nombre,
                "fecha_inicio": datos["inicio"],
                "fecha_fin": datos["fin"]
            }
            for i, (nombre, datos) in enumerate(etapas.items())
            if datos["ayuda"].lower() == "true"
        ]
        
        payload = {
                "id_proyecto": str(1), # Obtener el que da la BBDD
                "nombre_proyecto": nombre,
                "ong_originante": ong_responsable,
                #"etapas": json.dumps(etapas_ayuda)
            }
        
        payload_json = json.dumps(payload)
        
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
            
            # Buscar actividades
            time.sleep(1) # Esto es porque si le preguntas ni bien creas el proceso, a veces encuentra ya veces no, dejamos que lo guarde bien y despues consultamos 
            activity = api.search_activity_by_case_id(case_id)
            if activity:
                print(f"Actividad encontrada: {activity}")
                # Asigna la tarea a un usuario
                bates = api.get_user_id_by_username("franco.colapinto")
                api.assign_task(activity, bates)
                # Intentar ejecutar la tarea
                executed = api.execute_user_task(activity, {})
                print(f"Tarea ejecutada: {executed}")
            else:
                print("No se encontraron actividades pendientes (esto puede ser normal)")
            
            # Setear variable
            seteo = api.set_variable_by_case(case_id, "todas_etapas_cubiertas", False, "java.lang.Boolean")
            print(f"Variable seteada: {seteo}")
            
            seteo = api.set_variable_by_case(case_id, "proyecto_case", payload_json, "java.lang.String")
            print(f"Variable seteada: {seteo}")
            
            seteo = api.set_variable_by_case(case_id, "etapas", json.dumps(etapas_ayuda), "java.lang.String")
            print(f"Variable seteada: {seteo}")
            
            messages.info(request, f'Proceso Bonita iniciado con Case ID: {case_id}')
            
        except Exception as e:
            print(f"ERROR en proceso Bonita: {e}")
            messages.error(request, f'Error en Bonita: {str(e)}')
        
        return redirect('home')
    
    
@csrf_exempt
@require_GET
def obtener_destinatarios(request):
    # Mail fijo, despues hacemos la busqueda
    destinatarios = [
        "francobasterrechea@mail.com",
    ]
    return JsonResponse(destinatarios, safe=False)

def listar_pedidos(request):
    # Esta función se mantiene para compatibilidad pero delega a la vista completa
    return pedidos_view(request)


def pedidos_view(request):
    """Muestra un listado de proyectos (pedidos) con botón para ver etapas."""
    proyectos = Project.objects.all().prefetch_related('etapas')
    return render(request, 'pedidos.html', {'proyectos': proyectos})


def ver_etapas(request, project_id):
    """Muestra y permite marcar en qué etapas el usuario puede ayudar."""
    proyecto = get_object_or_404(Project, pk=project_id)
    etapas = proyecto.etapas.all()
    if request.method == 'POST':
        # Procesar ofertas enviadas por el usuario
        seleccionadas = request.POST.getlist('ayuda')  # lista de ids de etapas seleccionadas

        aportes = []

        if not seleccionadas:
            messages.info(request, 'No enviaste aportes.')
            return redirect('pedidos')

        # Verificar que el proyecto tenga case_id antes de comenzar la transacción
        case_id = proyecto.case_id
        if not case_id:
            messages.error(request, 'El proyecto no tiene un case_id asociado en Bonita.')
            return redirect('ver_etapas', project_id=project_id)

        try:
            api = get_bonita_api()

            # Usamos una transacción con select_for_update para prevenir condiciones de carrera
            with transaction.atomic():
                for etapa in etapas:
                    eid = str(etapa.id)
                    if eid in seleccionadas:
                        if not etapa.requiere_ayuda:
                            raise ValueError(f'La etapa "{etapa.nombre_aporte}" no está solicitando ayuda.')

                        aporte_text = request.POST.get(f'aporte_{eid}', '').strip()
                        cantidad_raw = request.POST.get(f'cantidad_{eid}', '').strip()

                        # validar cantidad como entero positivo
                        try:
                            cantidad = int(cantidad_raw) if cantidad_raw != '' else None
                        except ValueError:
                            raise ValueError(f'Cantidad inválida para la etapa "{etapa.nombre_aporte}".')

                        if cantidad is None or cantidad <= 0:
                            raise ValueError(f'Debe indicar una cantidad válida para la etapa "{etapa.nombre_aporte}".')
                        etapa_locked = Etapa.objects.select_for_update().get(pk=etapa.id)
                        if cantidad > etapa_locked.cant_aporte_necesario:
                            raise ValueError(f'La cantidad solicitada para "{etapa.nombre_aporte}" excede la necesaria ({etapa_locked.cant_aporte_necesario}).')

                        # Decrementar y guardar (queda dentro de la transacción)
                        etapa_locked.cant_aporte_necesario = etapa_locked.cant_aporte_necesario - cantidad
                        etapa_locked.save()

                        aportes.append({
                            'etapa_id': etapa_locked.id,
                            'etapa_nombre': etapa_locked.nombre_aporte,
                            'aporte': aporte_text,
                            'cantidad': cantidad,
                        })

                # Enviar las variables a Bonita para que las reenvíe al cloud
                payload = json.dumps(aportes)
                ok = api.set_variable_by_case(case_id, 'compromisos', payload, 'java.lang.String')

                if not ok:
                    # Forzar rollback de la transacción
                    raise RuntimeError('Ocurrió un error al enviar los compromisos a Bonita.')

            # Si llegamos acá, la transacción se completó y el envío a Bonita fue OK
            messages.success(request, 'Tus compromisos fueron enviados a Bonita.')

        except ValueError as ve:
            messages.error(request, str(ve))
            return redirect('ver_etapas', project_id=project_id)
        except Exception as e:
            # Errores generales (incluye fallo en el set_variable_by_case)
            messages.error(request, f'Error procesando los compromisos: {e}')
            return redirect('ver_etapas', project_id=project_id)

        return redirect('pedidos')

    return render(request, 'etapas.html', {
        'proyecto': proyecto,
        'etapas': etapas,
    })


# ===== VISTAS DE USUARIO (COMENTADAS TEMPORALMENTE) =====

# def register_view(request):
#     """Vista para registro de nuevos usuarios"""
#     if request.method == 'POST':
#         form = CustomUserCreationForm(request.POST)
#         if form.is_valid():
#             user = form.save()
#             messages.success(request, f'Usuario {user.username} creado exitosamente. Ya puedes iniciar sesión.')
#             return redirect('login')
#         else:
#             messages.error(request, 'Por favor corrige los errores en el formulario.')
#     else:
#         form = CustomUserCreationForm()
#     
#     return render(request, 'registration/register.html', {'form': form})


# def custom_login_view(request):
#     """Vista personalizada de login"""
#     if request.method == 'POST':
#         username = request.POST.get('username')
#         password = request.POST.get('password')
#         
#         user = authenticate(request, username=username, password=password)
#         if user is not None:
#             login(request, user)
#             messages.success(request, f'¡Bienvenido {user.profile.full_name}!')
#             next_url = request.GET.get('next', 'home')
#             return redirect(next_url)
#         else:
#             messages.error(request, 'Credenciales incorrectas.')
#     
#     return render(request, 'registration/login.html')


# def custom_logout_view(request):
#     """Vista personalizada de logout"""
#     logout(request)
#     messages.info(request, 'Has cerrado sesión exitosamente.')
#     return redirect('home')


# @login_required
# def profile_view(request):
#     """Vista para ver y editar el perfil del usuario"""
#     profile = request.user.profile
#     
#     if request.method == 'POST':
#         form = UserProfileUpdateForm(request.POST, instance=profile)
#         if form.is_valid():
#             form.save()
#             messages.success(request, 'Perfil actualizado exitosamente.')
#             return redirect('profile')
#         else:
#             messages.error(request, 'Por favor corrige los errores en el formulario.')
#     else:
#         form = UserProfileUpdateForm(instance=profile)
#     
#     return render(request, 'registration/profile.html', {
#         'form': form,
#         'profile': profile
#     })
