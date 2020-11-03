"""
Module providing model classes.
"""

from django.db import models
from django.db import transaction, DatabaseError
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal

# Create your models here.

class Currency(models.Model):
    """
    Currency model class.
    Currency objects have only 1 field- currency name
    which has to be unique due to being primary key.
    """
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
    """
    Outlay model class.
    Every outlay object has fields:
    curreny- foreign key of Currency model object, its the currency in
        which outlay has to be paid
    total_amount- whole amount of money that has to be paid
    to_settle- Amount of money that still needs to be paid
    settled- Amount of money that has been already paid
    vat- Boolean field, true indicates that the outlay can be paid
        with vat transfer.nsfer.
    is_settled- boolean field, True value indicates that whole outlay
        has been paid off.
    owner- foreign key of User, provides user that the outlay
        is imposed on.
    """
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
        """
        Overrides __init__.
        Saves 'settled' value of Outlay objects
        for updates purposes.
        """

        super(Outlay, self).__init__(*args, **kwargs)
        self.old_settled = self.settled

    def save(self, *args, **kwargs):
        """
        Overrides save method with custom methods counting
        'settled' and to 'settled' values.
        """

        self.count_to_settle()
        self.check_if_is_settled()
        super(Outlay, self).save(*args, **kwargs)
        self.old_settled = self.settled

    def count_to_settle(self):
        """
        Counts new 'to_settle' value.
        If counted 'to_settle' value is less then zero, sets its
        value to 0.
        If counted 'to_settle' value is higher then 'total_amount',
        sets its value to 'total_amount'.
        """
        self.to_settle = self.total_amount
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
        """
        Checks if 'to_settle' value is 0, if true then sets 'is_settled'
        value to 'True'. If false, sets 'is_settled' to false.
        """
        if self.to_settle == 0:
            self.is_settled = True
        else:
            self.is_settled = False

    def __str__(self):
        """
        Returns string represenatation of outlay objest.
        Example string:
        Przelew VAT użytkownika Bogdan.
        """
        return ("Przelew " + ("VAT" if self.vat else '') + " użytkownika "
                + str(self.owner))




class Transfer(models.Model):
    """
    Transfer model class.
    Every Transfer object has fields:
    is_vat- boolean field, indicates if its VAT transfer
    netto- netto value of transfer
    vat- VAT value of transfer
    brutto- Sum of netto and vat
    currency- foreign key of Currency object, indicates currency of
        paid amount
    outlay- foreign key of Outlay object, indicates for which outlay
        the transfer has been sent
    settled_date- date-time field, its the date and time of transfer
        being settled.
    is_booked- boolean field, True value means that transfer has
        been settled
    owner- foreign key of user object, provides user that made the
        transfer

    """
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
    sent_date = models.DateTimeField(db_column='Data przelewu')
    is_setted = models.BooleanField(db_column='Czy rozliczony?', default=False)
    owner = models.ForeignKey(
        'auth.User',
        db_column='Użytkownik',
        on_delete=models.CASCADE
    )

    def delete(self, *args, **kwargs):
        """
        Overrides delete method.
        Gets outlay object, that deleted transfer was for and
        decreases its "settled" value by the amount of "brutto"
        from that transfer.
        Performes update on outlay object and deletes transfer object.
        """
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
