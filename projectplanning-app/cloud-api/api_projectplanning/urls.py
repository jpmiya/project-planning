from django.urls import path
from . import views

urlpatterns = [
    path('authenticate', views.authenticate_user, name="authenticate"),
    path('prueba', views.prueba, name="prueba"),
    path('save_etapa', views.save_etapa, name="save_etapa"),
    path('save_proyecto', views.save_proyecto, name="save_proyecto"),
    path('save_compromiso', views.save_compromiso, name="save_compromiso"),
    path('mark_cumplido_fulfilled', views.mark_cumplido_fulfilled, name="mark_cumplido_fulfilled"),
    path('get_commitments_by_project_id', views.get_commitments_by_project_id, name="get_commitments_by_project_id"),
]
