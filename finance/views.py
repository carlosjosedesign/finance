import json
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import IntegrityError
from django.shortcuts import redirect, render
from django.urls import reverse
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
from django.db.models import (
    F, Sum, Count, Case, When, Q, 
    ExpressionWrapper,
    IntegerField, FloatField,DecimalField, CharField,
    OuterRef, Subquery
)
from django.db.models.functions import (
    Cast
)
from django.utils.translation import gettext_lazy as _

from .util import get_prices, get_price, check_stock, monetaryConversor

from .balance import balance

from .models import User, UserPreferences, Type, Institution, Investiment, Transaction, Goal

from .forms import CreateInstitution, CreateType, CreateGoal, CreateInvestiment, EditInvestiment, CreateTransaction, CreateFirstTransaction


def index(request):
    
    if request.user.is_authenticated:
        user_data = User.objects.get(pk=request.user.id)
        types = user_data.types.order_by("percent").all()
        goals = user_data.goals.order_by("value").all()

        getBalance = balance(request.user.id)

        print(getBalance)
        print(getBalance['typesTotal'].get('Ações Brasileiras'))

    

        nowPercetages = {}
        maxTypesPercentage = 100
        for type in types:
            if getBalance['total'] > 0:
                nowPercetages[type.typeName] = round((getBalance['typesTotal'].get(type.typeName) / getBalance['total']) * 100, 2)
            else:
                nowPercetages[type.typeName] = 0

            maxTypesPercentage = maxTypesPercentage -  type.percent

        print(nowPercetages)

        goalsArray = []
        nowGoal = None
        if goals:
            nowGoal = goals[0].value
            biggerGoal = 0

            for goal in goals:
                lack = 0
                status = 'off'
                if getBalance['total'] > 0:

                    if getBalance['total'] >= goal.value:
                        status = 'on'
                        lack = 100
                    else:
                        lack = round( (getBalance['total'] / float(goal.value)) * 100, 2)
                        status = 'off'

                        if biggerGoal == 0:
                            biggerGoal = goal.value

                        if nowGoal < goal.value and goal.value <= biggerGoal:
                            nowGoal = goal.value

                        if goal.value > biggerGoal:
                            biggerGoal: goal.value

                goalsArray.append({
                    'id' : goal.id,
                    'value' : goal.value,
                    'lack'  : lack,
                    'status'  : status,
                })

        return render(request, "finance/dashboard.html",{
            "types": types,
            "maxTypesPercentage": maxTypesPercentage,
            "goals": goalsArray,
            "nowGoal": nowGoal,
            "balance": getBalance,
            "nowPercetages": nowPercetages,
            "type_form": CreateType(),
            "goal_form": CreateGoal(),
        })

    return render(request, "finance/index.html")

def getPrices(request):
    if request.method == "POST":
        body = json.loads(request.body)
        codes = body.get('codes')
        print(codes)
        nowPrices = {}
        prices = get_prices(codes)
        for code in codes:
            nowPrices[code] = prices.tickers[code].info['regularMarketPrice']

        return JsonResponse({"success": nowPrices }, status=201)


import requests

def getPrice(request, code):
    print('CODE:', code)
    price = get_price(code)
    print(price)
    
    # ipca = 433
    # selic = 432

    # codigo_bcb = selic
    # API_BCB_URL = 'https://api.bcb.gov.br/dados/serie/bcdata.sgs.{codigo_serie}/dados?formato=json&dataInicial={dataInicial}&dataFinal={dataFinal}'.format(
    #     codigo_serie = codigo_bcb,
    #     dataInicial = '1/01/2021',
    #     dataFinal = '31/12/2022'
    # )

    # try:
    #     r = requests.get(API_BCB_URL)
    #     reponse = r.json()
    #     print(reponse)
    # except:
    #     print('cant')
    
    return render(request, "finance/index.html")

