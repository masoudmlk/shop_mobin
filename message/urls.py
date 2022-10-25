from django.urls import path, include
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
# from message.views import index, room
from django.contrib.auth import views
from rest_framework.routers import SimpleRouter

from message.views import BadWordViewSet, GroupViewSet
from message import views
from pprint import pprint

router = SimpleRouter()
router.register('badword', BadWordViewSet)
pprint(router.urls)
router.register('group', GroupViewSet, basename='group')

urlpatterns = [
    path("groups/join/<str:group_id>/", views.JoinGroup.as_view()),
    path("groups/remove/<str:group_id>/", views.RemoveFromGroup.as_view()),
    path("groups/sendToAll/", views.SendMessageToGroups.as_view()),
    path("groups/sendToAll/", views.SendMessageToGroups.as_view()),

    path('message-page/', views.index, name='message_index'),
    path("message-page/<int:pk>/", views.room, name='massage_page'),
    path("login/<str:username>/", views.login),
    path("logout/<str:username>/", views.logout),

]
urlpatterns += router.urls


# urlpatterns = [
#     # path('', index, name='message_index'),
#     # path("<str:room_name>/", room, name='room_index'),
#     path("badword/", BadWordViewSet.as_view({{'get': 'list'}}), name='badword')
# ]
