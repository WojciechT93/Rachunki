from django.contrib import admin
from .models import Transfer, Expense, Currency
# Register your models here.


admin.site.register(Transfer)
admin.site.register(Expense)
admin.site.register(Currency)
