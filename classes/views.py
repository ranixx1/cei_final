from django.urls import reverse_lazy
from django.views.generic.edit import CreateView
from .models import Turma
from django.views.generic import ListView, CreateView, DetailView, DeleteView
from django.views import View
from django.views.generic.edit import UpdateView
from .forms import TurmaForm
from django.contrib.auth.models import Group
from django.urls import reverse_lazy
from django.views.generic import DeleteView
from .models import Turma
from braces.views import LoginRequiredMixin, GroupRequiredMixin
from django.contrib import messages
from django.contrib.auth.models import User
from django.shortcuts import redirect
from profiles.models import CustomUser
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse


class TurmaCreateView(GroupRequiredMixin, LoginRequiredMixin,  CreateView):
    group_required = u"Administrador"
    login_url = reverse_lazy('login')
    model = Turma
    form_class = TurmaForm
    template_name = 'classes/cadastrar_turma.html'
    success_url = reverse_lazy('lista-turmas')

    def form_valid(self, form):
        response = super().form_valid(form)
        
        turma = form.instance
        group_name = f"{turma.nome}_{turma.serie}_{turma.turno}_{turma.curso}"
        Group.objects.get_or_create(name=group_name)
        
        return response
