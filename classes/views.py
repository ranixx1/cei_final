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

class ListaTurmas(ListView):
    model = Turma
    template_name = 'classes/lista_turmas.html'
    context_object_name = 'turmas'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_admin'] = self.request.user.groups.filter(name="Administrador").exists()
        return context

class TurmaDeleteView(GroupRequiredMixin, LoginRequiredMixin, DeleteView):
    group_required = u"Administrador"
    login_url = reverse_lazy('login')
    model = Turma
    template_name = 'classes/deletar_turma.html'
    success_url = reverse_lazy('lista-turmas')

    def post(self, request, *args, **kwargs):
        turma = self.get_object()

        error_message = turma.can_delete()
        if error_message:
            messages.error(self.request, error_message)
            return self.get(self.request, *args, **kwargs)

        group_name = f"{turma.nome}_{turma.serie}_{turma.turno}_{turma.curso}"
        group = Group.objects.filter(name=group_name).first()
        if group:
            group.delete()

        messages.success(self.request, "Turma excluída com sucesso!")
        return super().delete(request, *args, **kwargs)
    
class TurmaMembersView(DetailView):
    model = Turma
    template_name = 'classes/listar_membros.html'
    context_object_name = 'turma'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_servidor'] = self.request.user.groups.filter(name="Administrador").exists() or self.request.user.groups.filter(name="Docente").exists()
        context['is_admin'] = self.request.user.groups.filter(name="Administrador").exists()
        turma = self.object
        group_name = f"{turma.nome}_{turma.serie}_{turma.turno}_{turma.curso}"
        group = Group.objects.filter(name=group_name).first()
        context['members'] = group.user_set.all() if group else []
        return context