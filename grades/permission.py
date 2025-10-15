from rest_framework import permissions

class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Allow only admins to create, update, or delete.
    Students can only read (GET).
    """

    def has_permission(self, request, view):
        # SAFE_METHODS = ['GET', 'HEAD', 'OPTIONS']
        if request.method in permissions.SAFE_METHODS:
            return True
        # Only admin users can create, update, or delete
        return request.user and request.user.is_authenticated and request.user.is_admin
