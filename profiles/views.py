from django.views.generic.edit import CreateView, UpdateView
from django.contrib.auth.models import User, Group
from django.views.generic.detail import DetailView
from .models import CustomUser
from django.urls import reverse_lazy
from .forms import UsuarioForm
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.contrib import messages
from braces.views import LoginRequiredMixin, GroupRequiredMixin
from django.views.generic.list import ListView
from .forms import ProfessorForm, ProfessorEditForm


class CreateUser(CreateView):
    template_name = "register/register.html"
    form_class = UsuarioForm
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        turma = form.cleaned_data['turma']
        group_name = f"{turma.nome}_{turma.serie}_{turma.turno}_{turma.curso}"
        group_turma = get_object_or_404(Group, name=group_name)
        grupo = get_object_or_404(Group, name="Discente")
        url = super().form_valid(form)
        self.object.groups.add(group_turma)
        self.object.groups.add(grupo)
        self.object.save()
        return url

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['titulo'] = "Registro de novo usuário"
        context['botão'] = "Cadastrar"
        return context


class UserUpdate(UpdateView):
    template_name = "registration/edituser.html"
    model = CustomUser
    fields = ['username', 'email', 'turma']
    success_url = reverse_lazy("dashboard")

    def get_object(self, queryset=None):
        self.object = self.request.user
        return self.object

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        user = self.request.user
    
        if user.groups.filter(name='Docente').exists() or user.groups.filter(name='Administrador').exists():
            form.fields.pop('turma')
        elif user.groups.filter(name='Discente').exists():
            pass
        
        return form

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['page_title'] = 'Editar meus dados'
        return context

    def form_valid(self, form):
        user = form.instance
        original_user = CustomUser.objects.get(pk=user.pk)
        old_turma = original_user.turma

        if 'turma' in form.cleaned_data:
            new_turma = form.cleaned_data['turma']

            print(f"Old turma: {old_turma}")
            print(f"New turma: {new_turma}")

            if old_turma != new_turma:
                if old_turma:
                    old_group_name = f"{old_turma.nome}_{old_turma.serie}_{old_turma.turno}_{old_turma.curso}"
                    old_group = Group.objects.filter(name=old_group_name).first()
                    if old_group:
                        print(f"Removing from group: {old_group.name}")
                        user.groups.remove(old_group)

                user.turma = new_turma

                new_group_name = f"{new_turma.nome}_{new_turma.serie}_{new_turma.turno}_{new_turma.curso}"
                new_group, created = Group.objects.get_or_create(name=new_group_name)
                print(f"Adding to group: {new_group.name}")
                user.groups.add(new_group)
        else:
            print("Campo 'turma' não está presente no formulário para o usuário atual.")

        user.save()
        return super().form_valid(form)



class UserDetailView(GroupRequiredMixin, LoginRequiredMixin, DetailView):
    group_required = [u"Docente", u"Administrador"]
    login_url = reverse_lazy('login')
    model = CustomUser
    template_name = "registration/user_detail.html"
    context_object_name = "user_detail"

    def post(self, request, *args, **kwargs):
        user = self.get_object()
        
        tutor_group, _ = Group.objects.get_or_create(name="Tutor")
        discente_group, _ = Group.objects.get_or_create(name="Discente")
        
        if "toggle_tutor" in request.POST:
            if user.groups.filter(name="Tutor").exists():
                user.groups.remove(tutor_group)
                user.groups.add(discente_group)
                messages.success(request, f"{user.username} não é mais Tutor")
            else:
                user.groups.add(tutor_group)
                user.groups.remove(discente_group)
                messages.success(request, f"{user.username} agora é Tutor")
        
        return redirect('user_detail', pk=user.id)


class DocenteListView(ListView):
    template_name = "registration/docentes_list.html"
    model = CustomUser
    context_object_name = "docentes"

    def get_queryset(self):
        docente_group = Group.objects.filter(name="Docente").first()
        if docente_group:
            return CustomUser.objects.filter(groups=docente_group)
        return CustomUser.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_admin'] = self.request.user.groups.filter(name="Administrador").exists()
        context['titulo'] = "Lista de Professores"
        return context


class AddProfessorView(GroupRequiredMixin, LoginRequiredMixin, CreateView):
    group_required = u"Administrador"
    login_url = reverse_lazy('login')
    template_name = "registration/add_professor.html"
    form_class = ProfessorForm
    success_url = reverse_lazy('docentes_list')

    def form_valid(self, form):
        response = super().form_valid(form)

        docente_group, created = Group.objects.get_or_create(name="Docente")
        self.object.groups.add(docente_group)
        self.object.save()

        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = "Adicionar Professor"
        context['botao'] = "Adicionar"
        return context

class DocenteDetailView(GroupRequiredMixin, LoginRequiredMixin, DetailView):
    group_required = u"Administrador"
    login_url = reverse_lazy('login')
    model = CustomUser
    template_name = "registration/detail_docente.html"
    context_object_name = "docente"
    login_url = reverse_lazy('login')

    def get_queryset(self):
        docente_group = Group.objects.filter(name="Docente").first()
        if docente_group:
            return CustomUser.objects.filter(groups=docente_group)
        return CustomUser.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = f"Detalhes do Professor: {self.object.username}"
        return context

    def post(self, request, *args, **kwargs):
        docente = self.get_object()

        if 'remove_professor' in request.POST:
            try:
                docente.delete()

                messages.success(request, f"O professor {docente.username} foi removido com sucesso!")
            except Exception as e:
                messages.error(request, f"Erro ao remover o professor: {str(e)}")

            return redirect('docentes_list')

        return redirect('docente_detail', pk=docente.pk)


class EditProfessorView(GroupRequiredMixin, LoginRequiredMixin, UpdateView):
    group_required = u"Administrador"
    login_url = reverse_lazy('login')
    template_name = "registration/edit_professor.html"
    model = CustomUser
    form_class = ProfessorEditForm
    context_object_name = "professor"
    success_url = reverse_lazy('docentes_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = f"Editar Dados do Professor: {self.object.username}"
        context['botao'] = "Salvar Alterações"
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f"Os dados do professor {self.object.username} foram atualizados com sucesso!")
        return response

    def form_invalid(self, form):
        messages.error(self.request, "Houve um erro ao tentar atualizar os dados do professor. Verifique os campos e tente novamente.")
        return super().form_invalid(form)
