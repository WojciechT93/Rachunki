from django.shortcuts import render
from django.contrib.auth.models import User, Group
from django.http import Http404
from django.core import exceptions
from django.db.models import Avg, Sum
from rest_framework import viewsets, status, generics
from rest_framework.permissions import (
    IsAuthenticated, IsAdminUser, IsAuthenticatedOrReadOnly
)
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authentication import (
    SessionAuthentication, BasicAuthentication
)
from .models import Transfer, Outlay, Currency
from api.serializers import (
    UserSerializer, GroupSerializer, TransferSerializer, OutlaySerializer,CurrencySerializer, RegisterSerializer
)
from api.permissions import (
    CurrencyDetailAllowedMethods, CurrencyListAlloweMethods, OutlaysListAllowedMethods
)
import json

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
            res = {"user": UserSerializer(user, context=self.get_serializer_context()).data}
            return Response(res)

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
    permission_classes = [IsAuthenticated]

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

class StatiscticsListView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, format=None):
        sum_settled_name = 'Suma wszystkich wydatków rozliczonych'
        sum_unsettled_name = ('Suma wszystkich wydatków nierozliczonych ' 
                              'w walucie “USD”')
        avg_vat_name = 'Średnia wartość przelewu VAT w miesiącu Wrzesień 2020'

        if request.user.is_superuser:
            sum_unsettled_USD = Outlay.objects.filter(is_settled=False
                                             ).filter(currency='USD'
                                             ).aggregate(Sum('to_settle'))
            avg_vat = Transfer.objects.filter(is_vat=True
                                     ).filter(settled_date__year__gte=2020
                                     ).filter(settled_date__month__gte=10
                                     ).aggregate(Avg('brutto'))
            sum_settled = Outlay.objects.filter(is_settled=True
                                       ).aggregate(Sum('settled'))
        else:
            sum_unsettled_USD = Outlay.objects.filter(owner=self.request.user
                                             ).filter(is_settled=False
                                             ).filter(currency='USD'
                                             ).aggregate(Sum('to_settle'))
            avg_vat = Transfer.objects.filter(owner=self.request.user
                                     ).filter(is_vat=True
                                     ).filter(settled_date__year__gte=2020
                                     ).filter(settled_date__month__gte=10
                                     ).aggregate(Avg('brutto'))
            sum_settled = Outlay.objects.filter(owner=self.request.user
                                       ).filter(is_settled=True
                                       ).aggregate(Sum('settled'))
        
        data = (
            {sum_settled_name:sum_settled['settled__sum']},   
            {sum_unsettled_name:sum_unsettled_USD['to_settle__sum']},
            {avg_vat_name:avg_vat['brutto__avg']}
        )
        return Response(data=data, status=status.HTTP_200_OK)
    

    
    
    
    



