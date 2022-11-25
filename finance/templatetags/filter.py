from django import template
from django.utils.formats import localize
import locale
from re import sub
from decimal import Decimal
from django.template.defaultfilters import stringfilter
from forex_python.converter import CurrencyRates

register = template.Library()


@register.filter
def get_dic(dictionary, key):
    return dictionary.get(key)

@register.filter
def get_item(dictionary, key):
    if dictionary.get(key) == None:
        return dictionary.get(key+'.SA')

    return dictionary.get(key)


@register.simple_tag
def commaReplace(value):
    return str(value).replace(".",",")

@register.simple_tag
def moeda(value, userCurrency):
    value =  round(float(value),2)
    if userCurrency == '$':
        locale.setlocale(locale.LC_ALL, 'en_us')
    else:
        locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')

    value = locale.currency(value, grouping=True, symbol=None)
    # value = localize(value)
    return value

def formatfunc(*args):
    value = args[0]
    currency = args[1]
    pureValue = Decimal(sub(r'[^\d.]', '', str(value)))
    if abs(float(pureValue)) >= 0:
        return '{1} {0}'.format(value, currency)
    else:
        return '-{1} {0}'.format(abs(value), currency)


def convertCurrency(currency):
	if currency == 'R$' or currency == 'BRL':
		return 'BRL'
	if currency == '$' or currency == 'USD':
		return 'USD'
	if currency == '€' or currency == 'EUR':
		return 'EUR'
	if currency == '£' or currency == 'GBP':
		return 'GBP'

def monetaryConversorValue(from_currency, to_currency, amount):
	from_currency = convertCurrency(from_currency)
	to_currency = convertCurrency(to_currency)
	cr = CurrencyRates()
	output = cr.convert(from_currency, to_currency, amount)
	output = round(output,2)
	return output

@register.filter
@stringfilter
def multiply(value, qnt):
    count = round(float(value) * float(qnt),2)
    return count

@register.simple_tag
def profit(price, qnt, pay, position):
    if pay == 0:
        return 0

    have = multiply(price, qnt)

    if position == 'SELL': 
        # pay = pay * -1.00
        have = pay - have

    profit = round((have * 100 / pay) -100,2)

    if position == 'SELL':
        profit = profit * -1.00
        
        if profit > 0:
            profit = round(100 - profit,2)
   

    profit = str(profit).replace('.', ',')
    return profit

@register.simple_tag
def fixRevenue(revenue, action, currency):
    #print('fixRevenue',revenue)
    if action == 'SELL':
        return formatfunc(revenue * -1.00, currency)
    
    return formatfunc(revenue * 1.00, currency)


@register.simple_tag
def fixrevenuePercent(revenue, action):
    if action == 'SELL':
        return revenue * 1.00
    
    return revenue * -1.00

@register.simple_tag
def goWallet(rating, total):
    go = (rating/total)*100
    go =  round(float(go),2)
    return go

@register.simple_tag
def goWalletValue(rating, ratingtotal, total, currency, userCurrency):
    goPercent = rating/ratingtotal
    if currency != userCurrency:
        CurrencyValue = monetaryConversorValue(currency,userCurrency,1)
        total = round(total / CurrencyValue,2)

    goWalletVal = round(goPercent * total,2)
    goWalletVal = goWalletVal * 1.00
    goWalletValMoeda = moeda(goWalletVal, userCurrency)
    return formatfunc(goWalletValMoeda, currency)


@register.simple_tag
def toBuy(rating, ratingtotal, total, have,  currency, userCurrency):
    goPercent = rating/ratingtotal

    if currency != userCurrency:
        CurrencyValue = monetaryConversorValue(currency,userCurrency,1)
        total = round(total / CurrencyValue,2)

    toGo = goPercent * total
    toBuy =  toGo - round(have,2)
    toBuy = round(toBuy,2) * 1.00
    toBuy = moeda(toBuy, userCurrency)
    return formatfunc(toBuy, currency)

@register.simple_tag
def toBuyNum(rating, ratingtotal, total, have, Nowprice, currency, userCurrency):
    goPercent = rating/ratingtotal

    if currency != userCurrency:
        CurrencyValue = monetaryConversorValue(currency,userCurrency,1)
        total = round(total / CurrencyValue,2)

    toGo = goPercent * total
    toBuy =  toGo - round(have,2)
    toBuyNum = toBuy / Nowprice
    return round(toBuyNum,3)

@register.simple_tag
def inWallet(productTotal, portfolioTotal, currency, userCurrency):
    if portfolioTotal == 0:
        return 0
    if currency != userCurrency:
        productTotal = monetaryConversorValue(currency,userCurrency,productTotal)
    inw = (productTotal/portfolioTotal)*100
    inw =  round(float(inw),2)
    return inw

@register.simple_tag
def monetaryConversor(from_currency, to_currency, amount):
    output = monetaryConversorValue(from_currency, to_currency, amount)
    output = str(output).replace('.', ',')
    return output
