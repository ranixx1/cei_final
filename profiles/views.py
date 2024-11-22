from django.views.generic.edit import CreateView
from django.contrib.auth.models import User


class CreateUser(CreateView):
    template_name = "register.html"
    model = User
    fields = ['username', 'email', 'password']
