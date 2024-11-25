from django.views.generic.edit import FormView
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy




class RegisterView(FormView):
    template_name = 'register.html'
    form_class = UserCreationForm
    success_url = reverse_lazy('login')


    def form_valid(self, form):
        # Salva o usuário se o formulário for válido
        form.save()
        return super().form_valid(form)

