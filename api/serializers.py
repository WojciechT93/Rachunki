"""
Module providing Serializers
"""

from datetime import datetime
from django.contrib.auth.models import User, Group
from django.db import transaction
from rest_framework import serializers, status
from api.models import Expense, Transfer, Currency



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



class ExpenseSerializer(serializers.ModelSerializer):
    """
    Serializer for Expense model objects.
    """
    class Meta:
        model = Expense
        fields = [
            'id',
            'currency',
            'total_amount',
            'to_settle',
            'settled',
            'vat',
            'is_settled',
            'owner'
        ]
        read_only_fields = ['id', 'to_settle', 'settled', 'is_settled']

    def create(self, validated_data):
        validated_data['to_settle'] = validated_data['total_amount']
        return Expense.objects.create(**validated_data)

class TransferSerializer(serializers.ModelSerializer):
    """
    Serializer for Transfer model objects.
    """
    class Meta:
        model = Transfer
        fields = [
            'id',
            'netto',
            'vat',
            'brutto',
            'currency',
            'expense',
            'is_vat',
            'sent_date',
            'is_settled'
        ]
        read_only_fields = ['id', 'is_settled', 'brutto', 'sent_date']

    def create(self, validated_data):
        """
        Overrides create method for:
        counting "brutto",
        checking if provided outley is valid.
        """
        validated_data['brutto'] = (
            validated_data['netto'] + validated_data['vat']
        )
        validated_data['sent_date'] = datetime.now()
        self.check_expense(validated_data)
        return Transfer.objects.create(**validated_data)

    def check_expense(self, data):
        """
        Checks provides functions for checking if expense matches the
        transfer.
        Raises error if there is no expense for transfer.
        """
        expense = Expense.objects.get(id = data['expense'].id)
        if expense:
            self.check_if_user_is_owner(expense.owner_id, data['owner'].id)
            self.check_if_expense_vat(expense.vat, data['is_vat'])
            self.check_if_is_settled(expense.is_settled)
            self.check_if_same_currency(expense.currency, data['currency'])
        else:
            raise serializers.ValidationError(
                "There is no expense for this transfer."
            )

    @staticmethod
    def check_if_user_is_owner(expense_owner, transfer_owner):
        """
        Checks if user making transfer is its owner,
        else raises custom error message
        """
        if expense_owner != transfer_owner:
            raise serializers.ValidationError("User is not owner of expense")

    @staticmethod
    def check_if_is_settled(expense_is_settled):
        """
        Checks if expense is not already settled,
        else raises custom error with 409 status.
        """
        if expense_is_settled:
            res = serializers.ValidationError("This expense is settled.")
            res.status_code = status.HTTP_409_CONFLICT
            raise res

    @staticmethod
    def check_if_expense_vat(expense_is_vat, transfer_is_vat):
        """
        Checks if transfers field "is_vat" is set to "True" and
        selected expenses has "is_vat" set to "False",
        then raises custom error message with status 409.
        """
        if transfer_is_vat and not expense_is_vat:
            res = serializers.ValidationError(
                "Vat transfer can't be done on this non-vat expense"
            )
            res.status_code = status.HTTP_409_CONFLICT
            raise res

    @staticmethod
    def check_if_same_currency(expense_currency, transfer_currency):
        """
        Checks if transfer and selected expense are in same currency,
        else raises custom error message with status 409.
        """
        if expense_currency != transfer_currency:
            res = serializers.ValidationError(
                "Expense is in different currency then transfer."
            )
            res.status_code = status.HTTP_409_CONFLICT
            raise res

class SettleTransferSerializer(serializers.ModelSerializer):
    """
    Serializer for Transfer model objects.
    Used for admin settle transfer functionality.
    """
    class Meta:
        model = Transfer
        fields = [
            'id',
            'netto',
            'vat',
            'brutto',
            'currency',
            'expense',
            'is_vat',
            'sent_date',
            'is_settled'
        ]
        read_only_fields = [
            'id',
            'netto',
            'vat',
            'brutto',
            'currency',
            'expense',
            'is_vat',
            'sent_date'
        ]

    def update(self, instance, validated_data):
        """
        Overrides update method.
        If transfers 'is_settled' is true:
        updates expenses 'settled' value with 'brutto' from transfer.
        Updates expense and transfer objects.
        If false,
        """
        if validated_data['is_settled']:
            expense = Expense.objects.get(id = instance.expense.id)
            expense.settled += instance.brutto
            with transaction.atomic():
                expense.save()
                return (super(SettleTransferSerializer,self)
                            .update(instance, validated_data))

        return (super(SettleTransferSerializer,self)
                    .update(instance, validated_data))


class CurrencySerializer(serializers.ModelSerializer):
    """
    Serializer for Currency model objects.
    """
    class Meta:
        model = Currency
        fields = '__all__'
