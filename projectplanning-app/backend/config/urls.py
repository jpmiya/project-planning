"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from app import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('alta_proyecto/', views.alta_proyecto, name='alta_proyecto'),
    path('api/destinatarios/', views.obtener_destinatarios, name='obtener_destinatarios'),
    path('pedidos/', views.pedidos_view, name='pedidos'),
    path('proyecto/<int:project_id>/etapas/', views.ver_etapas, name='ver_etapas'),
    path('mis_proyectos/', views.projects_view, name='mis_proyectos'),
    path('mis_proyectos/<int:project_id>/compromisos/', views.project_compromises, name='project_compromises'),
    path('observacion/<int:observacion_id>/resolver/', views.resolver_observacion, name='resolver_observacion'),
    path('register/', views.register, name='register'),
    path('login/', views.custom_login_view, name='login'),
    path('logout/', views.custom_logout_view, name='logout'),
    path('proyectos_ejecucion/', views.proyectos_ejecucion_view, name='proyectos_ejecucion'),
    path('tablero_gerencial/', views.tablero_gerencial_view, name='tablero_gerencial'),
    #path('api/obtener_etapas_proyecto/<int:id_proyecto>/', views.obtener_etapas_proyecto, name='obtener_etapas_proyecto'),
    #path('api/obtener_proyecto/<int:id_proyecto>/', views.obtener_proyecto, name='obtener_proyecto'),
]
