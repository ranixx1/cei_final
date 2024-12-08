from django.urls import path
from django.contrib.auth import views as auth_views
from .views import CreateUser, UserUpdate, UserDetailView, DocenteListView, AddProfessorView, DocenteDetailView, EditProfessorView


urlpatterns = [
    path('login/', auth_views.LoginView.as_view(template_name = 'registration/login.html'), name = "login"),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('docente/<int:pk>/editar/', EditProfessorView.as_view(), name='edit_professor'),
    path('docente/<int:pk>/', DocenteDetailView.as_view(), name='docente_detail'),
    path('docentes/', DocenteListView.as_view(), name='docentes_list'),
    path('user/<int:pk>/', UserDetailView.as_view(), name='user_detail'),
    path('registrar/', CreateUser.as_view(template_name = 'registration/register.html'), name = "register"),
    path('docentes/add/', AddProfessorView.as_view(), name='add_professor'),
    path('edituser/', UserUpdate.as_view(), name = "edituser"),
]
