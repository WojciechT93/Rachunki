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
# router.register(r'outlay', views.OutlayViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('currencies/', views.CurrencyListView.as_view()),
    path('currency/<str:currency_name>/', views.CurrencyDetailView.as_view()),
    path('outlays/', views.OutlaysListView.as_view()),
    path('outlays/<int:id>', views.OutlayDetailView.as_view()),
]
