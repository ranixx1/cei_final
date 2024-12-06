from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    id = models.BigAutoField(primary_key=True)
    turma = models.ForeignKey('classes.Turma', on_delete=models.SET_NULL, blank=True, null=True, related_name='customuser_set')

    @property
    def cargo(self):
        if self.groups.filter(name="Tutor").exists():
            return "Aluno e Tutor"
        elif self.groups.filter(name="Discente").exists():
            return "Aluno"
        elif self.groups.filter(name="Docente").exists():
            return "Professor"
        elif self.groups.filter(name="Administrador").exists():
            return "Administrador"
        return "Indefinido"

    @property
    def perfilturma(self):
        if self.groups.filter(name="Discente").exists() or self.groups.filter(name="Tutor").exists():
            return self.turma 
        elif self.groups.filter(name="Docente").exists():
            return "Voce é professor :D"
        elif self.groups.filter(name="Administrador").exists():
            return "Voce é Administrador \o/"
        return "Indefinido"
