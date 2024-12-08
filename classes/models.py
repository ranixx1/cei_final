from django.db import models
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError


class Turma(models.Model):
    TURNO_CHOICES = [
        ('manha', 'Manhã'),
        ('tarde', 'Tarde'),
        ('noite', 'Noite'),
    ]

    CURSO_CHOICES = [
        ('edificacoes', 'Edificações'),
        ('informatica', 'Informática'),
        ('meio_ambiente', 'Meio Ambiente'),
        ('matematica', 'Matemática'),
    ]

    SERIE_CHOICES = [
        ('1', '1º Ano'),
        ('2', '2º Ano'),
        ('3', '3º Ano'),
        ('4', '4º Ano'),
    ]

    nome = models.CharField(max_length=8, unique=True)
    serie = models.CharField(max_length=1, choices=SERIE_CHOICES)
    turno = models.CharField(max_length=5, choices=TURNO_CHOICES)
    curso = models.CharField(max_length=15, choices=CURSO_CHOICES)

    def __str__(self):
        return f"{self.nome} - {self.serie}º {self.turno} ({self.curso})"

    def save(self, *args, **kwargs):
        if self.pk:
            turma_antiga = Turma.objects.get(pk=self.pk)
            old_group_name = f"{turma_antiga.nome}_{turma_antiga.serie}_{turma_antiga.turno}_{turma_antiga.curso}"
            new_group_name = f"{self.nome}_{self.serie}_{self.turno}_{self.curso}"

            if old_group_name != new_group_name:
                group = Group.objects.filter(name=old_group_name).first()
                if group:
                    group.name = new_group_name
                    group.save()
        else:
            group_name = f"{self.nome}_{self.serie}_{self.turno}_{self.curso}"
            Group.objects.get_or_create(name=group_name)

        super().save(*args, **kwargs)

    def can_delete(self):
        if self.customuser_set.exists():
            return "Não é possível excluir a turma porque existem usuários associados a ela. Verifique e tente novamente."
        if self.task_set.exists():
            return "Não é possível excluir a turma porque existem eventos associados a ela. Verifique e tente novamente."
        return None

    def delete(self, *args, **kwargs):
        error_message = self.can_delete()
        if error_message:
            raise ValidationError(error_message)
        super().delete(*args, **kwargs)