@login_required(login_url="finance:login")
def investiments(request):

    if request.method == "GET":
        filtterType = request.GET.get('type')
        my_q = Q( user_id=request.user.id)
        if filtterType:
            my_q = Q( type__id=filtterType)

        user_data = User.objects.get(pk=request.user.id)
        portfolio = user_data.investiments.order_by("-date").all().filter(my_q).annotate(
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

            accomplished = Case(
                When(~Q(position="NONE"), then=0),
                When(position="NONE", then=(
                    (Case(
                        When(lastedTrans="SELL", then=('balance')),
                        When(lastedTrans="BUY", then=(
                            (F('allBought') * -1) + F('allSales')
                        ))
                    ))
                ))
            ,output_field=FloatField()),
            accomplishedRevenuePercent = Case(
                When(~Q(position="NONE"), then=0),
                When(position="NONE", then=(
                    ExpressionWrapper(
                        (
                            (
                                (Case(
                                    When(lastedTrans="SELL", then=(
                                        F('allSales') - F('allBought')
                                    )),
                                    When(lastedTrans="BUY", then=(
                                        F('allBought') - F('allSales')
                                    ))
                                ))
                            )
                            /
                            (Case(
                                When(lastedTrans="SELL", then=(
                                    F('allBought')
                                )),
                                When(lastedTrans="BUY", then=(
                                    Case(
                                        When(allBought__lte=F('allSales'), then=( F('allSales' ) )),
                                        When(allBought__gte=F('allSales'), then=( F('allBought' ) ))
                                    )
                                ))
                            ))
    
                        ) * 100.00
                    ,output_field=FloatField())
                ))
            ,output_field=FloatField()), 
        )
        types = user_data.types.order_by("typeName").all()
        institutions = user_data.institutions.order_by("name").all()

        maxTypesPercentage = 100
        for type in types:
            maxTypesPercentage = maxTypesPercentage -  type.percent
        
        #Get portfolio each
        codes = []
        realcodes = []
        nowPrices = {}
        sumRating = 0
       
        for investiment in portfolio:
            sumRating  = sumRating + investiment.rating
            if investiment.currency == 'R$':
                realcodes.append(investiment.code)
                codes.append(investiment.code+'.SA')
            else:
                realcodes.append(investiment.code)
                codes.append(investiment.code)

        portfolioTotal = 0
        currenciesTotal = { 
            'R$' : 0,
            '$' : 0,
            '€' : 0,
            '£' : 0,
        }
        prices = get_prices(codes)
        for i in range(len(codes)):
            price = prices.tickers[codes[i]].info['regularMarketPrice']
            nowPrices[codes[i]] = price
            print( realcodes[i], codes[i])
            print(portfolio[i])
            print(portfolio[i].total)
            thisInvestimentSum = round(float(price) * float(portfolio[i].qnt),2)
            
            currenciesTotal[portfolio[i].currency] = currenciesTotal[portfolio[i].currency] + thisInvestimentSum

            if portfolio[i].currency == user_data.preferences.currency :
                portfolioTotal = portfolioTotal + thisInvestimentSum 
            else:
                print(portfolio[i].currency, user_data.preferences.currency , thisInvestimentSum)
                thisInvestimentSumUser =  monetaryConversor(portfolio[i].currency, user_data.preferences.currency , thisInvestimentSum)
                portfolioTotal = portfolioTotal + thisInvestimentSumUser 
        
        portfolioTotal = round(portfolioTotal,2)


        if filtterType == None or ( filtterType != None and len(types) == 1):
            Balance = {'total': portfolioTotal}
        else:
            Balance = balance(request.user.id)

        # Create page controll
        paginator = Paginator(portfolio, 10)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        investiment_form = CreateInvestiment()
        investiment_form.fields["type"].queryset = types
        investiment_form.fields["institution"].queryset = institutions

        edit_investtiment = EditInvestiment()
        edit_investtiment.fields["type"].queryset = types
        edit_investtiment.fields["institution"].queryset = institutions

        transaction_form = CreateTransaction()
        transaction_form.fields["investiment"].queryset = portfolio

        return render(request, "finance/investiments.html",{
            "page_obj": page_obj,
            "portfolio": page_obj,
            "nowPrices": nowPrices,
            "sumRating": sumRating,
            "currenciesTotal": currenciesTotal,
            "portfolioTotal": portfolioTotal,
            "balance": Balance,
            "types": types,
            "maxTypesPercentage": maxTypesPercentage,
            "institutions": institutions,
            "type_form": CreateType(),
            "institution_form": CreateInstitution(),
            "investiment_form": investiment_form,
            "transaction_form": transaction_form,
            "edit_investiment_form": edit_investtiment,
        })

    if request.method == "POST":
        form = CreateInvestiment(request.POST)
        formset = CreateFirstTransaction(request.POST)

        if request.POST.get("transaction_date") == '':
            messages.error(request, _("You must select the transaction date"))
            return redirect('finance:investiments')


        if all([form.is_valid(), formset.is_valid()]):
            code = form.cleaned_data.get("code")
            #Check if stock exist before create
            if check_stock(code, form.cleaned_data.get("currency")):
                if Investiment.objects.filter(code=code, user=request.user).exists():
                    CheckInvestiment = Investiment.objects.annotate(
                    qnt=Sum(Case(
                        When(transactions__action="BUY", then='transactions__quantity' ),
                        When(transactions__action="SELL", then=F('transactions__quantity') * -1 ),
                        output_field=IntegerField()
                    )),).get(code=code, user=request.user)
                
                    investiment_id = CheckInvestiment.id

                    print('update investiment')
                    
                    if formset.cleaned_data.get("action") == 'SELL':
                        if CheckInvestiment.qnt - formset.cleaned_data.get("quantity") < 0.00:
                            CheckInvestiment.position = 'SELL'
                        elif CheckInvestiment.qnt - formset.cleaned_data.get("quantity") > 0.00:
                            CheckInvestiment.position = 'BUY'
                        else:
                            CheckInvestiment.position = 'NONE'

                    print(CheckInvestiment.qnt)
                    print(CheckInvestiment.qnt + formset.cleaned_data.get("quantity"))

                    if formset.cleaned_data.get("action") == 'BUY':
                        if CheckInvestiment.qnt + formset.cleaned_data.get("quantity") < 0.00:
                            print('SELL')
                            CheckInvestiment.position = 'SELL'
                        elif CheckInvestiment.qnt + formset.cleaned_data.get("quantity") > 0.00:
                            print('BUY')
                            CheckInvestiment.position = 'BUY'
                        else:
                            print('NONE')
                            CheckInvestiment.position = 'NONE'
                    
                    CheckInvestiment.save()

                else:
                    print('create investiment')
                    #Crete investiment
                    new_investiment = Investiment(
                        user = User.objects.get(pk=request.user.id),
                        code = code,
                        rating = form.cleaned_data.get("rating"),
                        currency = form.cleaned_data.get("currency"),
                        institution = form.cleaned_data.get("institution"),
                        type = form.cleaned_data.get("type"),
                    )

                    if formset.cleaned_data.get("action") == 'SELL':
                        new_investiment.position = 'SELL'
                    else:
                        new_investiment.position = 'BUY'
                    
                    new_investiment.save()
                    investiment_id = new_investiment.id


                # Crete investiment first transaction
                new_transaction = Transaction(
                    user = User.objects.get(pk=request.user.id),
                    investiment = Investiment.objects.get(pk=investiment_id),
                    quantity = formset.cleaned_data.get("quantity"),
                    payprice = formset.cleaned_data.get("payprice"),
                    action = formset.cleaned_data.get("action"),
                    transaction_date = formset.cleaned_data.get("transaction_date"),
                )
                new_transaction.save()

                return HttpResponseRedirect(request.headers['Referer']) 

            else:
                messages.error(request, _("Investiment does not match with any stock"))
                return redirect('finance:investiments')
    

