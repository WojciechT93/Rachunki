import time
from datetime import datetime
from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APITestCase, URLPatternsTestCase
from api.models import Transfer, Expense, Currency
from .serializers import CurrencySerializer

# Create your tests here.

class ExpenseModelTestCase(TestCase):
    """
    Tests Expense model methods.
    """

    def setUp(self):
        self.user = User.objects.create(
            password='12345',
            username='Sam',
            email='sam@sam.sam'
        )
        self.currency = Currency.objects.create(currency_name='PLN')
        self.expense = Expense.objects.create(
            currency=self.currency,
            total_amount=100.00,
            to_settle=0,
            settled=0,
            vat=False,
            is_settled=False,
            owner=self.user
        )
        self.expense1 = Expense.objects.create(
            currency=self.currency,
            total_amount=100.00,
            to_settle=0,
            settled=0,
            vat=True,
            is_settled=False,
            owner=self.user
        )

    def test_update_with_changed_settled(self):
        updated_expense = self.expense
        updated_expense.settled = 50
        updated_expense.save()
        updated_expense2 = Expense.objects.get(id=1)
        self.assertEqual(updated_expense2.to_settle,50)
        self.assertEqual(updated_expense2.is_settled, False)

        updated_expense2.settled = 100
        updated_expense2.save()
        updated_expense3 = Expense.objects.get(id=1)
        self.assertEqual(updated_expense3.to_settle,0)
        self.assertEqual(updated_expense3.is_settled, True)

        updated_expense3.settled = 150
        updated_expense3.save()
        updated_expense4 = Expense.objects.get(id=1)
        self.assertEqual(updated_expense4.to_settle,0)
        self.assertEqual(updated_expense4.is_settled, True)

        updated_expense4.settled = 0
        updated_expense4.save()
        updated_expense5 = Expense.objects.get(id=1)
        self.assertEqual(updated_expense5.to_settle,100)
        self.assertEqual(updated_expense5.is_settled, False)

    def test___str__(self):
        
        self.assertEqual(str(self.expense), "Wydatek użytkownika Sam")
        self.assertEqual(str(self.expense1), "Wydatek VAT użytkownika Sam")

class TransferModelTestCase(TestCase):
    """
    Tests transfer model methods.
    """

    def setUp(self):
        self.user = User.objects.create(
            password='12345',
            username='Sam',
            email='sam@sam.sam'
        )
        self.currency = Currency.objects.create(currency_name='PLN')
        self.expense = Expense.objects.create(
            currency=self.currency,
            total_amount=100.00,
            to_settle=0,
            settled=0,
            vat=False,
            is_settled=False,
            owner=self.user
        )
        self.expense1 = Expense.objects.create(
            currency=self.currency,
            total_amount=100.00,
            to_settle=0,
            settled=0,
            vat=True,
            is_settled=False,
            owner=self.user
        )
        self.transfer = Transfer.objects.create(
            id = 1,
            is_vat=False,
            netto=50,
            vat=20,
            brutto=70,
            expense=self.expense,
            currency=self.currency,
            sent_date=datetime.now(),
            is_settled=False,
            owner=self.user
        )
    
    def test_overriden_delete_method(self):
        """
        Tests overriden delete method.
        Checks if expense value changes, when
        transfer is being deleted.
        """

        expense = Expense.objects.get(id=1)
        transfer = Transfer.objects.get(id=1)
        expense = Expense.objects.get(id=1)
        expense.settled = 100
        expense.save()
        transfer.delete()
        self.assertEqual(Expense.objects.get(id=1).settled, 30)

class CurrencySerializerTestCase(TestCase):
    """
    Tests CurrencySerializer
    """

    def setUp(self):
        self.currency_json = {'currency_name':'PLN'}

        self.currency = Currency.objects.create(**self.currency_json)
        self.serializer = CurrencySerializer(instance=self.currency)

    def test_contains_expected_fields(self):
        data = self.serializer.data
        self.assertEqual(data.keys(), set(['currency_name']))
        self.assertEqual(data['currency_name'], 'PLN')