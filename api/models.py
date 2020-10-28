from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

# Create your models here.

class Currency(models.Model):
    currency_name = models.CharField(db_column='Nazwa', max_length=15, primary_key=True)

    class Meta:
        db_table = "Waluta"


class Outlay(models.Model):
    currency= models.ForeignKey(Currency, on_delete=models.CASCADE)
    to_settle = models.DecimalField(db_column='Do rozliczenia', decimal_places=2, max_digits=16, validators=[MinValueValidator(0.01)])
    settled = models.DecimalField(db_column='Rozliczono', decimal_places=2, max_digits=16, validators=[MinValueValidator(0)])
    vat = models.BooleanField(db_column='Czy VAT?')
    is_settled = models.BooleanField(db_column='Czy spłacony?', default=False)
    owner = models.ForeignKey('auth.User', on_delete=models.CASCADE)

    def __init__(self, *args, **kwargs):
        super(Outlay, self).__init__(*args, **kwargs)
        self.old_settled = self.settled
        self.old_to_settle = self.to_settle

    def save(self, force_insert=False, force_update=False):
        if self.to_settle == self.old_to_settle:
            if self.old_settled < self.settled:
                self.to_settle = self.to_settle - (self.settled - self.old_settled)
            else:
                self.to_settle = self.to_settle + (self.old_settled - self.settled)
        super(Outlay,self).save(force_insert, force_update)
        self.old_settled = self.settled

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
