from decimal import Decimal
from turtle import position
from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator, BaseValidator
from django.db import models
from .util import get_price, check_stock

class User(AbstractUser):
    pass

class UserPreferences(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, related_name="preferences")
	theme = models.CharField(max_length=10)
	lang = models.CharField(max_length=5)
	currency = models.CharField(max_length=2, default="R$")

class Type(models.Model):
	typeName = models.CharField(max_length=64)
	percent = models.PositiveSmallIntegerField(default=1,validators=[MinValueValidator(1),MaxValueValidator(100)])
	user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="types")
	color = models.CharField(max_length=7, null=True)

	def __str__(self):
		return self.typeName

class Institution(models.Model):
	name = models.CharField(max_length=64)
	user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="institutions")
	def __str__(self):
		return self.name


class Investiment(models.Model):
	code = models.CharField(max_length=10)
	rating = models.PositiveSmallIntegerField(default=1, validators=[MinValueValidator(1)])
	CURRENCIES_CHOICES = (
        ("R$", "Real Brasileiro"),
        ("$", "Dollar"),
        ("€", "Euro"),
        ("£", "GBP")
    )
	currency = models.CharField(max_length=2, choices=CURRENCIES_CHOICES, blank=False, null=False)
	position = models.CharField(max_length=4, blank=True, null=True)
	user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="investiments")
	date = models.DateTimeField(auto_now_add=True, null=False, verbose_name="created on")
	institution = models.ForeignKey(Institution, on_delete=models.RESTRICT, blank=True, null=True, verbose_name="Institution", related_name="investimentInstitution")
	type = models.ForeignKey(Type, on_delete=models.RESTRICT, blank=True, null=True, verbose_name="Type", related_name="investimentType")
	
	def __str__(self):
		return self.code

	def nowPrice(self):
		return get_price(self.code)


class Transaction(models.Model):
	quantity = models.DecimalField(decimal_places=4, max_digits=20, default=1, validators=[MinValueValidator(Decimal('0.01'))])
	payprice = models.DecimalField( decimal_places=4, max_digits=20, default=0.01, validators=[MinValueValidator(Decimal('0.01'))])
	ACTION_CHOICES = (
        ('BUY', "Buy"),
        ('SELL', "Sell"),
    )
	action = models.CharField(max_length=4, choices=ACTION_CHOICES,  default=ACTION_CHOICES[1][1], blank=False, null=False)
	user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="transactions")
	investiment = models.ForeignKey(Investiment, on_delete=models.CASCADE, verbose_name="Investiment", related_name="transactions")
	transaction_date = models.DateField(blank=True, null=True)
	
	def __str__(self):
		return f"Transaction: {self.quantity} * {self.payprice }"

class Goal(models.Model):
	value = models.DecimalField(decimal_places=2, max_digits=10, default=0)
	user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="goals")

	




