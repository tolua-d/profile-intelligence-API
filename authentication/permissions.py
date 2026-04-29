"""
Role-based access control (RBAC) permissions and decorators
"""
from functools import wraps
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.permissions import SAFE_METHODS


class IsAuthenticated(permissions.BasePermission):
    """Allow access only to authenticated users"""
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)


class IsAdmin(permissions.BasePermission):
    """Allow access only to admin users"""
    def has_permission(self, request, view):
        return bool(
            request.user and 
            request.user.is_authenticated and 
            request.user.role == "admin"
        )


class IsAnalyst(permissions.BasePermission):
    """Allow access only to analyst users"""
    def has_permission(self, request, view):
        return bool(
            request.user and 
            request.user.is_authenticated and 
            request.user.role == "analyst"
        )


class IsAdminOrAnalyst(permissions.BasePermission):
    """Allow access to both admin and analyst users"""
    def has_permission(self, request, view):
        return bool(
            request.user and 
            request.user.is_authenticated and 
            request.user.role in ["admin", "analyst"]
        )


class IsAnalystOrReadOnly(permissions.BasePermission):
    """
    Allows read access to authenticated users,
    write access only to analysts and admins
    """
    message = "Only analyst and admin users can perform this action."
    
    def has_permission(self, request, view):
        # Allow read access to all authenticated users
        if request.method in SAFE_METHODS:
            return bool(request.user and request.user.is_authenticated)
        
        # Allow write access to analyst and admin users
        return bool(
            request.user and 
            request.user.is_authenticated and 
            request.user.role in ["admin", "analyst"]
        )


def require_role(required_role):
    """
    Decorator to enforce role-based access control on views
    Usage:
        @require_role('admin')
        def my_view(request):
            ...
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user or not request.user.is_authenticated:
                return Response(
                    {"error": "Unauthorized"},
                    status=status.HTTP_401_UNAUTHORIZED
                )
            
            if isinstance(required_role, str):
                allowed_roles = [required_role]
            else:
                allowed_roles = required_role
            
            if request.user.role not in allowed_roles:
                return Response(
                    {"error": f"Access denied. Required role(s): {', '.join(allowed_roles)}"},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def require_admin(view_func):
    """Decorator to require admin role"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user or not request.user.is_authenticated:
            return Response(
                {"error": "Unauthorized"},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        if request.user.role != "admin":
            return Response(
                {"error": "Access denied. Admin role required."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        return view_func(request, *args, **kwargs)
    return wrapper


def require_analyst(view_func):
    """Decorator to require analyst role"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user or not request.user.is_authenticated:
            return Response(
                {"error": "Unauthorized"},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        if request.user.role not in ["admin", "analyst"]:
            return Response(
                {"error": "Access denied. Analyst role required."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        return view_func(request, *args, **kwargs)
    return wrapper
