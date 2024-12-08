from django import forms
from .models import Turma


class TurmaForm(forms.ModelForm):
    class Meta:
        model = Turma
        fields = ['nome', 'serie', 'turno', 'curso']
        widgets = {
            'nome': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Coloque em sigla. Ex: INFO4V'
            }),
            'serie': forms.Select(attrs={'class': 'form-select'}),
            'turno': forms.Select(attrs={'class': 'form-select'}),
            'curso': forms.Select(attrs={'class': 'form-select'}),
        }