from datetime import datetime
from django.contrib.auth.models import User, Group
from django.db import transaction, DatabaseError
from rest_framework import serializers, status
from api.models import Outlay, Transfer, Currency



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
        user = User.objects.create_user(
            validated_data['username'],
            validated_data['email'],
            validated_data['password']
        )
        return user


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ['url', 'name']



class OutlaySerializer(serializers.ModelSerializer):
    class Meta:
        model = Outlay
        fields = [
            'currency',
            'total_amount',
            'to_settle',
            'settled',
            'vat',
            'is_settled',
            'owner'
        ]
        read_only_fields = ['to_settle', 'settled', 'is_settled']

class TransferSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transfer
        fields = ['netto', 'vat', 'currency', 'outlay', 'is_vat']

    def create(self, validated_data):
        validated_data['brutto'] = (
            validated_data['netto'] + validated_data['vat']
        )
        validated_data['settled_date'] = datetime.now()
        outlay = self.check_and_update_outlay(validated_data)
        try:
            with transaction.atomic():
                outlay.save()
                return Transfer.objects.create(**validated_data)
        except DatabaseError as error:
            raise str(error)

    def check_and_update_outlay(self, data):
        outlay = Outlay.objects.get(id = data['outlay'].id)
        if outlay:
            self.check_if_user_is_owner(outlay.owner_id, data['owner'].id)
            self.check_if_outlay_vat(outlay.vat, data['is_vat'])
            self.check_if_is_settled(outlay.is_settled)
            self.check_if_same_currency(outlay.currency, data['currency'])
            outlay.settled += data['brutto']
        else:
            raise serializers.ValidationError(
                "There is no outlay for this transfer."
            )
        return outlay

    def check_if_user_is_owner(self, outlay_owner, transfer_owner):
        if outlay_owner != transfer_owner:
            raise serializers.ValidationError("User is not owner of outlay")

    def check_if_is_settled(self, outlay_is_settled):
        if outlay_is_settled:
            res = serializers.ValidationError("This outlay is settled.")
            res.status_code = status.HTTP_409_CONFLICT
            raise res

    def check_if_outlay_vat(self, outlay_is_vat, transfer_is_vat):
        if transfer_is_vat and not outlay_is_vat:
            res = serializers.ValidationError(
                "Vat transfer can't be done on this non-vat outlay"
            )
            res.status_code = status.HTTP_409_CONFLICT
            raise res

    def check_if_same_currency(self, outlay_currency, transfer_currency):
        if outlay_currency != transfer_currency:
            res = serializers.ValidationError(
                "Outlay is in different currency then transfer."
            )
            res.status_code = status.HTTP_409_CONFLICT
            raise res



class CurrencySerializer(serializers.ModelSerializer):

    class Meta:
        model = Currency
        fields = '__all__'
