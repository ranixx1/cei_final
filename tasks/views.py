from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from .forms import TaskForm
from django.contrib import messages
from django.http import JsonResponse
from .models import Task
from datetime import datetime, date, timedelta
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.views import View
from braces.views import LoginRequiredMixin, GroupRequiredMixin
from django.views.generic import TemplateView
from django.utils import timezone
from classes.models import Turma
from django.db.models import Q
from django.utils.timezone import localdate

class TaskListView(GroupRequiredMixin, LoginRequiredMixin, ListView):
    group_required = [u"Docente", u"Tutor"]
    login_url = reverse_lazy('login')
    model = Task
    template_name = 'tasks/list.html'
    context_object_name = 'tasks'
    ordering = '-created_at'

    def get_queryset(self):
        user_groups = self.request.user.groups.values_list('name', flat=True)
        if "Administrador" in user_groups:
            return Task.objects.all()
        return Task.objects.filter(usuario=self.request.user)


class TaskDetailView(DetailView):
    model = Task
    template_name = 'tasks/task.html'
    context_object_name = 'task'


class TaskCreateView(GroupRequiredMixin, LoginRequiredMixin, CreateView):
    group_required = [u"Docente", u"Tutor"]
    login_url = reverse_lazy('login')
    model = Task
    form_class = TaskForm
    template_name = 'tasks/addtask.html'
    success_url = reverse_lazy('task-list')

    def form_valid(self, form):
        form.instance.usuario = self.request.user
        url = super().form_valid(form)
        return url


class TaskUpdateView(GroupRequiredMixin, LoginRequiredMixin, UpdateView):
    group_required = [u"Docente", u"Tutor"]
    login_url = reverse_lazy('login')
    model = Task
    form_class = TaskForm
    template_name = 'tasks/edittask.html'
    context_object_name = 'task'
    success_url = reverse_lazy('task-list')

    def dispatch(self, request, *args, **kwargs):
        task = self.get_object()
        user = self.request.user
        if task.usuario != user and not user.groups.filter(name="Administrador").exists():
            messages.error(request, "Você não tem permissão para editar esta tarefa.")
            return redirect('task-list')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        return super().form_valid(form)


