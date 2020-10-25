from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

# Create your models here.

class Currency(models.Model):
    currency_name = models.CharField(db_column='Nazwa', max_length=15)

    class Meta:
        db_table = "Waluta"


class Outlay(models.Model):
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE)
    to_settle = models.DecimalField(db_column='Do rozliczenia', decimal_places=2, max_digits=16, validators=[MinValueValidator(0.01)])
    settled = models.DecimalField(db_column='Rozliczono', decimal_places=2, max_digits=16, validators=[MinValueValidator(0.01)])
    vat = models.BooleanField(db_column='Czy VAT?')
    is_settled = models.BooleanField(db_column='Czy spłacony?', default=False)
    owner = models.ForeignKey('auth.User', on_delete=models.CASCADE)

    class Meta:
        db_table = "Wydatek"


class Transfer(models.Model):
    netto = models.DecimalField(db_column='Betto', decimal_places=2, max_digits=16, validators=[MinValueValidator(0.01)])
    vat = models.DecimalField(db_column='VAT', decimal_places=2, max_digits=16, validators=[MinValueValidator(0.01)])
    brutto = models.DecimalField(db_column='Brutto', decimal_places=2, max_digits=16, validators=[MinValueValidator(0.01)])
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE)
    outlay = models.ForeignKey(Outlay, on_delete=models.CASCADE)
    settled_date = models.DateTimeField(db_column='Data przelewu')
    is_booked = models.BooleanField(db_column='Czy rozliczony?', default=False)

    class Meta:
        db_table = "Przelew"
