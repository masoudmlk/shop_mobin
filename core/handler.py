from datetime import timedelta
from django.contrib.auth.signals import user_logged_in, user_logged_out
from rest_framework.response import Response
from core.models import User, AuthToken
from core.utils import Client



class UserHandler:

    @staticmethod
    def create_token(user: User, request) -> (AuthToken, str):

        if not isinstance(user, User):
            raise {"Error": "user instance is not valid"}

        # todo we should get timedelta form config file
        token, token_key = AuthToken.objects.create(user, timedelta(weeks=10000))
        if isinstance(token, AuthToken):
            token.user_agent = Client.get_user_agent(request)
            token.save(update_fields=['user_agent'])
        return token, token_key

    @staticmethod
    def logout(request):
        if request.user.is_authenticated:
            request._auth.delete()
            user_logged_out.send(sender=request.user.__class__,
                                 request=request, user=request.user)