@login_required(login_url="finance:login")
def investiment(request, id):
    if request.method == "PUT":
        body = json.loads(request.body)

        try:
            ThisInvestiment = Investiment.objects.get(pk=id, user=request.user)
        except (Investiment.DoesNotExist):
            return JsonResponse({
                "error": _("Investiment does not exist")
        }, status=404)

        print('Type',body.get("type"))

        ThisInvestiment.type = Type.objects.get(pk=body.get("type"), user=request.user) 
        ThisInvestiment.institution = Institution.objects.get(pk=body.get("institution"), user=request.user) 
        ThisInvestiment.rating = body.get("rating")
        ThisInvestiment.save()

        return HttpResponse(status=204) 

    if request.method == "DELETE":

        try:
            object_to_delete = Investiment.objects.get(pk=id, user=request.user)
        except (Investiment.DoesNotExist):
            return JsonResponse({
                "error": _("Investiment does not exist")
            }, status=404)


        objectId = object_to_delete.id
        # Delete the investiment
        object_to_delete.delete()
        return JsonResponse({"success": objectId }, status=201)


def updateInvestimentPosition(investiment_code, user):

    ThisInvestiment = Investiment.objects.annotate(
        qnt=Sum(Case(
            When(transactions__action="BUY", then='transactions__quantity' ),
            When(transactions__action="SELL", then=F('transactions__quantity') * -1 ),
            output_field=FloatField()
    )),).get(code=investiment_code, user=user)

    print('QNT >>>', ThisInvestiment.qnt)
    print(ThisInvestiment.qnt < 0.00)
    print(ThisInvestiment.qnt > 0.00)

    if ThisInvestiment.qnt < 0.00:
        ThisInvestiment.position = 'SELL'
    elif ThisInvestiment.qnt > 0.00:
        ThisInvestiment.position = 'BUY'
    else:
        ThisInvestiment.position = 'NONE'

    ThisInvestiment.save()       

