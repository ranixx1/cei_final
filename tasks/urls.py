from django.urls import path
from . import views
from .views import TaskListView, TaskDetailView, TaskEventsView

urlpatterns = [
    path('', views.home, name='home'),
    path('calendar/', views.calendar, name='calendar'),
    path('list/', TaskListView.as_view(), name='task-list'),
    path('task/<int:pk>/', TaskDetailView.as_view(), name='task-view'),  # Use pk para ID
    path('api/tasks/', TaskEventsView.as_view(), name='task_events'),  # Adiciona a nova view
]