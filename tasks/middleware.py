from django.http import JsonResponse

class BlockDirectAccessMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path == '/api/tasks/' and 'HTTP_REFERER' not in request.META:
            return JsonResponse({'error': 'Acesso direto nao permitido.'}, status=403)   
        return self.get_response(request)