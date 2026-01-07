from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner of the object.
        return obj.user == request.user


class IsOwner(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to access it.
    """
    def has_object_permission(self, request, view, obj):
        if hasattr(obj, 'user'):
            return obj.user == request.user
        elif hasattr(obj, 'owner'):
            return obj.owner == request.user
        return False


class IsOwnerOrMember(permissions.BasePermission):
    """
    Custom permission to allow owners and members of a project to access it.
    """
    def has_object_permission(self, request, view, obj):
        # If the object has a user field
        if hasattr(obj, 'user'):
            return obj.user == request.user
        # If the object has an owner field
        elif hasattr(obj, 'owner'):
            return obj.owner == request.user
        # If the object has a project field (like tasks)
        elif hasattr(obj, 'project'):
            return obj.project.owner == request.user or request.user in obj.project.members.all()
        return False


class IsSameUser(permissions.BasePermission):
    """
    Custom permission to only allow users to access their own data.
    """
    def has_object_permission(self, request, view, obj):
        if hasattr(obj, 'id'):
            return obj.id == request.user.id
        return False


class IsOwnerAccount(permissions.BasePermission):
    """
    Custom permission to only allow owners to perform certain actions.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_owner