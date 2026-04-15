import json
import requests
from django.db import transaction
from django.db.models import Q
from django.shortcuts import render
from rest_framework.views import Response
from rest_framework import viewsets, status
from requests import HTTPError
from .serializers import ProfileDataSerializer, ProfileListSerializer, ProfileSerializer
from .models import DELETED, Profile

# Create your views here.

class ProfileViewSet(viewsets.ViewSet):
    @transaction.atomic
    def create_profile(self, request):
        def fetch_external_api(url, api_name):
            try:
                response = requests.get(url)
                response.raise_for_status()
                return response.json()
            except HTTPError:
                return Response({
                    "status": "error",
                    "message": f"{api_name} returned an invalid response"
                }, status=status.HTTP_502_BAD_GATEWAY)
            
        serializer = ProfileSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'status': 'error',
                'message': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        validated_data = serializer.validated_data
        name: str = validated_data.get("name")
        if not name.replace(' ', '').isalpha():
            return Response({
                'status': 'error',
                'message': "'name' must only contain alphabets"
            }, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        
        profile = Profile.objects.filter(name=name).first()
        if profile:
            return Response({
                "status": "success",
                "message": "Profile already exists",
                "data": ProfileDataSerializer(profile).data
            }, status=status.HTTP_200_OK)

        # Extract gender, gender_probability, and count from Genderize. Rename count to sample_size
        gender_url = f"https://api.genderize.io?name={name}"
        gender_data = fetch_external_api(gender_url, "Genderize")
        
        gender = gender_data.get('gender')
        gender_probability = gender_data.get('probability')        
        count = gender_data.get('count')

        if count == 0 or gender == None:
            return Response({
                'status': 'error',
                'message': 'No gender prediction available for the provided name',
            }, status=status.HTTP_502_BAD_GATEWAY)

        # Extract age from Agify. Classify age_group: 0–12 → child, 13–19 → teenager, 20–59 → adult, 60+ → senior
        age_url = f"https://api.agify.io?name={name}"
        age_data = fetch_external_api(age_url, "Agify")
        
        age = age_data.get("age")
        if age == None:
            return Response({
                'status': 'error',
                'message': 'No age prediction available for the provided name',
            }, status=status.HTTP_502_BAD_GATEWAY)
        
        if 0 <= age <= 12:
            age_group = "child"
        elif 13 <= age <= 19:
            age_group = "teenager"
        elif 20 <= age <= 59:
            age_group = "adult"
        else:
            age_group = "senior"
        
        # Extract country list from Nationalize. Pick the country with the highest probability as country_id
        nationality_url = f"https://api.nationalize.io?name={name}"
        nationality_data = fetch_external_api(nationality_url, "Nationalize")
        country_data = nationality_data.get("country")
        if country_data in [[], None]:
            return Response({
                'status': 'error',
                'message': 'No nationality prediction available for the provided name',
            }, status=status.HTTP_502_BAD_GATEWAY)
        
        country_dict = max(country_data, key=lambda x: x['probability'])
        country_id = country_dict['country_id']
        country_probability = country_dict["probability"]
        sample_size = count

        create_data = {
            "name": name,
            "gender": gender,
            "gender_probability": gender_probability,
            "sample_size": sample_size,
            "age": age,
            "age_group": age_group,
            "country_id": country_id,
            "country_probability": country_probability
        }

        # Store the processed result        
        profile = Profile.objects.create(**create_data)

        return Response({
            "status": "success",
            "message": "Profile created successfully",
            "data": ProfileDataSerializer(profile).data
        }, status=status.HTTP_201_CREATED)
    
    @transaction.atomic
    def get_profile(self, request, id):
        profile = Profile.objects.filter(id=id).first()
        if not profile:
            return Response({
                "status": "error",
                "message": "Profile not found",
                "data": []
            }, status=status.HTTP_404_NOT_FOUND)
        
        return Response({
            "status": "success",
            "data": ProfileDataSerializer(profile).data
        }, status=status.HTTP_200_OK)

    @transaction.atomic
    def get_profiles(self, request):
        query_params = {k.lower(): v for k, v in request.GET.items()}
        gender = query_params.get("gender")
        country_id = query_params.get("country_id")
        age_group = query_params.get("age_group")

        profile = Profile.objects.all()

        query = Q()
        if gender:
            query &= Q(gender__iexact=gender)
        if country_id:
            query &= Q(country_id__iexact=country_id)
        if age_group:
            query &= Q(age_group__iexact=age_group)
        
        profiles = profile.filter(query)
        index_map = {}

        if profiles:
            index_map = {obj.id: idx + 1 for idx, obj in enumerate(profiles)}

        serializer = ProfileListSerializer(profiles, many=True, context={"index_map": index_map})

        return Response({
            "status": "success",
            "count": profiles.count(),
            "data": serializer.data
        }, status=status.HTTP_200_OK) 
    
    @transaction.atomic
    def delete_profile(self, request, id):
        profile = Profile.objects.filter(id=id).first()
        if not profile:
            return Response({
                "status": "error",
                "message": "Profile not found",
                "data": []
            }, status=status.HTTP_404_NOT_FOUND) 
        
        profile.status = DELETED
        profile.save()

        return Response(status=status.HTTP_204_NO_CONTENT) 