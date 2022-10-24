from datetime import timedelta
from django.contrib.auth.signals import user_logged_in, user_logged_out
from core.models import User, AuthToken, Score
from core.utils import Client
from typing import Tuple


def create_token(user: User, request) -> Tuple[AuthToken, str]:

    if not isinstance(user, User):
        raise {"Error": "user instance is not valid"}

    # todo we should get timedelta form config file
    token, token_key = AuthToken.objects.create(user, timedelta(weeks=10000))
    if isinstance(token, AuthToken):
        token.user_agent = Client.get_user_agent(request)
        token.save(update_fields=['user_agent'])
    return token, token_key


def logout(request):
    if request.user.is_authenticated:
        request._auth.delete()
        user_logged_out.send(sender=request.user.__class__,
                             request=request, user=request.user)


def create_update_score(user_id: int, product_id: int, score: int) -> Score:
    # check whether rate for product exist or not in order to create or update object
    scoreObj = Score.objects.filter(user_id=user_id, product_id=product_id).first()

    if scoreObj is not None and isinstance(scoreObj, Score):
        scoreObj.score = score
        scoreObj.save()
    else:
        scoreObj = Score.objects.create(user_id=user_id, product_id=product_id, score=score)
    return scoreObj

