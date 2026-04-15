import requests
from django.shortcuts import render
from rest_framework.views import Response
from rest_framework import viewsets

# Create your views here.

class Profile(viewsets.ViewSet):
    def create_profile(self, request):
        pass