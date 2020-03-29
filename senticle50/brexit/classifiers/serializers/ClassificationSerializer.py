from rest_framework import serializers


class ClassificationSerializer(serializers.Serializer):
    name = serializers.CharField()
    value = serializers.DecimalField(max_digits=20, decimal_places=0)