from django.urls import path, include
from pprint import pprint
from rest_framework_nested import routers
from core import views

router = routers.DefaultRouter()

router.register('customauth', views.CustomAuthViewSet, basename='customauth')

urlpatterns = router.urls

pprint(urlpatterns)
