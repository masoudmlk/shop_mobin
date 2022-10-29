from django.shortcuts import get_object_or_404

from rest_framework.viewsets import GenericViewSet, ModelViewSet
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework import status
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin, CreateModelMixin, UpdateModelMixin
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination

from message.serializers import BadWordSerializer, GroupSerializer, UsernameListSerializer, MessageToGroupsSerializer, SimpleGroupSerializer
from message.models import BadWord, Group, Message
from django.contrib.auth import get_user_model
from django.contrib.auth import login as auth_login, logout as auth_logout
User = get_user_model()

from django.shortcuts import render
from django.utils.safestring import mark_safe
# from message.models import Chat
import json
from django.urls import reverse
from django.http import HttpResponseRedirect, HttpResponse
from message.consumers import ChatConsumer
from django.contrib.auth.decorators import login_required

@login_required
def index(request):

    user = request.user
    groups = Group.objects.filter(members=user, active=True)
    left_links = {}
    for group in groups:
        left_links[group.pk] = reverse('left_group', kwargs={"pk": group.pk})
    context = {'groups': groups, "left_group_links": left_links}

    return render(request, "chat/index.html", context)

@login_required
def group(request, pk):
    username = request.user.username
    group = Group.objects.filter(pk=pk, members=request.user, active=True).first()

    if group is not None:
        messages = Message.objects.filter(related_group=group).select_related('author').order_by('created_at')
        context = {
            'group': pk,
            'username': mark_safe(json.dumps(username)),
            'messages': messages,
            'left_group_link': reverse('left_group', kwargs={"pk": group.pk}),
        }
        return render(request, "chat/group.html", context)
    return HttpResponse("404", status.HTTP_404_NOT_FOUND)

def login(request, username):

    user = User.objects.filter(username=username).first()
    auth_login(request, user)
    return HttpResponseRedirect(reverse('message_index'))


def logout(request):
    auth_logout(request)
    return HttpResponseRedirect(reverse('message_index'))

@login_required
def left_group(request, pk: int) -> HttpResponse:

    group = Group.objects.filter(Group, pk=pk).first()
    if group is not None:
        user = request.user
        group.members.remove(user)
        return HttpResponseRedirect(reverse('message_index'))
    return HttpResponse("404", status.HTTP_404_NOT_FOUND)


class BadWordViewSet(ModelViewSet):
    permission_classes = [IsAdminUser]
    serializer_class = BadWordSerializer
    queryset = BadWord.objects.filter(active=True)

    def get_serializer_context(self):
        return {'current_user': self.request.user}


class GroupViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = GroupSerializer

    def get_queryset(self):
        return Group.objects.filter(active=True, creator=self.request.user).select_related('creator').prefetch_related('members')

    def get_serializer_context(self):
        return {'current_user': self.request.user}


class JoinGroup(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, group_id):
        serializer = UsernameListSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username_list = serializer.validated_data.get("username_list")
        group_filter = {'pk': group_id, 'creator': self.request.user}
        group = get_object_or_404(Group, **group_filter)
        list_response = []
        for username in username_list:
            user = User.objects.filter(username=username).first()
            if user is not None:
                group.members.add(user)
                list_response.append({'username': username, 'status': 'success'})
            else:
                list_response.append({'username': username, 'status': 'failed'})
        return Response(list_response, status=status.HTTP_200_OK)


class RemoveFromGroup(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, group_id):
        serializer = UsernameListSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username_list = serializer.validated_data.get("username_list")
        group_filter = {'pk': group_id, 'creator': self.request.user}
        group = get_object_or_404(Group, **group_filter)
        list_response = []
        for username in username_list:
            user = User.objects.filter(username=username).first()
            if user is not None:
                group.members.remove(user)
                list_response.append({'username': username, 'status': 'removed'})
            # else:
            #     list_response.append({'username': username, 'status': 'failed to remove form group'})
        return Response(list_response, status=status.HTTP_200_OK)


class SendMessageToGroups(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = MessageToGroupsSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        ids = serializer.validated_data.get("ids")
        message = serializer.validated_data.get("message")
        list_response = []
        for group_id in ids:
            group = Group.objects.filter(pk=group_id, active=True).first()
            if group is not None:

                ChatConsumer.send_group_message(message, request.user.username, "new_message", group.pk)
                Message.objects.create(author=request.user, content=message, related_group=group)
                list_response.append({'group_id': group_id, 'status': 'success'})
            else:
                list_response.append({'group_id': group_id, 'status': 'failed'})

        return Response(list_response, status=status.HTTP_200_OK)

    def get(self, request):
        qs = Group.objects.filter(active=True).select_related('creator')
        serializer = SimpleGroupSerializer(qs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


