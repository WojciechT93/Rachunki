"""zadanie URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from api import views

router = routers.DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'register', views.RegisterViewSet, 'register')
router.register(r'groups', views.GroupViewSet)
# router.register(r'transfers', views.TransferViewSet)
# router.register(r'currency', views.CurrencyViewSet)
# router.register(r'expense', views.ExpenseViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(router.urls)),
    path('api-auth/', include('rest_framework.urls',
                               namespace='rest_framework')),
    path('currencies/', views.CurrencyListView.as_view()),
    path('currency/<str:currency_name>/', views.CurrencyDetailView.as_view()),
    path('expenses/', views.ExpensesListView.as_view()),
    path('expense/<int:id>', views.ExpenseDetailView.as_view()),
    path('transfers/', views.TransfersListView.as_view()),
    path('transfer/<int:id>', views.TransferDetailView.as_view()),
    path('statystyki/', views.StatisticsListView.as_view())
]
