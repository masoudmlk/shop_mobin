from rest_framework import serializers
from message.models import Message, BadWord, Group

from core.serializers import UserSerializer


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['__str__', 'content', 'created_at']


class BadWordSerializer(serializers.ModelSerializer):
    class Meta:
        model = BadWord
        fields = ['id', 'content', 'active', 'creator', 'created_at']
        extra_kwargs = {'creator': {'read_only': True}, 'id': {'read_only': True}, 'active': {'read_only': True}}

    def save(self, **kwargs):
        kwargs['creator'] = self.context.get('current_user')
        return super().save(**kwargs)


class GroupSerializer(serializers.ModelSerializer):
    creator = UserSerializer(read_only=True)
    members = UserSerializer(many=True, read_only=True)

    class Meta:
        model = Group
        fields = ['id', 'name', 'active', 'creator', 'members']
        extra_kwargs = {'id': {'read_only': True}}

    def save(self, **kwargs):
        kwargs['creator'] = self.context.get('current_user')
        return super().save(**kwargs)


class IdListSerializer(serializers.Serializer):
    ids = serializers.ListField(allow_null=False, allow_empty=False, min_length=1, max_length=10)


class MessageToGroupsSerializer(serializers.Serializer):
    ids = serializers.ListField(allow_null=False, allow_empty=False, min_length=1)
    message = serializers.CharField(max_length=255, allow_blank=False)


class SimpleGroupSerializer(serializers.ModelSerializer):
    creator = serializers.StringRelatedField()

    class Meta:
        model = Group
        fields = ['id', 'name', 'active', 'creator']
        extra_kwargs = {'id': {'read_only': True}}
