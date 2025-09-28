from django.db import models
from django.contrib.auth.models import User
from .organization import Organization


class UserProfile(models.Model):
    """
    Perfil de usuario que extiende el modelo User de Django
    con campos personalizados
    """
    # Relación uno a uno con el modelo User de Django
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile',
        verbose_name="Usuario"
    )
    
    # Organización asociada al usuario
    organization = models.ForeignKey(
        Organization,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='users',
        verbose_name="Organización"
    )

    class Meta:
        verbose_name = "Perfil de Usuario"
        verbose_name_plural = "Perfiles de Usuario"

    def __str__(self):
        return f"{self.user.username} - {self.organization.name if self.organization else 'Sin organización'}"

    @property
    def full_name(self):
        """Retorna el nombre completo del usuario"""
        return f"{self.user.first_name} {self.user.last_name}".strip() or self.user.username

    @property
    def email(self):
        """Acceso directo al email del usuario"""
        return self.user.email