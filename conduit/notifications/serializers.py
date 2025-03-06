from rest_framework import serializers
from share.models import Share


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Share
        fields = "__all__"
