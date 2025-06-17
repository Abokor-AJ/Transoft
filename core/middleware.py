from django.contrib.auth.models import User
from .models import UserProfile
from django.utils.deprecation import MiddlewareMixin

class UserProfileMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            try:
                request.user_profile = request.user.profile
            except UserProfile.DoesNotExist:
                # Create profile if it doesn't exist
                request.user_profile = UserProfile.objects.create(
                    user=request.user,
                    user_type=UserProfile.UserType.END_CUSTOMER_ADMIN
                )
        else:
            request.user_profile = None

        response = self.get_response(request)
        return response 

class DataScopeMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.user.is_authenticated:
            try:
                request.user_profile = UserProfile.objects.get(user=request.user)
            except UserProfile.DoesNotExist:
                request.user_profile = None
        else:
            request.user_profile = None

    def process_view(self, request, view_func, view_args, view_kwargs):
        # Add request to model for scoped queries
        from django.db import models
        models.Model._request = request 