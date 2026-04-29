import csv
import json
import logging
import re
from django.http import HttpResponse
import requests
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Q
from django.shortcuts import render
from rest_framework.views import Response
from rest_framework import viewsets, status
from requests import HTTPError
from rest_framework.permissions import IsAuthenticated, AllowAny
from .serializers import ProfileDataSerializer, ProfileSerializer
from .models import DELETED, Profile
from authentication.permissions import IsAnalystOrReadOnly, IsAnalyst, IsAdminOrAnalyst

logger = logging.getLogger(__name__)

# Create your views here.

class ProfileViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated, IsAnalystOrReadOnly]
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
            # "sample_size": sample_size,
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
        query_params = {k.lower().strip(): v for k, v in request.GET.items()}
        page = query_params.get("page", 1)
        limit = query_params.get("limit", 10)
        gender = query_params.get("gender")
        country_id = query_params.get("country_id")
        age_group = query_params.get("age_group")
        min_age = query_params.get('min_age')
        max_age = query_params.get("max_age")
        min_gender_probability = query_params.get('min_gender_probability')
        min_country_probability = query_params.get("min_country_probability")

        if age_group and age_group.lower() not in ["child", "teenager", "adult", "senior"]:
            return Response({
                "status": "error",
                "message": "age group options include: child, teenager, adult, senior"
            }, status=status.HTTP_400_BAD_REQUEST) 

        sort_by = query_params.get("sort_by")
        sort_by_options = ["age", "created_at", "gender_probability"]
        if sort_by and sort_by not in sort_by_options:
            return Response({
                "status": "error",
                "message": "sort-by options include: age, created_at, gender_probability"
            }, status=status.HTTP_400_BAD_REQUEST) 
        
        order_by = query_params.get("order_by")
        order_by_options = ["asc", "desc"]
        if order_by and order_by not in order_by_options:
            return Response({
                "status": "error",
                "message": "order-by options include: asc, desc"
            }, status=status.HTTP_400_BAD_REQUEST) 
        if order_by and order_by == "desc":
            sort_by = f"-{sort_by}"


        profile = Profile.objects.all()

        query = Q()
        if gender:
            query &= Q(gender__iexact=gender)
        if country_id:
            query &= Q(country_id__iexact=country_id)
        if age_group:
            query &= Q(age_group__iexact=age_group)
        if min_age:
            query &= Q(age__gte=int(min_age))
        if max_age:
            query &= Q(age__lte=int(max_age))
        if min_gender_probability:
            query &= Q(gender_probability__gte=float(min_gender_probability))
        if min_country_probability:
            query &= Q(country_probability__gte=float(min_country_probability))
        
        profiles = profile.filter(query)
        if int(limit) > 50:
            limit = 50
        if sort_by:
            profiles = profiles.order_by(sort_by)

        serializer = ProfileDataSerializer(profiles, many=True)

        paginator = Paginator(serializer.data, limit)
        page_obj  = paginator.get_page(page)

        return Response({
            "status": "success",
            "page": page,
            "limit": limit,
            "total": paginator.count,
            "data": page_obj.object_list
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
    
    @transaction.atomic
    def get_profiles_with_search_logic(self, request):
        try:
            query_params = {k.lower().strip(): v for k, v in request.GET.items()}
            search_logic: str = query_params.get("q")
            page = query_params.get("page", 1)
            limit = int(query_params.get("limit", 10))
            allowed_patterns = re.compile(r"^[a-zA-Z0-9\s]+$")
            query_is_safe = bool(allowed_patterns.match(search_logic.strip()))

            if not search_logic or not query_is_safe:
                return Response({
                    "status": "error",
                    "message": "Invalid query parameters"
                }, status=status.HTTP_422_UNPROCESSABLE_ENTITY) 
            
            # have a map of words that i can use to create core rules
            GENDER_MAP = {
                "female": "female",
                "females": "female",
                "women": "female",
                "woman": "female",
                "male": "male",
                "males": "male",
                "men": "male",
                "man": "male"
            }

            AGE_GROUP_MAP = {
                "child": (0, 12),
                "children": (0, 12),
                "young": (16, 24),
                "teenager": (13, 19),
                "teenagers": (13, 19),
                "adult": (20, 59),
                "adults": (20, 59),
                "senior": (60, 150),
                "seniors": (60, 150),   
            }

            # split search query
            logic_words = search_logic.lower().split()
            query = Q()
            i = 0
            matched = False

            # compare search logic with the list and filter queryset
            while i < len(logic_words):
                word = logic_words[i]
                if word in GENDER_MAP:
                    if logic_words[i + 1] == "and" and logic_words[i + 2] in GENDER_MAP:
                        query &= Q(gender=GENDER_MAP.get(word)) | Q(gender=GENDER_MAP.get(logic_words[i+2]))
                        matched = True
                        i += 3
                    else:
                        query &= Q(gender=GENDER_MAP.get(word))
                        i += 1
                    continue
                if word in AGE_GROUP_MAP:
                    min_age, max_age = AGE_GROUP_MAP.get(word)
                    query &= Q(age__gte=min_age) & Q(age__lte=max_age)
                    matched = True
                    i += 1
                    continue
                if word in ["above", "older", "over"]:
                    query &= Q(age__gt=logic_words[i+1])
                    matched = True
                    i += 1
                    continue
                if word in ["below", "younger", "under"]:
                    query &= Q(age__lt=logic_words[i+1])
                    matched = True
                    i += 1
                    continue
                if word == "from":
                    # handles country and age range
                    if i + 3 < len(logic_words) and logic_words[i + 2] == "to":
                        query &= Q(age__gte=logic_words[i+1]) & Q(age__lte=logic_words[i+3])
                        matched = True
                    # handles country
                    else:
                        with open("countries.json", "r") as file:
                            country_data = json.load(file)
                        #  handles multiple word country eg south africa
                        for size in [3, 2, 1]:
                            country = " ".join(logic_words[i+1:i+1+size]).title()
                            if country in country_data:
                                country_id = country_data.get(country)
                                query &= Q(country_id=country_id)
                                matched = True
                i += 1
        
            if not matched:
                return Response({
                    "status": "error",
                    "message": "Unable to interpret query"
                }, status=status.HTTP_400_BAD_REQUEST) 

            profiles = Profile.objects.filter(query)

            if not profiles:
                return Response({
                    "status": "error",
                    "message": "Profile not found"
                }, status=status.HTTP_404_NOT_FOUND) 
            
            if limit > 50:
                limit = 50

            serializer = ProfileDataSerializer(profiles, many=True)

            paginator = Paginator(serializer.data, limit)
            page_obj  = paginator.get_page(page)

            return Response({
                "status": "success",
                "page": page,
                "limit": limit,
                "total": paginator.count,
                "data": page_obj.object_list
            }, status=status.HTTP_200_OK) 
        except Exception:
            return Response({
                "status": "error",
                "message": "Server failure"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR) 
    
    @transaction.atomic
    def export_profiles(self, request):
        """Export profiles as CSV (requires analyst role)"""
        if request.user.role not in ["admin", "analyst"]:
            return Response({
                "error": "Analyst role required for exports"
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Get all profiles with filters
        profiles = Profile.objects.all().order_by('-created_at')
        
        # Apply filters if provided
        gender = request.GET.get("gender")
        age_group = request.GET.get("age_group")
        country_id = request.GET.get("country_id")
        
        filters = Q()
        if gender:
            filters &= Q(gender=gender.lower())
        if age_group:
            filters &= Q(age_group=age_group.lower())
        if country_id:
            filters &= Q(country_id=country_id.upper())
        
        profiles = profiles.filter(filters)
        
        # Create CSV response
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="profiles_export.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'ID', 'Name', 'Gender', 'Gender Probability', 'Age', 'Age Group',
            'Country ID', 'Country Name', 'Country Probability', 'Created At'
        ])
        
        for profile in profiles:
            writer.writerow([
                profile.id,
                profile.name,
                profile.gender,
                profile.gender_probability,
                profile.age,
                profile.age_group,
                profile.country_id,
                profile.country_name,
                profile.country_probability,
                profile.created_at.isoformat()
            ])
        
        logger.info(f"Profiles exported: {profiles.count()} records by user {request.user.email}")
        
        return response
    
class HealthCheck(viewsets.ViewSet):
    permission_classes = [AllowAny]
    @transaction.atomic
    def health_check(self, request):
        return Response({
            'status': 200,
            'message': 'ok'
        }, status=status.HTTP_200_OK)