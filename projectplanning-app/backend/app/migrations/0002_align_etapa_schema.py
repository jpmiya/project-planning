"""Migration para alinear la tabla `app_etapa` con el modelo actual.

Este archivo intenta transformar la tabla existente (esquema "viejo")
renombrando/añadiendo columnas para que coincida con el modelo definido en
`app/models/etapa.py`. Se asume PostgreSQL; ajustá las sentencias SQL si usás
otra base de datos.

Si estás en desarrollo y podés descartar datos, la opción más sencilla es
recrear la base de datos y ejecutar `migrate`. Este migration intenta hacer
la transición sin perder datos.
"""
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0001_initial'),
    ]

    operations = [
        migrations.RunSQL(
            sql=[
                # Renombrar columna 'nombre' -> 'nombre_etapa' si existe
                "ALTER TABLE app_etapa RENAME COLUMN nombre TO nombre_etapa;",
                # Añadir columna 'nombre_aporte' si no existe (varchar 255, default '')
                "ALTER TABLE app_etapa ADD COLUMN IF NOT EXISTS nombre_aporte varchar(255) NOT NULL DEFAULT '';",
                # Añadir columna 'cant_aporte_necesario' si no existe (integer, default 0)
                "ALTER TABLE app_etapa ADD COLUMN IF NOT EXISTS cant_aporte_necesario integer NOT NULL DEFAULT 0;",
                # Añadir columna 'cloud_id' si no existe (nullable integer)
                "ALTER TABLE app_etapa ADD COLUMN IF NOT EXISTS cloud_id integer;",
            ],
            reverse_sql=[
                # No revertimos automáticamente los cambios destructivos
                "",
            ],
        ),
    ]