@login_required(login_url="finance:login")
def transactions(request):
    if request.method == "GET":    
        user_data = User.objects.get(pk=request.user.id)

        filtterInvest = request.GET.get('i')
        my_q = Q( user_id=request.user.id)
        if filtterInvest:
            my_q = Q( investiment__id=filtterInvest)

        transactions = user_data.transactions.order_by("-transaction_date").all().filter(my_q).annotate(
            realDate=Cast('transaction_date', CharField()),
        )
    
        for transaction in transactions:
            print(transaction.transaction_date)

        investiments = user_data.investiments.order_by("code").all()

        transaction_form = CreateTransaction()
        transaction_form.fields["investiment"].queryset = investiments

        # Create page controll
        paginator = Paginator(transactions, 20)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        return render(request, "finance/transactions.html",{
            "transactions": page_obj,
            "page_obj": page_obj,
            "investiments": investiments,
            "balance": balance(request.user.id),
            "transaction_form": transaction_form,
        })

    if request.method == "POST":
        form = CreateTransaction(request.POST)

        if request.POST.get("transaction_date") == '' or request.POST.get("transaction_date") == None:
            messages.error(request, _("You must select the transaction date"))
            return HttpResponseRedirect(request.headers['Referer'])
        
        investiment = Investiment.objects.filter(pk=request.POST.get("investiment"), user=request.user.id)
        if not investiment:

            messages.error(request, _("Investiment does not exist"))
            return HttpResponseRedirect(request.headers['Referer'])


        if form.is_valid():
            # Crete investiment transaction
            new_transaction = Transaction(
                user = User.objects.get(pk=request.user.id),
                investiment = form.cleaned_data.get("investiment"),
                quantity = form.cleaned_data.get("quantity"),
                payprice = form.cleaned_data.get("payprice"),
                action = form.cleaned_data.get("action"),
                transaction_date = form.cleaned_data.get("transaction_date"),
            )
            new_transaction.save()
            
            #Update investiment position
            updateInvestimentPosition(form.cleaned_data.get("investiment"),request.user)

            return HttpResponseRedirect(request.headers['Referer'])

@login_required(login_url="finance:login")
def transaction(request, id):
    if request.method == "PUT":
        body = json.loads(request.body)
        print('chegou aqui 1')
        try:
            object_to_update = Transaction.objects.get(pk=id, user=request.user)
        except (Transaction.DoesNotExist):
            print('chegou aqui erro')
            return JsonResponse({
                "error": _("Transaction does not exist")
            }, status=404)

        print('chegou aqui 2')
        # Update transaction
        object_to_update.action = body.get('action')
        object_to_update.payprice = body.get('payprice')
        object_to_update.quantity = body.get('quantity')
        object_to_update.transaction_date = body.get('transaction_date')
        object_to_update.save()

        #Update investiment position
        updateInvestimentPosition(object_to_update.investiment,request.user)
        print('chegou aqui 3')
        return HttpResponse(status=204)

    if request.method == "DELETE":

        try:
            object_to_delete = Transaction.objects.get(pk=id, user=request.user)
        except (Transaction.DoesNotExist):
            return JsonResponse({
                "error": _("Transaction does not exist")
            }, status=404)
        
        objectId = object_to_delete.id
        # Delete the transaction
        object_to_delete.delete()

        #Update investiment position
        updateInvestimentPosition(object_to_delete.investiment,request.user)

        return JsonResponse({"success": objectId }, status=201)

