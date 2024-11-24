from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from .forms import TaskForm
from django.contrib import messages
from django.http import JsonResponse
from .models import Task
from datetime import datetime, timedelta
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.views import View
from braces.views import LoginRequiredMixin, GroupRequiredMixin


class TaskListView(ListView):
    model = Task
    template_name = 'tasks/list.html'
    context_object_name = 'tasks'
    ordering = '-created_at'


class TaskDetailView(DetailView):
    model = Task
    template_name = 'tasks/task.html'
    context_object_name = 'task'


def calendar(request):
    return render(request, 'tasks/calendar.html')


def home(request):
    return render(request, 'tasks/home.html')



class TaskEventsView(View):
    def get(self, request, *args, **kwargs):
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