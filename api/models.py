from django.db import models
from django.db import transaction, DatabaseError
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal

# Create your models here.

class Currency(models.Model):

    currency_name = models.CharField(
        db_column='Nazwa',
        max_length=15,
        primary_key=True
    )

    class Meta:
        db_table = "Waluta"

    def __str__(self):
        return self.currency_name


class Outlay(models.Model):

    currency = models.ForeignKey(
        Currency,
        db_column='Waluta',
        on_delete=models.CASCADE
    )
    total_amount = models.DecimalField(
        db_column='Cała kwota wydatku',
        decimal_places=2,
        max_digits=16,
        validators=[MinValueValidator(0.01)]
    )
    to_settle = models.DecimalField(
        db_column='Do rozliczenia',
        decimal_places=2,
        max_digits=16,
        validators=[MinValueValidator(0.01)]
    )
    settled = models.DecimalField(
        db_column='Rozliczono',
        decimal_places=2,
        max_digits=16,
        default=Decimal(0.00),
        validators=[MinValueValidator(0.00)]
    )
    vat = models.BooleanField(db_column='Czy VAT?')
    is_settled = models.BooleanField(db_column='Czy spłacony?', default=False)
    owner = models.ForeignKey(
        'auth.User',
        db_column='Użytkownik',
        on_delete=models.CASCADE
    )

    class Meta:
        db_table = "Wydatek"

    def __init__(self, *args, **kwargs):
        super(Outlay, self).__init__(*args, **kwargs)
        self.old_settled = self.settled
        self.old_to_settle = self.to_settle

    def save(self, *args, **kwargs):
        self.count_to_settle()
        self.check_if_is_settled()
        super(Outlay, self).save(*args, **kwargs)
        self.old_settled = self.settled

    def count_to_settle(self):
        if self.to_settle == self.old_to_settle:
            if self.old_settled < self.settled:
                self.to_settle = (
                    self.to_settle - (self.settled - self.old_settled)
                )
            else:
                self.to_settle = (
                    self.to_settle + (self.old_settled - self.settled)
                )
        if self.to_settle < 0:
            self.to_settle = 0
        if self.to_settle > self.total_amount:
            self.to_settle = self.total_amount

    def check_if_is_settled(self):
        if self.to_settle == 0:
            self.is_settled = True
        else:
            self.is_settled = False

    def __str__(self):
        return ("Przelew " + ("VAT" if self.vat else '') + " użytkownika "
                + str(self.owner))




class Transfer(models.Model):

    is_vat = models.BooleanField(db_column='Przelew VAT?', default=False)
    netto = models.DecimalField(
        db_column='Netto',
        decimal_places=2,
        max_digits=16,
        validators=[MinValueValidator(0.01)]
    )
    vat = models.DecimalField(
        db_column='VAT',
        decimal_places=2,
        max_digits=16,
        validators=[MinValueValidator(0.01)]
    )
    brutto = models.DecimalField(
        db_column='Brutto',
        decimal_places=2,
        max_digits=16,
        validators=[MinValueValidator(0.01)]
    )
    currency = models.ForeignKey(
        Currency,
        db_column='Waluta',
        on_delete=models.CASCADE)
    outlay = models.ForeignKey(
        Outlay,
        db_column='Wydatek',
        on_delete=models.CASCADE
    )
    settled_date = models.DateTimeField(db_column='Data przelewu')
    is_booked = models.BooleanField(db_column='Czy rozliczony?', default=False)
    owner = models.ForeignKey(
        'auth.User',
        db_column='Użytkownik',
        on_delete=models.CASCADE
    )

    def delete(self, *args, **kwargs):
        outlay = Outlay.objects.get(id=self.outlay.id)
        outlay.settled -= self.brutto
        try:
            with transaction.atomic():
                outlay.save()
                super(Transfer, self).delete(*args, **kwargs)
        except DatabaseError as de:
            raise str(de)

    class Meta:
        db_table = "Przelew"