@login_required(login_url="finance:login")
def institutions(request):
    
    if request.method == "POST":
        form = CreateInstitution(request.POST)
        
        if form.is_valid():
            new_institution = Institution(
                user = User.objects.get(pk=request.user.id),
                name = form.cleaned_data.get("name")
            )
            new_institution.save()

            institutionData = {
                    'id': new_institution.id,
                    'name': new_institution.name,
            }
            return JsonResponse(institutionData, safe=False)
        
        else:
            return JsonResponse({
                "error": form.errors
            }, status=404)
            
    
    if request.method == "GET":
        user_data = User.objects.get(pk=request.user.id)
        institutions = user_data.institutions.order_by("name").all().annotate(
            investiments = Count('investimentInstitution')
        )

        # Create page controll
        paginator = Paginator(institutions, 20)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        return render(request, "finance/institutions.html",{
            "page_obj": page_obj,
            "institutions": page_obj,
            "institution_form": CreateInstitution(),
            "balance": balance(request.user.id),
	    })


@login_required(login_url="finance:login")
def institution(request, id):
    if request.method == "PUT":
        body = json.loads(request.body)

        try:
            object_to_update = Institution.objects.get(pk=id, user=request.user)
        except (Institution.DoesNotExist):
            return JsonResponse({
                "error": _("Institution does not exist")
            }, status=404)
            
        object_to_update.name = body.get('name')
        object_to_update.save()
        return HttpResponse(status=204)

    if request.method == "DELETE":
        try:
            object_to_delete = Institution.objects.get(pk=id, user=request.user)
        except (Institution.DoesNotExist):
            return JsonResponse({
                "error": _("Institution does not exist")
            }, status=404)


        objectId = object_to_delete.id
        # Delete the institution
        try:
            object_to_delete.delete()
        except:
            return JsonResponse({
                "error": _("To delete this institution, remove all related investiments first")
            }, status=404)

        return JsonResponse({"success": objectId }, status=201)

@login_required(login_url="finance:login")
def create_type(request):
    if request.method == "POST":
        
        form = CreateType(request.POST)

        if form.is_valid():

            user_data = User.objects.get(pk=request.user.id)
            types = user_data.types.order_by("percent").all()
            maxTypesPercentage = 100
            for type in types:
                maxTypesPercentage = maxTypesPercentage -  type.percent

            print('maxTypesPercentage',maxTypesPercentage, form.cleaned_data.get("percent"))

            if form.cleaned_data.get("percent") > maxTypesPercentage:
                return JsonResponse({
                    "error": {
                        "percent": _("The sum of your investiment types percentages must be less than 100%")
                    }
                   
                }, status=404)
                

            new_type = Type(
                user = User.objects.get(pk=request.user.id),
                typeName = form.cleaned_data.get("typeName"),
                percent = form.cleaned_data.get("percent"),
                color = form.cleaned_data.get("color")
            )
            new_type.save()

            typenData = {
                'id': new_type.id,
                'name': new_type.typeName,
                'percent': new_type.percent,
            }

            return JsonResponse(typenData, safe=False)

        else:
            print('invalid')
            return JsonResponse({
                "error": form.errors
            }, status=404)
            


@login_required(login_url="finance:login")
def type(request, id):
    if request.method == "PUT":
        body = json.loads(request.body)

        try:
            object_to_update = Type.objects.get(pk=id, user=request.user)
        except (Type.DoesNotExist):
            return JsonResponse({
                "error": _("Type does not exist")
            }, status=404)
            
        object_to_update.typeName = body.get('typeName')
        object_to_update.percent = body.get('percent')
        object_to_update.color = body.get('color')
        object_to_update.save()
        return HttpResponse(status=204)

    if request.method == "DELETE":
        try:
            object_to_delete = Type.objects.get(pk=id, user=request.user)
        except (Type.DoesNotExist):
            return JsonResponse({
                "error": _("Type does not exist")
            }, status=404)

        objectId = object_to_delete.id
        # Delete type
        try:
            object_to_delete.delete()
        except:
            return JsonResponse({
                "error": _("To delete this type, remove all related investiments first")
            }, status=404)

        return JsonResponse({"success": objectId }, status=201)

