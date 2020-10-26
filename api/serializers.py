from django.contrib.auth.models import User, Group
from rest_framework import serializers
from .models import Outlay, Transfer, Currency
from rest_framework.validators import UniqueValidator


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ['url', 'password','username', 'email', 'groups']


class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password')
        extra_kwargs = {'password' : {'write_only': True}}
        
    def create(self, validated_data):
        user = User.objects.create_user(validated_data['username'],
                                        validated_data['email'], 
                                        validated_data['password'])
        return user


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