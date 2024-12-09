from django.contrib.auth.models import Group

def user_in_discente(request):
    if request.user.is_authenticated:
        return {'user_in_discente': request.user.groups.filter(name="Discente").exists()}
    return {'user_in_discente': False}