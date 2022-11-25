import json
import yfinance as yf
from yahooquery import Ticker
from forex_python.converter import CurrencyRates
# import investpy

# Get online investiment stock
def get_stock(code):
	ticker = yf.Ticker(code).info
	if(ticker['regularMarketPrice'] == None):
		# Try brazilian stock schange
		ticker = yf.Ticker(code + '.SA').info
	
	return ticker

def check_stock(code, currency):
	stock = get_stock(code)

	if stock['regularMarketPrice'] == None:
		return False

	#Tranform coin into currency code
	if currency == 'R$':
		fixcurrency = 'BRL'
	elif currency == '$':
		fixcurrency = 'USD'
	elif currency == '€':
		fixcurrency = 'EUR'
	elif currency == '£':
		fixcurrency = 'GBP'

	if stock['currency'] != fixcurrency:
		return False

	return True

def get_price(code):
	market_price = get_stock(code)['regularMarketPrice']

	return market_price

def get_prices(codes):
	tickers = yf.Tickers(codes)

	return tickers

def convertCurrency(currency):
	if currency == 'R$' or currency == 'BRL':
		return 'BRL'
	if currency == '$' or currency == 'USD':
		return 'USD'
	if currency == '€' or currency == 'EUR':
		return 'EUR'
	if currency == '£' or currency == 'GBP':
		return 'GBP'

def monetaryConversor(from_currency, to_currency, amount):
	from_currency = convertCurrency(from_currency)
	to_currency = convertCurrency(to_currency)
	cr = CurrencyRates()
	output = cr.convert(from_currency, to_currency, amount)
	output = round(output,2)
	print(output)
	return output

	
