from channels.generic.websocket import WebsocketConsumer, AsyncWebsocketConsumer
from channels.layers import get_channel_layer
from django.db.models import QuerySet
import json
from asgiref.sync import async_to_sync
from message.models import Message, Group
from message.serializers import MessageSerializer
from rest_framework.renderers import JSONRenderer
from django.contrib.auth import get_user_model
from message.utils import FilterText
User = get_user_model()


class ChatConsumer(WebsocketConsumer):

    COMMANDS = {
        'new_message': 'new_message',
    }

    def connect(self):

        self.group_id = self.scope['url_route']['kwargs']['group_id']
        self.group_name = ChatConsumer.group_name(self.group_id)

        async_to_sync(self.channel_layer.group_add)(
            self.group_name,
            self.channel_name
        )

        self.accept()

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.group_name,
            self.channel_name
        )

    def receive(self, text_data=None, bytes_data=None):
        text_data_dict = json.loads(text_data)
        message = text_data_dict.get("message")
        username = text_data_dict.get('username', None)
        command = text_data_dict.get("command")

        message = (FilterText(message)).filter()

        if command == self.COMMANDS['new_message']:

            user = self.scope['user']
            Message.objects.create(author=user, content=message, related_group_id=self.group_id)

            self.send_to_chat_message(message, username, self.COMMANDS['new_message'])

    def chat_message(self, event):
        print(event)
        self.send(text_data=json.dumps(event))

    def send_to_chat_message(self, message, username, command):
        async_to_sync(self.channel_layer.group_send)(
            self.group_name,
            {
                'type': 'chat_message',
                'message': message,
                'username': username,
                'command': command,
            }
        )
    @staticmethod
    def send_group_message(message, username, command, group_id):
        group_name = ChatConsumer.group_name(group_id)

        channel_layer = get_channel_layer()
        message = FilterText(message).filter()
        async_to_sync(channel_layer.group_send)(
            group_name,
            {
                'type': 'chat_message',
                'message': message,
                'username': username,
                'command': command,
            }
        )

    @staticmethod
    def group_name(group_id):
        return f"chat_{group_id}"