from django.urls import path
from authentication import views

app_name = 'authentication'

urlpatterns = [
    # GitHub OAuth
    path("github/login/", views.AuthViewSet.as_view({
        "get": "github_login"
    }), name="github-login"),
    
    path("github/callback/", views.AuthViewSet.as_view({
        "get": "github_callback"
    }), name="github-callback"),
    
    path("github/token/", views.AuthViewSet.as_view({
        "post": "github_cli_token"
    }), name="github-cli-token"),
    
    # Token management
    path("token/refresh/", views.AuthViewSet.as_view({
        "post": "refresh_token"
    }), name="token-refresh"),
    
    path("logout/", views.AuthViewSet.as_view({
        "post": "logout"
    }), name="logout"),
    
    # User info
    path("me/", views.AuthViewSet.as_view({
        "get": "me"
    }), name="user-me"),
]
