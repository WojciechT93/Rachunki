from django.contrib.auth.models import User, Group
from rest_framework import serializers
from .models import Outlay, Transfer, Currency


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ['url', 'username', 'email', 'groups']


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ['url', 'name']


class OutlaySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Outlay
        fields = '__all__'


class TransferSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Transfer
        fields = '__all__'


class CurrencySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Currency
        fields = '__all__'