from django.utils.deprecation import MiddlewareMixin
from .models import ActivityLog
from django.contrib.contenttypes.models import ContentType
import json


class ActivityLogMiddleware(MiddlewareMixin):
    def process_response(self, request, response):
        if request.user.is_authenticated and hasattr(request, 'resolver_match'):
            # Log the activity based on the request method and view
            if request.resolver_match:
                view_name = request.resolver_match.view_name
                method = request.method
                
                # Determine the action based on HTTP method
                if method == 'POST':
                    action = ActivityLog.Action.CREATED
                elif method == 'PUT' or method == 'PATCH':
                    action = ActivityLog.Action.UPDATED
                elif method == 'DELETE':
                    action = ActivityLog.Action.DELETED
                else:
                    # For other methods, we might not want to log
                    return response
                
                # Skip logging for auth endpoints to prevent recursion
                if view_name and any(skip in view_name for skip in ['login', 'register', 'logout', 'token']):
                    return response
                
                # Create activity log entry
                try:
                    ActivityLog.objects.create(
                        user=request.user,
                        action=action,
                        target_type=ContentType.objects.get(app_label='auth', model='user'),
                        target_id=request.user.id,
                        description=f"User performed {method} on {view_name}",
                        ip_address=self.get_client_ip(request),
                        user_agent=request.META.get('HTTP_USER_AGENT', '')
                    )
                except Exception:
                    # Fail silently to avoid breaking the request
                    pass
        
        return response

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip