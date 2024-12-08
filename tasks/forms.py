from django import forms
from .models import Task
from django.forms import DateInput
from django import forms

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ["title", "description", "turma", "start_date", "end_date", "start_time", "end_time"]

        widgets = {
            "title": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Insira o título do evento"}
            ),
            "description": forms.Textarea(
                attrs={"class": "form-control", "placeholder": "Insira a descrição do evento", "rows": 3 }
            ),
            "turma": forms.Select(
                attrs={"class": "form-select", "aria-label": "Selecionar turma"}
            ),
            "start_date": DateInput(attrs={"class": "form-control", "placeholder": "dd/mm/aaaa"}),
            "end_date": DateInput(attrs={"class": "form-control", "placeholder": "dd/mm/aaaa"}),
            "start_time": DateInput(attrs={"class": "form-control", "placeholder": "hh:mm:ss"}),
            "end_time": DateInput(attrs={"class": "form-control", "placeholder": "hh:mm:ss"}),
        }

    def __init__(self, *args, **kwargs):
        super(TaskForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        task = super().save(commit=False)
        task.id_turma = self.cleaned_data['turma'].id
        if commit:
            task.save()
        return task