@login_required(login_url="finance:login")
def create_goal(request):
    if request.method == "POST":
        
        form = CreateGoal(request.POST)
        print('form')
        print(form.errors )

        if form.is_valid():
            print('valid')
            new_goal = Goal(
                user = User.objects.get(pk=request.user.id),
                value = form.cleaned_data.get("value"),
            )
            new_goal.save()

            goalData = {
                'id': new_goal.id,
                'value': new_goal.value,
            }

            return JsonResponse(goalData, safe=False)

        else:
            print('invald')
            return JsonResponse({
                "error": form.errors
            }, status=404)

@login_required(login_url="finance:login")
def goal(request, id):
    
    if request.method == "DELETE":
        try:
            object_to_delete = Goal.objects.get(pk=id, user=request.user)
        except (Goal.DoesNotExist):
            return JsonResponse({
                "error": _("Goal does not exist")
            }, status=404)

        objectId = object_to_delete.id

        # Delete the goal
        try:
            object_to_delete.delete()
        except:
            return JsonResponse({
                "error": _("Something goes wrong")
            }, status=404)

        return JsonResponse({"success": objectId }, status=201)

def setCurrency(request):
    if request.method == "POST":
        body = json.loads(request.body)
        currency = body.get("currency")

        if request.user.is_authenticated:
            print('is_authenticated')
            try:
                obj = UserPreferences.objects.get(user=request.user.id)
                obj.currency = currency
                obj.save()
            except UserPreferences.DoesNotExist:
                obj = UserPreferences( user=request.user, currency = currency)
                obj.save()

        response = HttpResponse()
        response.set_cookie('currency', currency, max_age = 5000000)

        return HttpResponseRedirect(request.headers['Referer'])

def setTheme(request):
    if request.method == "POST":
        body = json.loads(request.body)
        theme = body.get("theme")

        if request.user.is_authenticated:
            try:
                obj = UserPreferences.objects.get(user=request.user.id)
                obj.theme = theme
                obj.save()
            except UserPreferences.DoesNotExist:
                obj = UserPreferences( user=request.user, theme = theme)
                obj.save()

        return HttpResponseRedirect(request.headers['Referer'])


def login_view(request):
    """ View: Controls logging in """

    if request.method == "POST":
        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)

            # If user tried to enter login_required page - go there after login
            if "next" in request.POST:
                request_args =  request.POST.get("next")[1:].split('/')
                return HttpResponseRedirect(reverse(
                        "finance:" + request_args[0], args=request_args[1:]
                       ))
            else:
                return HttpResponseRedirect(reverse("finance:index"))
        else:
            return render(request, "finance/login.html", {
                "message": _("Invalid username and/or password.")
            })
    else:
        # Show login panel only for not login users
        if request.user.is_authenticated:
            return HttpResponseRedirect(reverse("finance:index"))
        else:
            return render(request, "finance/login.html")


def logout_view(request):
    """ View: Controls logging out """

    logout(request)
    return HttpResponseRedirect(reverse("finance:index"))


def register(request):
    """ View: Controls registration """

    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]

        # Ensure no blank fields
        if  (not username) or (not email) or (not password):
            return render(request, "finance/register.html", {
                "message": _("You must fill out all fields.")
            })
        # Ensure password matches confirmation
        elif password != confirmation:
            return render(request, "finance/register.html", {
                "message": _("Passwords must match.")
            })

        # Attempt to create new user and its profile
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "finance/register.html", {
                "message": _("Username already taken.")
            })

        login(request, user)
        return HttpResponseRedirect(reverse("finance:index"))
    else:
        # Show register panel only for not login users
        if request.user.is_authenticated:
            return HttpResponseRedirect(reverse("finance:index"))
        else:
            return render(request, "finance/register.html")