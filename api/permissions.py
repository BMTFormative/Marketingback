from rest_framework import permissions

class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object or admins to edit it.
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Check if the user is admin/staff
        if request.user.is_staff:
            return True
            
        # For user objects, check if the user is trying to modify themselves
        if hasattr(obj, 'id') and hasattr(request.user, 'id') and obj.id == request.user.id:
            return True
        
        # For objects with a user field, check if user is the owner
        if hasattr(obj, 'user'):
            return obj.user == request.user
            
        return False