class TaskDeleteView(GroupRequiredMixin, LoginRequiredMixin, DeleteView):
    group_required = [u"Docente", u"Tutor"]
    login_url = reverse_lazy('login')
    model = Task
    template_name = 'tasks/deletetask.html'
    success_url = reverse_lazy('task-list')

    def dispatch(self, request, *args, **kwargs):
        task = self.get_object()
        user = self.request.user
        if task.usuario != user and not user.groups.filter(name="Administrador").exists():
            messages.error(request, "Você não tem permissão para excluir esta tarefa.")
            return redirect('task-list')
        return super().dispatch(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Tarefa deletada com sucesso.')
        return super().delete(request, *args, **kwargs)



class CalendarView(TemplateView):
    template_name = 'tasks/calendar.html'

    def get_context_data(self, **kwargs):
        user_turma = getattr(self.request.user, 'turma', None)
        context = super().get_context_data(**kwargs)

        user_groups = self.request.user.groups.values_list('name', flat=True) if self.request.user.is_authenticated else []
        is_tutor = 'Tutor' in user_groups
        is_discente = 'Discente' in user_groups
        is_docente = 'Docente' in user_groups
        is_administrador = 'Administrador' in user_groups
        today = timezone.localdate()

        if is_administrador:
            events_today = Task.objects.filter(
                start_date__lte=today,
                end_date__gte=today
            )
        elif not self.request.user.is_authenticated:
            events_today = Task.objects.filter(
                start_date__lte=today,
                end_date__gte=today
            )
        elif is_tutor and user_turma:
            events_today = Task.objects.filter(
                Q(turma=user_turma) | Q(usuario=self.request.user),
                start_date__lte=today,
                end_date__gte=today
            )
        elif is_discente and user_turma:
            events_today = Task.objects.filter(
                turma=user_turma,
                start_date__lte=today,
                end_date__gte=today
            )
        elif is_docente:
            events_today = Task.objects.filter(
                usuario=self.request.user,
                start_date__lte=today,
                end_date__gte=today
            )
        else:
            events_today = Task.objects.filter(
                start_date__lte=today,
                end_date__gte=today
            )
        context['events_today'] = events_today
        context['turmas'] = Turma.objects.all()
        return context


class TaskEventsView(View):
    def get(self, request, *args, **kwargs):
        turma_id = request.GET.get('turma_id', None)
        user_turma = getattr(request.user, 'turma', None)
        user_groups = request.user.groups.values_list('name', flat=True) if request.user.is_authenticated else []
        is_administrador = 'Administrador' in user_groups
        is_tutor = 'Tutor' in user_groups
        is_discente = 'Discente' in user_groups
        is_docente = 'Docente' in user_groups

        if is_administrador:
            tasks = Task.objects.all()
        elif turma_id:
            tasks = Task.objects.filter(turma_id=turma_id)
        elif is_tutor and user_turma:
            tasks = Task.objects.filter(
                Q(turma=user_turma) | Q(usuario=request.user)
            )
        elif is_discente and user_turma:
            tasks = Task.objects.filter(turma=user_turma)
        elif is_docente:
            tasks = Task.objects.filter(usuario=request.user)
        else:
            tasks = Task.objects.all()

        events = []
        for task in tasks:
            if task.start_date and task.start_time and task.end_date and task.end_time:
                start_datetime = datetime.combine(task.start_date, task.start_time)
                end_datetime = datetime.combine(task.end_date, task.end_time)
                events.append({
                    'id': task.id,
                    'title': task.title,
                    'start': start_datetime.isoformat(),
                    'end': end_datetime.isoformat(),
                    'description': task.description,
                })

        return JsonResponse(events, safe=False)


class EventCountView(LoginRequiredMixin, TemplateView):
    login_url = reverse_lazy('login')
    template_name = 'tasks/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        today = localdate()
        start_of_week = today
        end_of_week = today + timedelta(days=(6 - today.weekday()))
        user_groups = user.groups.values_list('name', flat=True)
        is_administrador = 'Administrador' in user_groups
        is_tutor = 'Tutor' in user_groups
        is_discente = 'Discente' in user_groups
        is_docente = 'Docente' in user_groups

        if is_administrador:
            tasks_today = Task.objects.filter(
                start_date__lte=today, end_date__gte=today
            )
            tasks_week = Task.objects.filter(
                start_date__gte=today, end_date__lte=end_of_week
            )
            total_tasks = Task.objects.filter(
                start_date__gte=today
            )
            context['tasks'] = Task.objects.all()
        elif is_tutor and user.turma:
            tasks_today = Task.objects.filter(
                Q(turma=user.turma) | Q(usuario=user),
                start_date__lte=today, end_date__gte=today
            )
            tasks_week = Task.objects.filter(
                Q(turma=user.turma) | Q(usuario=user),
                start_date__gte=today, end_date__lte=end_of_week
            )
            total_tasks = Task.objects.filter(
                Q(turma=user.turma) | Q(usuario=user),
                start_date__gte=today
            )
            context['tasks'] = Task.objects.filter(Q(turma=user.turma) | Q(usuario=user))
        elif is_discente and user.turma:
            tasks_today = Task.objects.filter(
                turma=user.turma, start_date__lte=today, end_date__gte=today
            )
            tasks_week = Task.objects.filter(
                turma=user.turma, start_date__gte=today, end_date__lte=end_of_week
            )
            total_tasks = Task.objects.filter(
                turma=user.turma, start_date__gte=today
            )
            context['tasks'] = Task.objects.filter(turma=user.turma)
        elif is_docente:
            tasks_today = Task.objects.filter(
                usuario=user, start_date__lte=today, end_date__gte=today
            )
            tasks_week = Task.objects.filter(
                usuario=user, start_date__gte=today, end_date__lte=end_of_week
            )
            total_tasks = Task.objects.filter(
                usuario=user, start_date__gte=today
            )
            context['tasks'] = Task.objects.filter(usuario=user)
        else:
            tasks_today = Task.objects.none()
            tasks_week = Task.objects.none()
            total_tasks = Task.objects.none()
            context['tasks'] = Task.objects.none()

        context['tasks_today_count'] = tasks_today.count()
        context['tasks_week_count'] = tasks_week.count()
        context['total_tasks_count'] = total_tasks.count()

        return context


class ChartYear(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        year_data = [0] * 12
        user = request.user
        user_groups = user.groups.values_list('name', flat=True) if user.is_authenticated else []
        is_administrador = 'Administrador' in user_groups
        is_tutor = 'Tutor' in user_groups
        is_discente = 'Discente' in user_groups
        is_docente = 'Docente' in user_groups

        if is_administrador:
            tasks = Task.objects.all()
        elif is_tutor and hasattr(user, 'turma'):
            tasks = Task.objects.filter(
                Q(turma=user.turma) | Q(usuario=user)
            )
        elif is_discente and hasattr(user, 'turma'):
            tasks = Task.objects.filter(turma=user.turma)
        elif is_docente:
            tasks = Task.objects.filter(usuario=user)
        else:
            tasks = Task.objects.none()

        for task in tasks:
            if task.start_date:
                year_data[task.start_date.month - 1] += 1

        return JsonResponse(year_data, safe=False)


def verificar_user(request):
    user_in_docente = request.user.groups.filter(name="Docente").exists()
    return render(request, 'base.html', {'user_in_docente': user_in_docente})