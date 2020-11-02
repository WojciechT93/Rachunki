from rest_framework.permissions import BasePermission

class CurrencyDetailAllowedMethods(BasePermission):
    user_methods = ['GET', 'PUT', 'PATCH']

    def has_permission(self, request, view):
        if (request.method in self.user_methods and 
                request.user.is_authenticated):
            return True
        return False

class CurrencyListAlloweMethods(BasePermission):
    user_methods = ['GET']

    def has_permission(self, request, view):
        if request.method in self.user_methods or request.user.is_superuser:
            return True
        return False

class OutlaysListAllowedMethods(BasePermission):
    user_methods = ['GET']

    def has_permission(self, request, view):
        if request.method in self.user_methods or request.user.is_superuser:
            return True
        return False

