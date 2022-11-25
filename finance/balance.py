from .models import User, Transaction
from django.db.models import (
    F, Q, Sum,  Case, When, FloatField, Subquery, OuterRef
)
from .util import get_prices, monetaryConversor

def balance(userID):
    user_data = User.objects.get(pk=userID)
    portfolio = user_data.investiments.order_by("-date").all().annotate( 
            lastedTrans=Subquery(
                Transaction.objects.filter(
                    investiment=OuterRef('pk')
                ).order_by('-transaction_date').values('action')[:1]
            ),      
            firstTrans=Subquery(
                Transaction.objects.filter(
                    investiment=OuterRef('pk')
                ).order_by('-id').values('payprice')[:1]
            ),       
            qnt = Case(
                When(position="BUY", then=(
                    Sum(Case(
                    When(transactions__action="BUY", then='transactions__quantity' ),
                    When(transactions__action="SELL", then=F('transactions__quantity') * -1 ),
                    output_field=FloatField()
                    ))
                )),
                When(position="SELL", then=(
                    Sum(Case(
                    When(transactions__action="BUY", then='transactions__quantity' ),
                    When(transactions__action="SELL", then=F('transactions__quantity') * -1 ),
                    output_field=FloatField()
                    ))* -1
                )),
                When(position="NONE", then=0)
            ,output_field=FloatField()), 

            allBought=  ( 
                        Sum(Case(
                            When(transactions__action="BUY", then=F('transactions__quantity') * F('transactions__payprice')),
                            output_field=FloatField()
                        ),  output_field=FloatField())
            * 1.0),         
            allSales =  ( 
                        Sum(Case(
                            When(transactions__action="SELL", then=F('transactions__quantity') * F('transactions__payprice')),
                            output_field=FloatField()
                        ),  output_field=FloatField())
            * 1.0), 

            balance =  Sum(Case(
                    When(transactions__action="BUY", then=F('transactions__quantity') * F('transactions__payprice')),
                    When(transactions__action="SELL", then=F('transactions__quantity') * F('transactions__payprice') * -1 ),
                    output_field=FloatField()
            )),

            total = Case(
                When(position="BUY", then=(
                    Case(
                        When( balance__gt = 0, then=F('balance')),
                        When( ~Q(balance__gt = 0), then=(
                            F('firstTrans') * F('qnt')
                        ))
                    ,output_field=FloatField())
                )),
                When(position="SELL", then=( 
                    Case(
                        When( balance__gt = 0, then=F('balance') * -1),
                        When( ~Q(balance__gt = 0), then=(
                            F('firstTrans') * F('qnt')
                        ))
                    ,output_field=FloatField())
                    
                )),
                When(position="NONE", then=('allBought'))

            ,output_field=FloatField()),  
    )

    codes = []
    realcodes = []
    invested = 0
    portfolioTotal = 0
    typesTotal = {}
    typesExpected = {}

    types = user_data.types.all()
    
    for type in types:
        typesTotal[type.typeName] = 0
        typesExpected[type.typeName] = 0
    
    for investiment in portfolio:
        if investiment.currency == 'R$':
            realcodes.append(investiment.code)
            codes.append(investiment.code+'.SA')
        else:
            realcodes.append(investiment.code)
            codes.append(investiment.code)
        

        if investiment.currency == user_data.preferences.currency:
            productTotal = investiment.total
        else:
            productTotal = monetaryConversor(investiment.currency, user_data.preferences.currency , investiment.total)
        
        invested = invested + productTotal

    prices = get_prices(codes)

    for i in range(len(codes)):
        price = prices.tickers[codes[i]].info['regularMarketPrice']
        thisInvestimentSum = round(float(price) * float(portfolio[i].qnt),2)

        
        if portfolio[i].currency != user_data.preferences.currency :
            thisInvestimentSum =  monetaryConversor(portfolio[i].currency, user_data.preferences.currency , thisInvestimentSum)
            
        
        typesTotal[portfolio[i].type.typeName] = typesTotal[portfolio[i].type.typeName] + thisInvestimentSum
    
        portfolioTotal = portfolioTotal + thisInvestimentSum 
        portfolioTotal = round(portfolioTotal,2)

    
    profit = 0
    if invested > 0:
        profit = round( (1 - (invested / portfolioTotal)) * 100 , 2)
        
    if portfolioTotal > 0:
        for type in types:
            typesExpected[type.typeName] = portfolioTotal * (type.percent /100)
    
    balance = {
        'total': portfolioTotal,
        'typesTotal': typesTotal,
        'typesExpected': typesExpected,
        'invested': invested,
        'profit': profit,
    }

    return balance