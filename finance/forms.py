from flatpickr import DatePickerInput
from django import forms
from django.forms.widgets import NumberInput
from colorfield.widgets import ColorWidget
from django.utils.translation import gettext_lazy as _
from django.conf import settings

from .models import User, Type, Institution, Investiment, Transaction, Goal

class RangeInput(NumberInput):
    input_type = 'range'


class CreateInstitution(forms.ModelForm):

    class Meta:
        model = Institution
        fields = ["name"]
        labels = {
            "name": _("Name"),
        }
        widgets = {
            "name": forms.TextInput(attrs={
                'required': 'required',
                "placeholder": _("Institution name"),
                "aria-label": _("Institution name"),
                "class": "form-control"
                }),
        }

class CreateType(forms.ModelForm):

    class Meta:
        model = Type
        fields = ["typeName", "percent", "color"]
        labels = {
            "typeName": _("Type"),
            "percent": _("Percent"),
            "color": _("Color"),
        }
        widgets = {
            "typeName": forms.TextInput(attrs={
                'required': 'required',
                "placeholder": _("Investiment type"),
                "aria-label": _("Investiment type"),
                "class": "form-control"
                }),
            "percent": RangeInput(attrs={
                'required': 'required',
                "placeholder": _("Percent"),
                "aria-label": _("Percent"),
                "class": "form-control",
                "max": "100",    
                "min": "1"
                }),
            "color": forms.TextInput(attrs={
                'required': 'required',
                "class": "form-control",
                "type": "color"
            }),
        }


class CreateInvestiment(forms.ModelForm):

    class Meta:
        model = Investiment
        fields = ["code", "rating", "currency", "institution", "type"]
        labels = {
            "code": _("Code"),
            "rating": _("Rating"),
            "currency": _("Currency"),
            "institution": _("Institution"),
            "type": _("Type"),
        }
        widgets = {
            "code": forms.TextInput(attrs={
                "placeholder": _("Prodcut CODE"),
                "aria-label": _("Prodcut CODE"),
                'required': 'required',
                "class": "form-control"
                }),
            "rating": NumberInput(attrs={
                "placeholder": _("Set share's weight in your portfolio"),
                "aria-label": _("Set share's weight in your portfolio"),
                "class": "form-control",  
                "required": "required",
                "min": "1",
                }),
            "currency": forms.Select(attrs={
                "class": "form-control",  
                'required': 'required',
                }),
            "institution": forms.Select(attrs={
                "class": "form-control",  
                'required': 'required',
                }),
            "type": forms.Select(attrs={
                "class": "form-control",
                'required': 'required',  
            }),
        }

class EditInvestiment(forms.ModelForm):

    class Meta:
        model = Investiment
        fields = ["rating","institution", "type"]
        labels = {
            "rating": _("Rating"),
            "institution": _("Institution"),
            "type": _("Type"),
        }
        widgets = {
            "rating": NumberInput(attrs={
                "placeholder": _("Set share's weight in your portfolio"),
                "aria-label": _("Set share's weight in your portfolio"),
                "class": "form-control",  
                'required': 'required',
                'min': '1'
                }),
            "institution": forms.Select(attrs={
                "class": "form-control",  
                'required': 'required',
                }),
            "type": forms.Select(attrs={
                "class": "form-control",
                'required': 'required',  
            }),
        }

ACTION_CHOICES = (
    ('BUY', _("BUY")),
    ('SELL', _("SELL")),
)

class CreateFirstTransaction(forms.ModelForm):

    transaction_date = forms.DateField(required=True, label=_("Transaction date"), widget=DatePickerInput(
        options = {
            "altFormat": "d F Y",
            "altInput": True,
            "dateFormat": "yyyy-mm-dd"
        },
        attrs = {
            'required': 'required',
        },
    ))

    action = forms.ChoiceField(choices = ACTION_CHOICES, label=_("Position"), widget= forms.Select(attrs={
        'required': 'required',
        'class': 'form-control'
    }))

    class Meta:
        model = Transaction
        fields = ["quantity", "payprice", "action", "transaction_date"]
        widgets = {
            "quantity": forms.NumberInput(attrs={
                'required': 'required',
                "placeholder": _("Quantity"),
                "aria-label": _("Quantity"),
                "class": "form-control",
                'min': '0.01',
                'step': "0.01"
                }),
            "payprice": forms.NumberInput(attrs={
                'required': 'required',
                "placeholder": _("Price"),
                "aria-label": _("Price"),
                "class": "form-control",  
                'min': '0.01',
                'step': "0.01"
            }),
        }

class CreateTransaction(forms.ModelForm):

    transaction_date = forms.DateField(required=False, label=_("Transaction date"), widget=DatePickerInput(
        options = {
            "altFormat": "d F Y",
            "altInput": True,
            "dateFormat": "yyyy-mm-dd"
        },
    ))


    action = forms.ChoiceField(choices = ACTION_CHOICES, label=_("Position"), widget= forms.Select(attrs={
        'class': 'form-control'
    }))


    class Meta:
        model = Transaction
        fields = ["investiment","quantity", "payprice", "action", "transaction_date"]
        labels = {
            "investiment": _("Investiment"),
            "quantity": _("Quantity"),
            "payprice": _("Price"),
            "transaction_date": _("First Transaction"),
        }
        widgets = {
            "investiment": forms.Select(attrs={
                "class": "form-control",  
                }),
            "quantity": forms.NumberInput(attrs={
                'required': 'required',
                "placeholder": _("Quantity"),
                "aria-label": _("Quantity"),
                "class": "form-control",
                'min': '0.01',
                'step': "0.0001"
                }),
            "payprice": NumberInput(attrs={
                'required': 'required',
                "placeholder": _("Price"),
                "aria-label": _("Price"),
                "class": "form-control",  
                'min': '0.01',
                'step': "0.0001"
            }),
        }

class CreateGoal(forms.ModelForm):

    class Meta:
        model = Goal
        fields = ["value"]
        labels = {
            "value": _("Goal"),
        }
        widgets = {
            "value": forms.NumberInput(attrs={
                'required': 'required',
                "placeholder": _("Goal"),
                "aria-label": _("Goal"),
                "class": "form-control",
                'min': 0,
                'step': "0.01"
                }),
        }