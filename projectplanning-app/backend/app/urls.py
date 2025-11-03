from django.urls import path
from . import views

urlpatterns = [
    path('destinatarios/', views.obtener_destinatarios, name='obtener_destinatarios'),
]