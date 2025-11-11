"""Alinear esquema de la tabla `app_project` con el modelo actual.

Agrega columnas `case_id` y `cloud_id` si no existen. Esta migración usa
sentencias SQL compatibles con PostgreSQL; si usás otro motor puede requerir
ajustes.
"""
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0002_align_etapa_schema'),
    ]

    operations = [
        migrations.RunSQL(
            sql=[
                "ALTER TABLE app_project ADD COLUMN IF NOT EXISTS case_id integer;",
                "ALTER TABLE app_project ADD COLUMN IF NOT EXISTS cloud_id integer;",
            ],
            reverse_sql=[
                # No revert automático
                "",
            ],
        ),
    ]
