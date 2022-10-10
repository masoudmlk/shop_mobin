from django.shortcuts import redirect
from django import http
from django.urls import reverse
from core.models import Token
from django.urls import resolve
from core.utils import Client
from core.views import CustomAuthViewSet

class CheckTokenMiddleware:
    response_redirect_class = http.HttpResponsePermanentRedirect

    PATH_ALLOW_ANY = ['customauth-list', 'customauth-login', 'customauth-send_otp', 'customauth-forget_pass', 'customauth-register']

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = request.user
        current_url = resolve(request.path_info).url_name
        if current_url in CheckTokenMiddleware.PATH_ALLOW_ANY:
            response = self.get_response(request)
            return response

        if request.user.is_authenticated:

            userAgent = Client.get_user_agent(request)
            token_exists = Token.objects.filter(user_id=user.pk, user_agent=userAgent).exists()

            if token_exists:
                response = self.get_response(request)
                return response
        return self.response_redirect_class(reverse('customauth-list'))
