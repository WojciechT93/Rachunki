from django.shortcuts import render
from django.contrib.auth.models import User, Group
from rest_framework import viewsets
from rest_framework import permissions
from .models import Transfer, Outlay, Currency
from api.serializers import UserSerializer, GroupSerializer, TransferSerializer, OutlaySerializer, CurrencySerializer


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]


class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAuthenticated]


class CurrencyViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows currences to be viewed or edited.
    """
    queryset = Currency.objects.all()
    serializer_class = CurrencySerializer
    permission_classes = [permissions.IsAdminUser]


class OutlayViewSet(viewsets.ModelViewSet):
    queryset = Outlay.objects.all()
    serializer_class = OutlaySerializer
    permission_classes = [permissions.IsAdminUser]


class TransferViewSet(viewsets.ModelViewSet):
    queryset = Transfer.objects.all()
    serializer_class = TransferSerializer
    permission_classes = [permissions.IsAdminUser]
