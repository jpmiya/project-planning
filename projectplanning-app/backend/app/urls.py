from django.urls import path
from . import views

urlpatterns = [
    path('destinatarios/', views.obtener_destinatarios, name='obtener_destinatarios'),
    path('post_cloud_project_id/', views.obtener_destinatarios, name='set_cloud_project_id'),
]