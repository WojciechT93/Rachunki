"""
This module provides sets of permissions for api Views.
Based on user status (authenticated, superuser, anynomous)
gives permissions for views methods.
"""

from rest_framework.permissions import BasePermission


class CurrencyDetailAllowedMethods(BasePermission):
    """
    Works with CurrencyDetailView.
    Gives GET, PUT and PATCH permissions for logged user.
    Admin gets permissions for all actions.
    Unauthorized user gets nothing.
    """
    user_methods = ['GET', 'PUT', 'PATCH']

    def has_permission(self, request, view):
        if ((request.method in self.user_methods and
                request.user.is_authenticated) or
                request.user.is_superuser):
            return True
        return False

class CurrencyListAllowedMethods(BasePermission):
    """
    Works with CurrencyListView.
    Gives only GET permissions for every user, but admin.
    Admin gets permissions for all actions.
    """
    user_methods = ['GET']

    def has_permission(self, request, view):
        if request.method in self.user_methods or request.user.is_superuser:
            return True
        return False

class ExpensesListAllowedMethods(BasePermission):
    """
    Works with ExpensesListView.
    Gives only GET permissions for authorized user.
    Admin Gets permissions for all actions.
    """
    user_methods = ['GET']

    def has_permission(self, request, view):
        if request.method in self.user_methods or request.user.is_superuser:
            return True
        return False

class TransferDetailViewAllowedMethods(BasePermission):
    """
    Works with TransferDetialView.
    Gives only GET and DELETE permissions for autheticated user.
    """
    user_methods = ['GET', 'DELETE']

    def has_permission(self, request,view):
        if ((request.method in self.user_methods and
                request.user.is_authenticated) or
                request.user.is_superuser):
            return True
        return False
