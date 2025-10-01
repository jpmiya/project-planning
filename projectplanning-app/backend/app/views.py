from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from app.utils import procesar_etapas
from app.controllers.projects import save_project
from app.api.bonita import get_bonita_api 

# Create your views here.
def home(request):
    return render(request, 'home.html')

def alta_proyecto(request):
    if request.method == 'GET':
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
        # Llamadas de prueba
        #api = get_bonita_api() # Funciona
        #process_id = api.get_process_id("Project-Planning") # Funciona
        #case_id = api.initiate_project_by_id(process_id) # Funciona
        #activity = api.search_activity_by_case_id(case_id) # "Funciona", devuelve una lista vacia, seguro sea si por un tema del diagrama BPMN
        #seteo = api.set_variable_by_case(case_id, "todas_etapas_cubiertas", False, "java.lang.Boolean") # Funciona
        #completo = api.execute_user_task(activity) # Deberia funcionar, pero necesita el id de la actividad, y es lo que me devuelve una lista vacia
        #task = api.assign_task(activity, "walter.bates") # No lo probe
        return redirect('home')


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
