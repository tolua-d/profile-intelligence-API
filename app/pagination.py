"""
Pagination helper for API responses with versioning support
"""
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class PaginationHelper(PageNumberPagination):
    """
    Custom pagination class that returns a standardized response shape
    Supporting API versioning
    """
    page_size = 10
    page_size_query_param = 'limit'
    max_page_size = 50
    page_query_param = 'page'
    
    def paginate_queryset(self, queryset, request, view=None):
        """Paginate queryset and store pagination info"""
        self.request = request
        return super().paginate_queryset(queryset, request, view)
    
    def get_paginated_response(self, data):
        """Return paginated response with standardized shape"""
        return Response({
            'status': 'success',
            'pagination': {
                'page': self.page.number,
                'limit': self.page_size,
                'total': self.page.paginator.count,
                'pages': self.page.paginator.num_pages,
            },
            'data': data
        })


class PaginationHelperV2(PageNumberPagination):
    """
    API v2 pagination with enhanced metadata
    """
    page_size = 10
    page_size_query_param = 'limit'
    max_page_size = 50
    page_query_param = 'page'
    
    def paginate_queryset(self, queryset, request, view=None):
        """Paginate queryset and store pagination info"""
        self.request = request
        return super().paginate_queryset(queryset, request, view)
    
    def get_paginated_response(self, data):
        """Return paginated response with v2 shape including additional metadata"""
        return Response({
            'status': 'success',
            'version': 'v2',
            'pagination': {
                'page': self.page.number,
                'limit': self.page_size,
                'total': self.page.paginator.count,
                'pages': self.page.paginator.num_pages,
                'has_next': self.page.has_next(),
                'has_previous': self.page.has_previous(),
            },
            'data': data
        })
