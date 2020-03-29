from rest_framework import serializers
from .ClassificationSerializer import ClassificationSerializer


class ClassifiedDaySerializer(serializers.Serializer):
    date = serializers.DateField()
    classifications = ClassificationSerializer(many=True)