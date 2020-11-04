from django.contrib.auth.models import User, Group
from django.db.models import Avg, Sum
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, status, generics
from rest_framework.permissions import (
    IsAuthenticated, IsAdminUser,
)
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Transfer, Expense, Currency
from .serializers import (
    UserSerializer, GroupSerializer, TransferSerializer,
    ExpenseSerializer, CurrencySerializer, RegisterSerializer,
    SettleTransferSerializer
)
from .permissions import (
    CurrencyDetailAllowedMethods, CurrencyListAllowedMethods,
    ExpensesListAllowedMethods, TransferDetailViewAllowedMethods
)


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
    """
    Lists and creates currency objects.
    Http methods:

    GET - Lists all Currency objects for every user.
    GET /currencies/

    POST - Creates new Currency. Permitted only for admin user.
    POST /currencies/
    Request body:
    {
        "currency":"PLN"
    }
    """
    serializer_class = CurrencySerializer
    queryset = Currency.objects.all()
    permission_classes = [CurrencyListAllowedMethods]

class CurrencyDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Detail view of currency object.
    Http methods:

    GET- Retrieves existing Currency object. Permitted for authenticated user.
    GET /currency/PLN

    PUT- Updates Currency object given in url. Permitted for authenticated
        user.
    PUT /currency/EUR/
    Request body:
    {
        "currency":"PLN"
    }

    DELETE- Deletes currency object given in url. Permitted for superuser.
    DELETE /currency/PLN
    """

    queryset = Currency.objects.all()
    serializer_class = CurrencySerializer
    lookup_field = 'currency_name'
    permission_classes = [CurrencyDetailAllowedMethods,IsAuthenticated]

class ExpensesListView(generics.ListCreateAPIView):
    """
    Lists and creates expense objects
    Http methods:

    GET - Lists all Expenses objects owned by user. For superuser shows
        everything.
    GET /expenses/

    POST - Creates new expense. Permitted only for admin user.
    POST /expenses/
    Request body:
    {
        'currency':'PLN',
        'total_amount':'1000',
        'vat':'false',
        'owner':'2'
    }
    """

    queryset = Expense.objects.all()
    serializer_class = ExpenseSerializer
    lookup_field = 'id'
    permission_classes = [ExpensesListAllowedMethods, IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_superuser:
            return Expense.objects.all()
        return Expense.objects.filter(owner=self.request.user)


class ExpenseDetailView(generics.RetrieveDestroyAPIView):
    """
    Detail view of expense objects.
    All methods permitted only for  admin user.

    Http methods:
    GET- Retrieves existing Expenses object given in url.
    GET /expense/1

    DELETE- Deletes expense object given in url.
    DELETE /expense/1
    """

    queryset = Expense.objects.all()
    serializer_class = ExpenseSerializer
    lookup_field = 'id'
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        if self.request.user.is_superuser:
            return Expense.objects.all()
        return Expense.objects.filter(owner=self.request.user)


class TransfersListView(generics.ListCreateAPIView):
    """
    Lists and creates transfer objects.

    Http methods:

    GET - Lists all Transfer objects owned by user. For superuser shows
        everything.
    GET /transfers/

    POST - Creates new transfer. Permitted only for autheticated users.
    POST /transfers/
    Request body:
    {
        'currency':'PLN',
        'is_vat':'false'
        'netto':'1000',
        'vat':'0',
        'expense':'1',
        'owner':'2'
    }
    """
    queryset = Transfer.objects.all()
    serializer_class = TransferSerializer
    lookup_field = 'id'
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['is_settled']

    def get_queryset(self):
        if self.request.user.is_superuser:
            return Transfer.objects.all()
        return Transfer.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class TransferDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Returns detail view for transfer object.

    Http methods:

    GET- Retrieves existing Transfer object. Permitted for authenticated user.
    GET /transfer/<transfer id>

    PUT- Updates Transfer object given in url. Permitted for admin users.
    PUT /transfer/<transfer id>
    Request body:
    {
        "is_settled":"true"
    }

    DELETE- Deletes Transfer object given in url. Permitted for authorized
        users.
    DELETE /transfer/<transfer id>
    """

    queryset = Transfer.objects.all()
    serializer_class = TransferSerializer
    lookup_field = 'id'
    permission_classes = [TransferDetailViewAllowedMethods, IsAuthenticated]

    def get_serializer_class(self):
        if self.request.user.is_superuser:
            return SettleTransferSerializer
        return TransferSerializer

    def get_queryset(self):
        if self.request.user.is_superuser:
            return Transfer.objects.all()
        return Transfer.objects.filter(owner=self.request.user)


class StatisticsListView(APIView):
    """
    List of generated statistics values.

    GET /statistics/
    """
    permission_classes = [IsAuthenticated]
    def get(self, request, format=None):
        sum_settled_name = 'Suma wszystkich wydatków rozliczonych'
        sum_unsettled_name = ('Suma wszystkich wydatków nierozliczonych '
                              'w walucie “USD”')
        avg_vat_name = 'Średnia wartość przelewu VAT w miesiącu Wrzesień 2020'

        if request.user.is_superuser:
            sum_unsettled_usd = Expense.objects.filter(is_settled=False
                                             ).filter(currency='USD'
                                             ).aggregate(Sum('to_settle'))
            avg_vat = Transfer.objects.filter(is_vat=True
                                     ).filter(sent_date__year__gte=2020
                                     ).filter(sent_date__month__gte=10
                                     ).aggregate(Avg('brutto'))
            sum_settled = Expense.objects.filter(is_settled=True
                                       ).aggregate(Sum('settled'))
        else:
            sum_unsettled_usd = Expense.objects.filter(owner=self.request.user
                                             ).filter(is_settled=False
                                             ).filter(currency='USD'
                                             ).aggregate(Sum('to_settle'))
            avg_vat = Transfer.objects.filter(owner=self.request.user
                                     ).filter(is_vat=True
                                     ).filter(sent_date__year__gte=2020
                                     ).filter(sent_date__month__gte=10
                                     ).aggregate(Avg('brutto'))
            sum_settled = Expense.objects.filter(owner=self.request.user
                                       ).filter(is_settled=True
                                       ).aggregate(Sum('settled'))

        data = (
            {sum_settled_name:sum_settled['settled__sum']},
            {sum_unsettled_name:sum_unsettled_usd['to_settle__sum']},
            {avg_vat_name:avg_vat['brutto__avg']}
        )
        return Response(data=data, status=status.HTTP_200_OK)
