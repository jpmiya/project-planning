from django.db import models

class ONG (models.Model):
    id_ong = models.AutoField(primary_key=True)
    nombre_ong = models.CharField(max_length=50)
    
    def __str__(self):
        return "ONG " + self.nombre_ong