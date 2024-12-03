from rest_framework import serializers
from .models import Part, AircraftModel

class PartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Part
        fields = ['__all__']

class AircraftModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = AircraftModel
        fields = ['id', 'name']
