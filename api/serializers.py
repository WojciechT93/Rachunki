from django.contrib.auth.models import User, Group
from rest_framework import serializers
from .models import Outlay, Transfer, Currency
from rest_framework.validators import UniqueValidator
from datetime import datetime


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ['url','username', 'email', 'groups']


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



class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ['url', 'name']



class OutlaySerializer(serializers.ModelSerializer):
    class Meta:
        model = Outlay
        fields = '__all__'



class TransferSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transfer
        fields = ['netto', 'vat', 'currency', 'outlay', 'is_vat']

    def create(self, validated_data):
        validated_data['brutto'] = validated_data['netto'] + validated_data['vat']
        self.check_and_update_outlay(validated_data['outlay'].id, 
                                    validated_data['brutto'], 
                                    validated_data['owner'].id,
                                    validated_data['is_vat'],
                                    validated_data['currency'])
        validated_data['settled_date'] = datetime.now()
        return Transfer.objects.create(**validated_data)
    
    def check_and_update_outlay(self, outlay_id, brutto, transfer_owner, is_vat, currency):
        outlay = Outlay.objects.get(id = outlay_id)
        if outlay:
            self.check_if_user_is_owner(outlay.owner_id, transfer_owner)
            self.check_if_outlay_vat(outlay.vat, is_vat)
            self.check_if_is_settled(outlay.is_settled)
            self.check_if_same_currency(outlay.currency, currency)
            outlay.settled += brutto 
            outlay.save()
        else:
            raise serializers.ValidationError("There is no outlay for this transfer.")
    
    def check_if_user_is_owner(self, outlay_owner, transfer_owner):
        if outlay_owner != transfer_owner:
            raise serializers.ValidationError("User is not owner of outlay")

    def check_if_is_settled(self, outlay_is_settled):
        if outlay_is_settled:
            return serializers.ValidationError("This outlay is settled.")

    def check_if_outlay_vat(self, outlay_is_vat, transfer_is_vat):
        if transfer_is_vat == True and outlay_is_vat == False:
            raise serializers.ValidationError("Vat transfer can't be done on this non-vat outlay")

    def check_if_same_currency(self, outlay_currency, transfer_currency):
        if outlay_currency != transfer_currency:
            raise serializers.ValidationError("Outlay is in different currency then transfer.")



class CurrencySerializer(serializers.ModelSerializer):

    class Meta:
        model = Currency
        fields = '__all__'