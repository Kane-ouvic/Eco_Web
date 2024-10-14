from django.apps import AppConfig
from django.shortcuts import redirect
from django.urls import reverse


class BlogConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'blog'

class LoginRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        if response.status_code == 302 and response.url.startswith(reverse('login')):
            # 檢查是否是由 login_required 引起的重定向
            next_url = request.GET.get('next')
            if next_url:
                return redirect(reverse('login_reminder') + f'?next={next_url}')

        return response
