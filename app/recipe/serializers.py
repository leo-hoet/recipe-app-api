from dataclasses import fields
from rest_framework import serializers

from core.models import Tag


class TagSerializer(serializers.ModelSerializer):
    """Serializer for tags objetcs"""

    class Meta:
        model = Tag
        fields = ('id', 'name')
        read_only_fields = ('id',)