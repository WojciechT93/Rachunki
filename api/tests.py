import time, pytz
from datetime import datetime
from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import (
    APITestCase, URLPatternsTestCase, APIRequestFactory, APIClient,
    force_authenticate
)
from rest_framework import status
from api.models import Transfer, Expense, Currency
from .serializers import CurrencySerializer, ExpenseSerializer

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

        self.assertEqual(str(self.expense),
                        "ID 1 | Nie spłacony wydatek użytkownika Sam")
        self.assertEqual(str(self.expense1),
                        "ID 2 | Nie spłacony wydatek VAT użytkownika Sam")

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
            sent_date=datetime.now(pytz.utc),
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

    def test_contains_expected_values(self):
        data = self.serializer.data
        self.assertEqual(data['currency_name'], 'PLN')

class RegisterViewTestCase(APITestCase):
    """
    Tests RegisterView
    """
    def test_registration(self):
        data = {
            "username":"test",
            "email":"test@test.test",
            "password":"password"
        }
        response = self.client.post("/register/", data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

class CurrencyListViewTestCase(APITestCase):
    """
    Tests CurrencyListView
    """

    def setUp(self):
        self.superuser = User.objects.create_superuser(
            password='12345',
            username='admin',
            email='admin@user.test'
        )
        self.user = User.objects.create(
            password='12345',
            username='adam',
            email='adam@user.test'
        )
        self.currency = Currency.objects.create(
            currency_name='PLN'
        )

    def test_creating_currency(self):
        data = {"currency_name":"abc"}
        self.client.login(
            username='admin',
            password='12345'
        )
        response = self.client.post("/currencies/", data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        currency = Currency.objects.get(currency_name="abc")
        self.assertEqual(currency.currency_name, 'abc')
        self.client.logout()

    def test_get_currencies_list(self):
        response = self.client.get("/currencies/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

class CurrencyDetailViewTestCase(APITestCase):
    """
    Tests CurrencyDetailView
    """
    def setUp(self):
        self.superuser = User.objects.create_superuser(
            password='12345',
            username='admin',
            email='admin@user.test'
        )
        self.user = User.objects.create(
            password='12345',
            username='adam',
            email='adam@user.test'
        )
        self.currency = Currency.objects.create(
            currency_name='PLN'
        )
        self.currency = Currency.objects.create(
            currency_name='ABC'
        )
        self.currency = Currency.objects.create(
            currency_name='JPY'
        )

    def test_updating_currency(self):
        data = {"currency_name":"EUR"}
        self.client.force_login(self.user)
        response = self.client.put("/currency/PLN/", data)
        self.assertEqual(response.status_code,
                         status.HTTP_200_OK)
        currency = Currency.objects.get(currency_name='EUR')
        self.assertEqual(currency.currency_name, 'EUR')
        self.client.logout()

    def test_updating_currency_as_anonymous_user_error_status(self):
        data = {"currency_name":"BCD"}
        response = self.client.put("/currency/ABC/", data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_updating_currency_with_name_that_already_exists(self):
        data = {"currency_name":"JPY"}
        self.client.force_login(self.user)
        response = self.client.put("/currency/ABC/", data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.client.logout()

    def test_destroying_currency(self):
        self.client.login(
            username='admin',
            password='12345'
        )
        response = self.client.delete("/currency/JPY/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_get_currency(self):
        self.client.force_login(self.user)
        response = self.client.get("/currency/ABC/")
        self.assertEqual(response.data, {"currency_name":"ABC"})

class ExpenseListViewTestCase(APITestCase):
    """
    Tests ExpenseListView.
    """
    def setUp(self):
        self.currency1 = Currency.objects.create(
            currency_name='PLN'
        )
        self.currency2 = Currency.objects.create(
            currency_name='ABC'
        )
        self.currency3 = Currency.objects.create(
            currency_name='JPY'
        )
        self.superuser = User.objects.create_superuser(
            password='12345',
            username='admin',
            email='admin@user.test'
        )
        self.user = User.objects.create(
            password='12345',
            username='adam',
            email='adam@user.test'
        )
        self.data1 = {
            'currency':'PLN',
            'total_amount':'1000',
            'vat':'false',
            'owner':'2'
        }
        self.data2 = {
            'currency':'PLN',
            'total_amount':'1000',
            'vat':'false',
            'owner':'2'
        }
        self.data3 = {
            'currency':'PLN',
            'total_amount':'1000',
            'vat':'false',
            'owner':'2'
        }

    def test_admin_create_expense(self):
        self.client.login(
            username='admin',
            password='12345'
        )
        response=self.client.post('/expenses/', self.data1)
        self.assertEqual(response.status_code,status.HTTP_201_CREATED)
        self.assertEqual(Expense.objects.all().count(), 1)

    def test_get_expenses_list(self):
        self.client.force_login(self.user)
        response=self.client.get('/expenses/')
        self.assertEqual(response.status_code,status.HTTP_200_OK)
