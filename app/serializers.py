from rest_framework import serializers
from .models import Profile

class ProfileSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255)

class ProfileDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        exclude = ("status",)
    
class ProfileListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ("id", "name", "gender", "age", "age_group", "country_id")

