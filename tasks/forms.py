from django import forms
from .models import Task
from django.forms import DateInput
from django import forms

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ["title", "description", "start_date", "end_date", "start_time", "end_time"]
        widgets = {
            "title": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Insira o título do evento"}
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "placeholder": "Insira a descrição do evento",
                }
            ),
            "start_date": DateInput(
                attrs={"class": "form-control"},
            ),
            "end_date": DateInput(
                attrs={"class": "form-control"},
            ),
            "start_time": DateInput(
                attrs={"class": "form-control"},
            ),
            "end_time": DateInput(
                attrs={"class": "form-control"},
            ),
        }
        exclude = ["user"]

    def __init__(self, *args, **kwargs):
        super(TaskForm, self).__init__(*args, **kwargs)