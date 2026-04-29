from django.urls import path
from app import views

urlpatterns = [
    path('profiles', views.ProfileViewSet.as_view({
        'post': 'create_profile',
        'get': 'get_profiles'
    })),
    path("profiles/search", views.ProfileViewSet.as_view({
        "get": "get_profiles_with_search_logic"
    })),
    path('profiles/<id>', views.ProfileViewSet.as_view({
        'get': 'get_profile',
        'delete': 'delete_profile'
    })),
    path('profiles/export/csv', views.ProfileViewSet.as_view({
        'get': 'export_profiles'
    }), name='profile-export-csv'),
    path("health", views.HealthCheck.as_view({
        "get": "health_check"
    }))
]