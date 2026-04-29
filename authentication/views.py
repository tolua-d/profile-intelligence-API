from django.shortcuts import render
import requests
import logging
from datetime import datetime
from django.contrib.auth import authenticate
from django.contrib.auth.models import update_last_login
from django.db import transaction
from django.db.models import Q
from django.shortcuts import render, redirect
from rest_framework.views import Response
from rest_framework import viewsets, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from requests import HTTPError
from rest_framework_simplejwt.tokens import RefreshToken

from utils import exchange_code_for_token, generate_code_challenge, get_github_user
from .serializers import LoginUserSerializer, SignUserUpSerializer, UserSerializer
from .models import User, RefreshTokenBlacklist
from config.settings import GITHUB_CLIENT_ID, GITHUB_CLIENT_SECRET, FRONTEND_URL, GITHUB_REDIRECT_URI

logger = logging.getLogger(__name__)


class AuthViewSet(viewsets.ViewSet):
    """Authentication ViewSet for GitHub OAuth and token management"""

    def get_permissions(self):
        """Apply per-action auth rules instead of global IsAuthenticated."""
        public_actions = {"github_login", "github_callback", "github_cli_token", "refresh_token"}
        if getattr(self, "action", None) in public_actions:
            return [AllowAny()]
        return [IsAuthenticated()]
    
    @transaction.atomic
    def github_login(self, request):
        """Initiate GitHub OAuth login flow"""
        try:
            verifier, code_challenge = generate_code_challenge()
            github_url = "https://github.com/login/oauth"
            
            request.session['code_verifier'] = verifier
            
            url = (
                f"{github_url}/authorize?"
                f"client_id={GITHUB_CLIENT_ID}"
                f"&redirect_uri={GITHUB_REDIRECT_URI}"
                f"&scope=user"
                f"&code_challenge={code_challenge}"
                f"&code_challenge_method=S256"
            )
            
            logger.info(f"GitHub OAuth login initiated")
            return redirect(url)
        except Exception as e:
            logger.error(f"GitHub login error: {str(e)}")
            return Response({"error": "Authentication failed"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @transaction.atomic
    def github_callback(self, request):
        """Handle GitHub OAuth callback"""
        try:
            code = request.GET.get("code")
            code_verifier = request.session.get("code_verifier")

            if not code or not code_verifier:
                logger.warning("GitHub callback: Missing code or verifier")
                return Response({"error": "Invalid request"}, status=status.HTTP_400_BAD_REQUEST)
            
            token_data = exchange_code_for_token(code, code_verifier)
            github_access_token = token_data.get("access_token")

            if not github_access_token:
                logger.warning("GitHub callback: No access token received")
                return Response({"error": "GitHub auth failed"}, status=status.HTTP_400_BAD_REQUEST)
            
            # Fetch GitHub user data
            github_user = get_github_user(github_access_token)
            
            # Create or get user
            user, created = User.objects.get_or_create(
                github_id=github_user["id"],
                defaults={
                    "email": github_user.get("email") or f"{github_user['login']}@github.local",
                    "username": github_user["login"],
                    "github_username": github_user["login"],
                    "is_verified": True,
                    "is_active": True,
                }
            )
            
            # Update user info if not new
            if not created:
                user.username = github_user["login"]
                user.github_username = github_user["login"]
                user.is_active = True
                user.last_login_at = datetime.now()
                user.save()
            
            # Issue JWT tokens
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            
            logger.info(f"User {user.email} authenticated via GitHub")
            
            # Create response with redirect
            response = redirect(FRONTEND_URL + "/dashboard")
            
            # Set HTTP-only cookies
            response.set_cookie(
                key="access_token",
                value=access_token,
                httponly=True,
                secure=True,
                samesite="Lax",
                max_age=600  # 10 minutes
            )
            
            response.set_cookie(
                key="refresh_token",
                value=str(refresh),
                httponly=True,
                secure=True,
                samesite="Lax",
                max_age=604800  # 7 days
            )
            
            return response
        except Exception as e:
            logger.error(f"GitHub callback error: {str(e)}")
            return Response({"error": "Authentication failed"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @transaction.atomic
    def github_cli_token(self, request):
        """Get tokens for CLI authentication"""
        try:
            code = request.data.get("code")
            code_verifier = request.data.get("code_verifier")

            if not code or not code_verifier:
                logger.warning("CLI token: Missing code or verifier")
                return Response({"error": "Missing fields"}, status=status.HTTP_400_BAD_REQUEST)

            token_data = exchange_code_for_token(code, code_verifier)
            github_access_token = token_data.get("access_token")

            if not github_access_token:
                logger.warning("CLI token: No GitHub access token")
                return Response({"error": "GitHub auth failed"}, status=status.HTTP_400_BAD_REQUEST)

            # Fetch GitHub user
            github_user = get_github_user(github_access_token)

            # Create or get user
            user, created = User.objects.get_or_create(
                github_id=github_user["id"],
                defaults={
                    "email": github_user.get("email") or f"{github_user['login']}@github.local",
                    "username": github_user["login"],
                    "github_username": github_user["login"],
                    "is_verified": True,
                    "is_active": True,
                }
            )
            
            if not created:
                user.last_login_at = datetime.now()
                user.save()
            
            # Issue tokens
            refresh = RefreshToken.for_user(user)

            logger.info(f"CLI tokens issued for user {user.email}")

            return Response({
                "status": "success",
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "user": {
                    "id": str(user.id),
                    "email": user.email,
                    "username": user.username,
                    "role": user.role
                }
            }, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"CLI token error: {str(e)}")
            return Response({"error": "Authentication failed"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @transaction.atomic
    def refresh_token(self, request):
        """Refresh access token using refresh token"""
        try:
            refresh_token_str = request.data.get("refresh") or request.COOKIES.get("refresh_token")
            
            if not refresh_token_str:
                logger.warning("Refresh token: No refresh token provided")
                return Response(
                    {"error": "Refresh token required"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Check if token is blacklisted
            blacklisted = RefreshTokenBlacklist.objects.filter(token=refresh_token_str).exists()
            if blacklisted:
                logger.warning("Refresh token: Token is blacklisted")
                return Response(
                    {"error": "Token has been revoked"},
                    status=status.HTTP_401_UNAUTHORIZED
                )
            
            # Create new refresh token
            try:
                refresh = RefreshToken(refresh_token_str)
                new_access = str(refresh.access_token)
                new_refresh = str(refresh)
                
                logger.info(f"Token refreshed successfully")
                
                response = Response({
                    "status": "success",
                    "access": new_access,
                    "refresh": new_refresh
                }, status=status.HTTP_200_OK)
                
                # Set new cookies if from web
                if "refresh_token" in request.COOKIES:
                    response.set_cookie(
                        key="access_token",
                        value=new_access,
                        httponly=True,
                        secure=True,
                        samesite="Lax",
                        max_age=600
                    )
                    response.set_cookie(
                        key="refresh_token",
                        value=new_refresh,
                        httponly=True,
                        secure=True,
                        samesite="Lax",
                        max_age=604800
                    ) 
                
                return response
            except Exception as e:
                logger.error(f"Refresh token validation failed: {str(e)}")
                return Response(
                    {"error": "Invalid refresh token"},
                    status=status.HTTP_401_UNAUTHORIZED
                )
        except Exception as e:
            logger.error(f"Token refresh error: {str(e)}")
            return Response(
                {"error": "Token refresh failed"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @transaction.atomic
    def logout(self, request):
        """Logout user and invalidate tokens"""
        try:
            refresh_token_str = request.data.get("refresh") or request.COOKIES.get("refresh_token")
            
            if refresh_token_str and request.user.is_authenticated:
                # Add to blacklist
                from datetime import timedelta
                from rest_framework_simplejwt.settings import api_settings
                expires_at = datetime.now() + timedelta(seconds=api_settings.REFRESH_TOKEN_LIFETIME.total_seconds())
                
                RefreshTokenBlacklist.objects.create(
                    token=refresh_token_str,
                    user=request.user,
                    expires_at=expires_at
                )
            
            logger.info(f"User {request.user.email if request.user.is_authenticated else 'unknown'} logged out")
            
            response = Response({
                "status": "success",
                "message": "Logged out successfully"
            }, status=status.HTTP_200_OK)
            
            # Clear cookies
            response.delete_cookie('access_token')
            response.delete_cookie('refresh_token')
            
            return response
        except Exception as e:
            logger.error(f"Logout error: {str(e)}")
            return Response(
                {"error": "Logout failed"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @transaction.atomic
    def me(self, request):
        """Get current user info"""
        if not request.user or not request.user.is_authenticated:
            return Response(
                {"error": "Unauthorized"},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        return Response({
            "status": "success",
            "data": UserSerializer(request.user).data
        }, status=status.HTTP_200_OK)
