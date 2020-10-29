from django.shortcuts import render
from django.contrib.auth.models import User, Group
from django.http import Http404
from django.core import exceptions
from rest_framework import viewsets, status, generics
from rest_framework.permissions import IsAuthenticated, IsAdminUser, IsAuthenticatedOrReadOnly
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from .models import Transfer, Outlay, Currency
from api.serializers import UserSerializer, GroupSerializer, TransferSerializer, OutlaySerializer, CurrencySerializer, RegisterSerializer
from api.permissions import CurrencyDetailAllowedMethods, CurrencyListAlloweMethods, OutlaysListAllowedMethods


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]

class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [IsAdminUser]

class RegisterViewSet(viewsets.ModelViewSet):
    serializer_class = RegisterSerializer
    queryset = User.objects.all()

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        if user:
            return Response({"user": UserSerializer(user, context=self.get_serializer_context()).data})

class CurrencyListView(generics.ListCreateAPIView):
    serializer_class = CurrencySerializer
    queryset = Currency.objects.all()
    permission_classes = [CurrencyListAlloweMethods]

class CurrencyDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Currency.objects.all()
    serializer_class = CurrencySerializer
    lookup_field = 'currency_name'
    permission_classes = [CurrencyDetailAllowedMethods]

class OutlaysListView(generics.ListCreateAPIView):
    queryset = Outlay.objects.all()
    serializer_class = OutlaySerializer
    lookup_field = 'id'
    permission_classes = [OutlaysListAllowedMethods, IsAuthenticated]
    def get_queryset(self):
        if self.request.user.is_superuser:
            return Outlay.objects.all()
        return Outlay.objects.filter(owner=self.request.user)


class OutlayDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Outlay.objects.all()
    serializer_class = OutlaySerializer
    lookup_field = 'id'
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        if self.request.user.is_superuser:
            return Outlay.objects.all()
        return Outlay.objects.filter(owner=self.request.user)
    

class TransfersListView(generics.ListCreateAPIView):
    queryset = Transfer.objects.all()
    serializer_class = TransferSerializer
    lookup_field = 'id'
    template_name = 'transfers'

    def get_queryset(self):
        if self.request.user.is_superuser:
            return Transfer.objects.all()
        return Transfer.objects.filter(owner=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

class TransferDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Transfer.objects.all()
    serializer_class = TransferSerializer
    lookup_field = 'id'
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_superuser:
            return Transfer.objects.all()
        return Transfer.objects.filter(owner=self.request.user)
    
    
    
    



