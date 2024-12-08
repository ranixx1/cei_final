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
    

class ExcluirContaView(GroupRequiredMixin, LoginRequiredMixin, View):
    group_required = u"Administrador"
    login_url = reverse_lazy('login')
    
    def post(self, request, *args, **kwargs):
        user_id = request.POST.get('user_id')
        user = get_object_or_404(CustomUser, id=user_id)
        
        user.delete()
        
        messages.success(request, f"A conta de {user.username} foi excluída com sucesso.")
        
        return HttpResponseRedirect(reverse('turma_members', kwargs={'pk': kwargs.get('pk')}))

class UserUpdateView(GroupRequiredMixin, LoginRequiredMixin, UpdateView):
    group_required = u"Administrador"
    login_url = reverse_lazy('login')
    template_name = "registration/edituser.html"
    model = CustomUser
    fields = ['username', 'email', 'turma']
    
    def get_object(self, queryset=None):
        user_id = self.kwargs.get('pk')
        return get_object_or_404(CustomUser, pk=user_id)
    
    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        
        context['page_title'] = 'Editar Dados do Usuário'
        return context

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        user = self.get_object()
    
        if user.groups.filter(name='Docente').exists():
            form.fields.pop('turma')
        return form

    def form_valid(self, form):
        user = form.instance
        original_user = CustomUser.objects.get(pk=user.pk)
        old_turma = original_user.turma

        if 'turma' in form.cleaned_data:
            new_turma = form.cleaned_data['turma']

            if old_turma != new_turma:
                if old_turma:
                    old_group_name = f"{old_turma.nome}_{old_turma.serie}_{old_turma.turno}_{old_turma.curso}"
                    old_group = Group.objects.filter(name=old_group_name).first()
                    if old_group:
                        user.groups.remove(old_group)

                user.turma = new_turma

                new_group_name = f"{new_turma.nome}_{new_turma.serie}_{new_turma.turno}_{new_turma.curso}"
                new_group, created = Group.objects.get_or_create(name=new_group_name)
                user.groups.add(new_group)

        user.save()
        return super().form_valid(form)

    success_url = reverse_lazy('lista-turmas')

class TurmaUpdateView(GroupRequiredMixin, LoginRequiredMixin, UpdateView):
    group_required = u"Administrador"
    login_url = reverse_lazy('login')
    model = Turma
    form_class = TurmaForm
    template_name = 'classes/editar_turma.html'
    success_url = reverse_lazy('lista-turmas')

    def form_valid(self, form):
        turma = self.get_object()
        old_group_name = f"{turma.nome}_{turma.serie}_{turma.turno}_{turma.curso}"
        
        response = super().form_valid(form)
        
        new_group_name = f"{form.instance.nome}_{form.instance.serie}_{form.instance.turno}_{form.instance.curso}"
        
        if old_group_name != new_group_name:
            group = Group.objects.filter(name=old_group_name).first()
            if group:
                group.name = new_group_name
                group.save()
        
        return response