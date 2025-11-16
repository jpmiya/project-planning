import json
from django.db import transaction
from app.api.bonita import get_bonita_api
from app.models.etapa import Etapa
from django.contrib.auth.models import User
import datetime


class ProyectosServiceError(Exception):
    pass


def process_offers(project, seleccionadas, post_data, user=None):
    """Procesa las ofertas de ayuda (aportes) para un proyecto.

    Args:
        project: instancia de Project
        seleccionadas: lista de ids (strings) de etapas seleccionadas
        post_data: request.POST (Mapping) con los campos enviados
        user: usuario que realiza la acción (opcional)

    Returns:
        dict con keys: 'aportes' (list) y 'case_id' (str)

    Lanza ProyectosServiceError en caso de problemas predecibles.
    """
    if not seleccionadas:
        raise ProyectosServiceError('No se enviaron aportes.')

    case_id = getattr(project, 'case_id', None)
    if not case_id:
        raise ProyectosServiceError('El proyecto no tiene un case_id asociado en Bonita.')    

    aportes = []

    # Usamos una transacción para asegurar consistencia en decrementos
    with transaction.atomic():
        for etapa in project.etapas.all():
            eid = str(etapa.id)
            if eid in seleccionadas:
                if not etapa.requiere_ayuda:
                    raise ProyectosServiceError(f'La etapa "{etapa.nombre_aporte}" no está solicitando ayuda.')

                aporte_text = post_data.get(f'aporte_{eid}', '').strip()
                cantidad_raw = post_data.get(f'cantidad_{eid}', '').strip()

                try:
                    cantidad = int(cantidad_raw) if cantidad_raw != '' else None
                except (ValueError, TypeError):
                    raise ProyectosServiceError(f'Cantidad inválida para la etapa "{etapa.nombre_aporte}".')

                if cantidad is None or cantidad <= 0:
                    raise ProyectosServiceError(f'Debe indicar una cantidad válida para la etapa "{etapa.nombre_aporte}".')

                etapa_locked = Etapa.objects.select_for_update().get(pk=etapa.id)
                if cantidad + etapa_locked.cant_aporte_actual > etapa_locked.cant_aporte_necesario:
                    raise ProyectosServiceError(f'La cantidad solicitada para "{etapa.nombre_aporte}" excede la necesaria ({etapa_locked.cant_aporte_necesario}).')

                etapa_locked.cant_aporte_actual =etapa_locked.cant_aporte_actual + cantidad
                etapa_locked.save()
                ong_coolaboradora = User.objects.get(username=post_data.user)
                
                aportes.append({
                    'nombre_ong_coolaboradora': ong_coolaboradora.first_name,
                    'id_ong_coolaboradora': ong_coolaboradora.id,
                    'id_etapa_back': etapa_locked.id,
                    'aporte': aporte_text,
                    'cantidad': cantidad,
                    'fecha_compromiso': datetime.date.today,
                    'cumplido': False,
                })

        # Enviar las variables a Bonita
        payload = {
            "compromisos": aportes
        }
        api = get_bonita_api("franco.colapinto", "Williams_Fw46")
        activity = api.search_activity_by_case_id(case_id)
        if activity:
            print(f"Actividad encontrada: {activity}")
            # Asigna la tarea a un usuario
            bates = api.get_user_id_by_username("franco.colapinto")
            api.assign_task(activity, bates)
            # Intentar ejecutar la tarea
            executed = api.execute_user_task(activity, payload)
            print(f"Tarea ejecutada: {executed}")
        else:
            print("No se encontraron actividades pendientes (esto puede ser normal)")

    return {'aportes': aportes, 'case_id': case_id}
