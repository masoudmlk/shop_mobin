# from channels.generic.websocket import WebsocketConsumer, AsyncWebsocketConsumer
# from django.db.models import QuerySet
# import json
# from asgiref.sync import async_to_sync
# from message.models import Message, Chat
# from message.serializers import MessageSerializer
# from rest_framework.renderers import JSONRenderer
# from django.contrib.auth import get_user_model
#
# user = get_user_model()
#
# class ChatConsumer(WebsocketConsumer):
#
#
#
#     def new_message(self, data):
#         print(data)
#         data = eval(data)
#         message = data.get('message')
#         author = data.get('username')
#         room_name = data.get('room_name')
#         print(message, type(message))
#         print(author, type(author))
#         print(room_name, type(room_name))
#
#         uesr_obj = user.objects.filter(username=author).first()
#         chat_room = Chat.objects.filter(room_name=room_name).first()
#         message = Message.objects.create(author=uesr_obj, content=message, related_chat=chat_room)
#         print(message)
#         message_json = self.message_serializer(message)
#         result = eval(message_json)
#         self.send_to_chat_message(result)
#
#     def fetch_message(self, data=None):
#         data = eval(data)
#         room_name = data.get("room_name")
#         qs = Message.last_message(room_name)
#         message_json = self.message_serializer(qs)
#         content = {
#             'message': eval(message_json),
#         }
#         print(content['message'])
#         self.chat_message(content)
#
#     def message_serializer(self, qs):
#         many = True if isinstance(qs, QuerySet) else False
#         serializer = MessageSerializer(qs, many=many)
#         content = JSONRenderer().render(serializer.data)
#         return content
#
#     COMMANDS = {
#         'new_message': new_message,
#         'fetch_message': fetch_message,
#     }
#
#     def connect(self):
#         print(self.scope['url_route']['kwargs'])
#
#         self.room_name = self.scope['url_route']['kwargs']['room_name']
#         self.room_group_name = f"chat_{self.room_name}"
#
#         async_to_sync(self.channel_layer.group_add)(
#             self.room_group_name,
#             self.channel_name
#         )
#
#         self.accept()
#
#     def disconnect(self, close_code):
#         async_to_sync(self.channel_layer.group_discard)(
#             self.room_group_name,
#             self.channel_name
#         )
#
#
#     def receive(self, text_data=None, bytes_data=None):
#         print(text_data)
#         text_data_dict = json.loads(text_data)
#         message = text_data_dict.get("message")
#         username = text_data_dict.get('username', None)
#         if isinstance(message, Message):
#             message = message.content
#         command = text_data_dict.get("command")
#         method = self.COMMANDS.get(command)
#         if method is not None:
#             method(self, text_data)
#
#             # async_to_sync(self.channel_layer.group_send)(
#             #     self.room_group_name,
#             #     {
#             #         'type': 'chat_message',
#             #         'message': message,
#             #
#             #     }
#             # )
#
#         #
#         # self.send(text_data=json.dumps({
#         #     'message': message,
#         # }))
#
#     def chat_message(self, event):
#         self.send(text_data=json.dumps(event))
#
#     def send_to_chat_message(self, message):
#         async_to_sync(self.channel_layer.group_send)(
#             self.room_group_name,
#             {
#                 'type': 'chat_message',
#                 'message': message,
#
#             }
#         )
#
# # class ChatConsumer(AsyncWebsocketConsumer):
# #
# #     async def connect(self):
# #         print(self.scope['url_route']['kwargs'])
# #
# #         self.room_name = self.scope['url_route']['kwargs']['room_name']
# #         self.room_group_name = f"chat_{self.room_name}"
# #
# #         await self.channel_layer.group_add(
# #             self.room_group_name,
# #             self.channel_name
# #         )
# #
# #         await self.accept()
# #
# #     async def disconnect(self, close_code):
# #         await self.channel_layer.group_discard(
# #             self.room_group_name,
# #             self.channel_name
# #         )
# #
# #
# #     async def receive(self, text_data=None, bytes_data=None):
# #         text_data_dict = json.loads(text_data)
# #         message = text_data_dict.get("message")
# #
# #         await self.channel_layer.group_send(
# #             self.room_group_name,
# #             {
# #                 'type': 'chat_message',
# #                 'message': message,
# #                 'command': "mlkco mmmand",
# #             }
# #         )
# #
# #         #
# #         # self.send(text_data=json.dumps({
# #         #     'message': message,
# #         # }))
# #
# #     async def chat_message(self, event):
# #         message = event['message']
# #         print(event)
# #         await self.send(text_data=json.dumps({
# #             'message': message,
# #         }))
#
