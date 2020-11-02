from datetime import datetime
from django.contrib.auth.models import User, Group
from django.db import transaction, DatabaseError
from rest_framework import serializers, status
from api.models import Outlay, Transfer, Currency



class UserSerializer(serializers.HyperlinkedModelSerializer):
    """
    Serializer for User model objects.
    """
    class Meta:
        model = User
        fields = ['url','username', 'email', 'groups']


class RegisterSerializer(serializers.ModelSerializer):
    """
    Serializer for Registration page data.
    """
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
    """
    Serializer for Group model objects.
    """
    class Meta:
        model = Group
        fields = ['url', 'name']



class OutlaySerializer(serializers.ModelSerializer):
    """
    Serializer for Outlay model objects.
    """
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

    def create(self, validated_data):
        validated_data['to_settle'] = validated_data['total_amount']
        return Outlay.objects.create(**validated_data)

class TransferSerializer(serializers.ModelSerializer):
    """
    Serializer for Transfer model objects.
    """
    class Meta:
        model = Transfer
        fields = ['netto', 'vat', 'currency', 'outlay', 'is_vat']

    def create(self, validated_data):
        """
        Overrides create method for:
        counting "brutto",
        seting "settled_date" on current time and date,
        checking if provided outley is valid.
        If everything pass, then performs updates modified outlay
        object and saves new transfer object in a transaction.
        """
        validated_data['brutto'] = (
            validated_data['netto'] + validated_data['vat']
        )
        validated_data['settled_date'] = datetime.now()
        outlay = self.check_and_change_outlay(validated_data)
        try:
            with transaction.atomic():
                outlay.save()
                return Transfer.objects.create(**validated_data)
        except DatabaseError as error:
            raise str(error) from error

    def check_and_change_outlay(self, data):
        """
        Checks if provided outley is valid and counts outlays
        new "settled" value.
        Raises error if something is wrong.
        """
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

    @staticmethod
    def check_if_user_is_owner(outlay_owner, transfer_owner):
        """
        Checks if user making transfer is its owner,
        else raises custom error message
        """
        if outlay_owner != transfer_owner:
            raise serializers.ValidationError("User is not owner of outlay")

    @staticmethod
    def check_if_is_settled(outlay_is_settled):
        """
        Checks if outlay is not already settled,
        else raises custom error with 409 status.
        """
        if outlay_is_settled:
            res = serializers.ValidationError("This outlay is settled.")
            res.status_code = status.HTTP_409_CONFLICT
            raise res

    @staticmethod
    def check_if_outlay_vat(outlay_is_vat, transfer_is_vat):
        """
        Checks if transfers field "is_vat" is set to "True" and
        selected outlays has "is_vat" set to "False",
        then raises custom error message with status 409.
        """
        if transfer_is_vat and not outlay_is_vat:
            res = serializers.ValidationError(
                "Vat transfer can't be done on this non-vat outlay"
            )
            res.status_code = status.HTTP_409_CONFLICT
            raise res

    @staticmethod
    def check_if_same_currency(outlay_currency, transfer_currency):
        """
        Checks if transfer and selected outlay are in same currency,
        else raises custom error message with status 409.
        """
        if outlay_currency != transfer_currency:
            res = serializers.ValidationError(
                "Outlay is in different currency then transfer."
            )
            res.status_code = status.HTTP_409_CONFLICT
            raise res



class CurrencySerializer(serializers.ModelSerializer):
    """
    Serializer for Currency model objects.
    """
    class Meta:
        model = Currency
        fields = '__all__'
