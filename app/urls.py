from django.urls import path
from app import views

urlpatterns = [
    path('profiles', views.ProfileViewSet.as_view({
        'post': 'create_profile',
        'get': 'get_profiles'
    })),
    path('profiles/<id>', views.ProfileViewSet.as_view({
        'get': 'get_profile',
        'delete': 'delete_profile'
    }))
]