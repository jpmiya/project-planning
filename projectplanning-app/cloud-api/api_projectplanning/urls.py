from django.urls import path
from . import views

urlpatterns = [
    path('authenticate', views.authenticate_user, name="authenticate"),
    path('prueba', views.prueba, name="prueba"),
]
