"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # API v1 endpoints (legacy, will be maintained)
    path('api/v1/', include('app.urls')),
    
    # API v2 endpoints (current version)
    path('api/v2/', include(('app.urls', 'app'), namespace='v2')),
    
    # Authentication endpoints
    path('auth/', include('authentication.urls')),
]

