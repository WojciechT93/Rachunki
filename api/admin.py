from django.contrib import admin
from .models import Transfer, Outlay, Currency
# Register your models here.


admin.site.register(Transfer)
admin.site.register(Outlay)
admin.site.register(Currency)