import json
from django.test import TestCase, Client
from django.contrib import auth
from django.contrib.messages import get_messages

from .models import *
from .forms import *


class ModelsTestCase(TestCase):
    def setUp(self):
        #Create user
        self.user = User.objects.create_user(username="test", password="test")

        #Create institution
        self.institution = Institution.objects.create(user=self.user, name="Broker")

        #Create type
        self.type = Type.objects.create(user=self.user, typeName="TypeTest", percent=10, color="#ffffff")

        #Create investiment
        self.investiment = Investiment.objects.create(
            user=self.user, 
            code="GOOGL",
            rating=1,
            currency="$",
            position='NONE',
            institution=self.institution,
            type=self.type,
        )

        #Create transaction
        self.transaction = Transaction.objects.create(
            user=self.user, 
            quantity=10,
            payprice=10,
            action="BUY",
            investiment=self.investiment,
            transaction_date="2022-11-11",
        )

        #Create goal
        self.user = Goal.objects.create(user=self.user, value="10000")

    def test_auto_preferences_create(self):
        """ Create new user -> create new user preferences  """
        self.assertEqual(UserPreferences.objects.count(), 1)


class RegistersViewsTestCase(TestCase):
    """ Backend test of every view """
    def setUp(self):
        # Force english translation
        settings.LANGUAGE_CODE = 'en'

        self.user = User.objects.create_user(username="test", password="test")
        self.c = Client()

        # Login view - GET
        def test_GET_login_status_code(self):
            """ Make sure status code for GET login is 200 """
            response = self.c.get("/login")
            self.assertEqual(response.status_code, 200)
        
        def test_GET_login_correct_redirection(self):
            """ Check redirection to index for logged users """

            # Login user
            self.c.login(username='test', password="test")
            # Get the response
            response = self.c.get('/login')
            # Check redirect status code and redirection url
            self.assertEqual(response.status_code, 302)
            self.assertEqual(response.url, '/')

        # Login view - POST
        def test_POST_login_correct_user(self):
            """ Check login basic behaviour - status code, redirection, login status """
            # Get user logged out info
            c_logged_out = auth.get_user(self.c)
            # Try to login
            response = self.c.post('/login', {'username': 'test', 'password': 'test'})
            # Get user logged in info
            c_logged_in = auth.get_user(self.c)

            self.assertFalse(c_logged_out.is_authenticated)
            self.assertEqual(response.status_code, 302)
            self.assertEqual(response.url, '/')
            self.assertTrue(c_logged_in.is_authenticated)

    def test_POST_login_invalid_password(self):
        """ Check invalid password login behaviour """
        response = self.c.post('/login', {'username': 'test', 'password': '123'})

        self.assertEqual(response.context["message"], "Invalid username and/or password.")

    # Logout view
    def test_logout_view(self):
        """ Check all logout behaviour - status code, redirection, login status """
        # Login user
        self.c.login(username='test', password="test")
        # Get user logged in info
        c_logged_in = auth.get_user(self.c)
        # Try to logout
        response = self.c.get('/logout')
        # Get user logged out info
        c_logged_out = auth.get_user(self.c)

        self.assertTrue(c_logged_in.is_authenticated)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/')
        self.assertFalse(c_logged_out.is_authenticated)

    # Register view - GET
    def test_GET_register_status_code(self):
        """ Make sure status code for GET register is 200 """
        response = self.c.get("/register")
        self.assertEqual(response.status_code, 200)

    def test_GET_register_correct_redirection(self):
        """ Check redirection to index for logged users """
        # Login user
        self.c.login(username='test', password="test")
        # Get response
        response = self.c.get('/register')
        # Check redirect status code and redirection url
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/')

    # Register view - POST
    def test_POST_register_correct(self):
        """ Check register basic behaviour - status code, redirection, login status """
        # Get user logged out info
        c_logged_out = auth.get_user(self.c)
        # Try to register
        response = self.c.post('/register', {
            'username': 'correct',
            'email': 'correct@gmail.com',
            'password': 'correct',
            'confirmation': 'correct'
            })
        # Get user registered info
        c_registered = auth.get_user(self.c)
        # Get the new user
        new_user = User.objects.filter(username='correct')

        self.assertFalse(c_logged_out.is_authenticated)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/')
        self.assertTrue(c_registered.is_authenticated)
        self.assertEqual(new_user.count(), 1)

    def test_POST_register_empty_username(self):
        """ If username empty -> make sure error msg is correct """
        # Try to register
        response = self.c.post('/register', {
            'username': '',
            'email': 'correct@gmail.com',
            'password': 'correct',
            'confirmation': 'correct'
            })

        self.assertEqual(response.context['message'], "You must fill out all fields.")

    def test_POST_register_empty_email(self):
        """ If email empty -> make sure error msg is correct """
        # Try to register
        response = self.c.post('/register', {
            'username': 'correct',
            'email': '',
            'password': 'correct',
            'confirmation': 'correct'
            })

        self.assertEqual(response.context['message'], "You must fill out all fields.")

    def test_POST_register_empty_password(self):
        """ If password empty -> make sure error msg is correct """
        # Try to register
        response = self.c.post('/register', {
            'username': 'correct',
            'email': 'correct@gmail.com',
            'password': '',
            'confirmation': ''
            })

        self.assertEqual(response.context['message'], "You must fill out all fields.")

    def test_POST_register_passwords_dont_match(self):
        """ If password != confirmation -> make sure error msg is correct """
        # Try to register
        response = self.c.post('/register', {
            'username': 'correct',
            'email': 'correct@gmail.com',
            'password': 'test',
            'confirmation': 'correct'
            })

        self.assertEqual(response.context['message'], "Passwords must match.")

    def test_POST_register_username_taken(self):
        """ If user already exists -> make sure error msg is correct """
        # Try to register
        response = self.c.post('/register', {
            'username': 'test',
            'email': 'test@gmail.com',
            'password': 'test',
            'confirmation': 'test'
        })

        self.assertEqual(response.context['message'], "Username already taken.")


class ViewsTestCase(TestCase):

    def setUp(self):
        # Force english translation
        settings.LANGUAGE_CODE = 'en'

        self.user = User.objects.create_user(username="test", password="test")
        self.c = Client()
    
    #Create type
    def test_create_type(self):
        # Login user
        self.c.login(username="test", password="test")

        # Post a type
        response = self.c.post('/create_type', {
            "typeName": "my first type",
            "percent" : 70,
            "color": "#ff0000"
        }, HTTP_REFERER='/dashboard')

        self.assertEqual(Type.objects.filter(typeName="my first type").count(), 1)
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            response.content,
            {
                "id": 1,
                "name": "my first type",
                "percent" : 70,
            }
        )

    #Dont create with 0%
    def test_create_invalid_type(self):
        # Login user
        self.c.login(username="test", password="test")

        # Post a invalid type
        response = self.c.post('/create_type', {
            "typeName": "my second type",
            "percent" : 0,
            "color": "#ff0000"
        }, HTTP_REFERER='/dashboard')

        self.assertEqual(response.status_code, 404)
        self.assertJSONEqual(
            response.content,
            {
                'error': {
                    'percent': ['Ensure this value is greater than or equal to 1.' ]
                }
            }
        )

    #Dont create type if 100% is filled
    def test_create_maxpercent_type(self):
        # Login user
        self.c.login(username="test", password="test")

        # Post a invalid type
        response = self.c.post('/create_type', {
            "typeName": "my first type",
            "percent" : 70,
            "color": "#ff0000"
        }, HTTP_REFERER='/dashboard')
        response = self.c.post('/create_type', {
            "typeName": "my second type again",
            "percent" : 90,
            "color": "#ff0000"
        }, HTTP_REFERER='/dashboard')

        self.assertEqual(response.status_code, 404)
        self.assertJSONEqual(
            response.content,
            {
                'error': {
                    'percent': "The sum of your investiment types percentages must be less than 100%"
                }
            }
        )
    
    #Update type
    def test_update_type(self):
        # Login user
        self.c.login(username="test", password="test")

        #Create type
        old_type = Type.objects.create(user=self.user, typeName="TypeTest", percent=10, color="#ffffff")
        
        # Update a type
        response = self.c.put('/type/' + str(old_type.id), json.dumps({
            "typeName": "my new type",
            "percent" : 70,
            "color": "#ff0000"
        }))

        # Get the type after editing
        new_type = Type.objects.get(pk=old_type.id)


        self.assertEqual(new_type.typeName, "my new type")
        self.assertEqual(response.status_code, 204)

    #Delete empty Type
    def test_delete_type(self):
        # Login user
        self.c.login(username="test", password="test")

        #Create type
        this_type = Type.objects.create(user=self.user, typeName="TypeTest", percent=10, color="#ffffff")

        # Get types count before delete request
        types_count_before_delete = Type.objects.all().count()

        # Delete type
        response = self.c.delete('/type/' + str(this_type.id), json.dumps({"id": this_type.id}))

        # Get types count after delete request
        types_count_after_delete = Type.objects.all().count()

        self.assertEqual(response.status_code, 201)
        self.assertEqual(types_count_before_delete, 1)
        self.assertEqual(types_count_after_delete, 0)

    #Cant delete type contains investiments
    def test_dont_delete_type(self):
        # Login user
        self.c.login(username="test", password="test")

        #Create type
        self.type = Type.objects.create(user=self.user, typeName="TypeTest", percent=10, color="#ffffff")
        
        #Create institution
        self.institution = Institution.objects.create(user=self.user, name="Broker")

        #Create investiment
        self.investiment = Investiment.objects.create(
            user=self.user, 
            rating=1,
            currency="$",
            position='NONE',
            institution=self.institution,
            type=self.type,
        )

        # Get types count before delete request
        types_count_before_delete = Type.objects.all().count()

        # Delete type
        response = self.c.delete('/type/' + str(self.type.id), json.dumps({"id": self.type.id}))

        # Get types count after delete request
        types_count_after_delete = Type.objects.all().count()

        self.assertEqual(response.status_code, 404)
        self.assertEqual(types_count_before_delete, 1)
        self.assertEqual(types_count_after_delete, 1)

    #Create institution
    def test_create_institution(self):
        # Login user
        self.c.login(username="test", password="test")

        # Post a institution
        response = self.c.post('/institutions', {"name": "my first institution",}, HTTP_REFERER='/institutions')

        self.assertEqual(Institution.objects.filter(name="my first institution").count(), 1)
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            response.content,
            {
                "id": 1,
                "name": "my first institution",
            }
        )
    
    #Delete empty institution
    def test_delete_institution(self):
        # Login user
        self.c.login(username="test", password="test")

        #Create institution
        this_institution = Institution.objects.create(user=self.user, name="Broker")

        # Get institutions count before delete request
        institution_count_before_delete = Institution.objects.all().count()

        # Delete type
        response = self.c.delete('/institution/' + str(this_institution.id), json.dumps({"id": this_institution.id}))

        # Get institutions count after delete request
        institution_count_after_delete = Institution.objects.all().count()

        self.assertEqual(response.status_code, 201)
        self.assertEqual(institution_count_before_delete, 1)
        self.assertEqual(institution_count_after_delete, 0)

    #Cant delete institution contains investiments
    def test_dont_delete_institution(self):
        # Login user
        self.c.login(username="test", password="test")

        #Create type
        self.type = Type.objects.create(user=self.user, typeName="TypeTest", percent=10, color="#ffffff")
        
        #Create institution
        self.institution = Institution.objects.create(user=self.user, name="Broker")

        #Create investiment
        self.investiment = Investiment.objects.create(
            user=self.user, 
            rating=1,
            currency="$",
            position='NONE',
            institution=self.institution,
            type=self.type,
        )

        # Get institutions count before delete request
        institution_count_before_delete = Institution.objects.all().count()

        # Delete type
        response = self.c.delete('/institution/' + str(self.institution.id), json.dumps({"id": self.institution.id}))

        # Get institutions count after delete request
        institution_count_after_delete = Institution.objects.all().count()

        self.assertEqual(response.status_code, 404)
        self.assertEqual(institution_count_before_delete, 1)
        self.assertEqual(institution_count_after_delete, 1)

    #Crete valid investiments - check action and currency
    def test_create_valid_investments(self):
        # Login user
        self.c.login(username="test", password="test")

        #Create type
        self.type = Type.objects.create(user=self.user, typeName="TypeTest", percent=10, color="#ffffff")
        
        #Create institution
        self.institution = Institution.objects.create(user=self.user, name="Broker")

        # Create buy investiment
        responseBuy = self.c.post('/investiments', {
            "code": "ITSA4",
            "rating" : 1,
            "currency": "R$",
            "payprice" : 10,
            "quantity" : 10,
            "action": "BUY",
            "transaction_date": "2022-11-11",
            "institution": self.institution.id,
            "type" : self.type.id
        }, HTTP_REFERER='/investiments')
        self.assertEqual(responseBuy.status_code, 302)

        responseBuySecond = self.c.post('/investiments', {
            "code": "DIS",
            "rating" : 1,
            "currency": "$",
            "payprice" : 10,
            "quantity" : 10,
            "action": "BUY",
            "transaction_date": "2022-11-11",
            "institution": self.institution.id,
            "type" : self.type.id
        }, HTTP_REFERER='/investiments')
        self.assertEqual(responseBuySecond.status_code, 302)

        # Create sell investiment
        responseSell = self.c.post('/investiments', {
            "code": "GOOGL",
            "rating" : 1,
            "currency": "$",
            "payprice" : 10,
            "quantity" : 10,
            "action": "SELL",
            "transaction_date": "2022-11-11",
            "institution": self.institution.id,
            "type" : self.type.id
        }, HTTP_REFERER='/investiments')
        self.assertEqual(responseSell.status_code, 302)

        responseSellSecond = self.c.post('/investiments', {
            "code": "DIS",
            "rating" : 1,
            "currency": "$",
            "payprice" : 10,
            "quantity" : 10,
            "action": "SELL",
            "transaction_date": "2022-11-11",
            "institution": self.institution.id,
            "type" : self.type.id
        }, HTTP_REFERER='/investiments')
        self.assertEqual(responseSellSecond.status_code, 302)


        response = self.c.get('/investiments')
        self.assertEqual(response.status_code, 200)

        self.assertEqual(response.context['portfolio'][0].total, 100)
        self.assertEqual(response.context['portfolio'][0].position, 'SELL')
        self.assertEqual(response.context['portfolio'][1].qnt, 0)
        self.assertEqual(response.context['portfolio'][1].total, 100)
        self.assertEqual(response.context['portfolio'][1].position, 'NONE')
        self.assertEqual(response.context['portfolio'][2].total, 100)
        self.assertEqual(response.context['portfolio'][2].position, 'BUY')

    #Crete invalid investiments - check code and currency
    def test_create_invalid_investments(self):
        # Login user
        self.c.login(username="test", password="test")

        #Create type
        self.type = Type.objects.create(user=self.user, typeName="TypeTest", percent=10, color="#ffffff")
        
        #Create institution
        self.institution = Institution.objects.create(user=self.user, name="Broker")

        # Create investiment with invalid code
        invalidCode = self.c.post('/investiments', {
            "code": "XXXX",
            "rating" : 1,
            "currency": "R$",
            "payprice" : 10,
            "quantity" : 10,
            "action": "BUY",
            "transaction_date": "2022-11-11",
            "institution": self.institution.id,
            "type" : self.type.id
        }, HTTP_REFERER='/investiments')
        self.assertEqual(invalidCode.status_code, 302)
        messages = list(get_messages(invalidCode.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Investiment does not match with any stock')

        # Create investiment with invalid currency
        invalidCurrency = self.c.post('/investiments', {
            "code": "DIS",
            "rating" : 1,
            "currency": "R$",
            "payprice" : 10,
            "quantity" : 10,
            "action": "BUY",
            "transaction_date": "2022-11-11",
            "institution": self.institution.id,
            "type" : self.type.id
        }, HTTP_REFERER='/investiments')
        self.assertEqual(invalidCurrency.status_code, 302)
        moreMessages = list(get_messages(invalidCurrency.wsgi_request))
        self.assertEqual(len(moreMessages), 2)
        self.assertEqual(str(moreMessages[1]), 'Investiment does not match with any stock')

    #Create a valid transaction - check if investiment exist
    def test_create_valid_transactions(self):
        # Login user
        self.c.login(username="test", password="test")

        #Create type
        self.type = Type.objects.create(user=self.user, typeName="TypeTest", percent=10, color="#ffffff")
        
        #Create institution
        self.institution = Institution.objects.create(user=self.user, name="Broker")

        # Create investiment
        responseInvestiment = self.c.post('/investiments', {
            "code": "ITSA4",
            "rating" : 1,
            "currency": "R$",
            "payprice" : 10,
            "quantity" : 10,
            "action": "BUY",
            "transaction_date": "2022-11-11",
            "institution": self.institution.id,
            "type" : self.type.id
        }, HTTP_REFERER='/investiments')
        self.assertEqual(responseInvestiment.status_code, 302)

        self.investiment = Investiment.objects.get(code="ITSA4")

        # Create no date transaction
        responseNoDateTransaction = self.c.post('/transactions', {
            "investiment": self.investiment.id,
            "action": "BUY",
            "payprice" : 10,
            "quantity" : 10,
        }, HTTP_REFERER='/transactions')
        self.assertEqual(responseNoDateTransaction.status_code, 302)
        messages = list(get_messages(responseNoDateTransaction.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'You must select the transaction date')

        # Create invalid transaction
        responseInvalidTransaction = self.c.post('/transactions', {
            "investiment": 99,
            "action": "BUY",
            "payprice" : 10,
            "quantity" : 10,
            "transaction_date": "2022-11-12",
        }, HTTP_REFERER='/transactions')
        self.assertEqual(responseInvalidTransaction.status_code, 302)
        messages = list(get_messages(responseInvalidTransaction.wsgi_request))
        self.assertEqual(len(messages), 2)
        self.assertEqual(str(messages[1]), 'Investiment does not exist')

        # Create valid transaction
        responseTransaction = self.c.post('/transactions', {
            "investiment": self.investiment.id,
            "action": "BUY",
            "payprice" : 10,
            "quantity" : 10,
            "transaction_date": "2022-11-12",
        }, HTTP_REFERER='/transactions')
        self.assertEqual(responseTransaction.status_code, 302)

        investimentsResponse = self.c.get('/investiments')
        self.assertEqual(investimentsResponse.status_code, 200)

        self.assertEqual(investimentsResponse.context['portfolio'][0].total, 200)
        self.assertEqual(investimentsResponse.context['portfolio'][0].qnt, 20)
        self.assertEqual(investimentsResponse.context['portfolio'][0].position, 'BUY')

        transactionsResponse = self.c.get('/transactions')
        self.assertEqual(transactionsResponse.status_code, 200)
        self.assertEqual(len(transactionsResponse.context['transactions']), 2)

    #Update transactions
    def test_update_transactions(self):
        # Login user
        self.c.login(username="test", password="test")

        #Create type
        self.type = Type.objects.create(user=self.user, typeName="TypeTest", percent=10, color="#ffffff")
        
        #Create institution
        self.institution = Institution.objects.create(user=self.user, name="Broker")

        # Create investiment
        responseInvestiment = self.c.post('/investiments', {
            "code": "ITSA4",
            "rating" : 1,
            "currency": "R$",
            "payprice" : 5,
            "quantity" : 5,
            "action": "BUY",
            "transaction_date": "2022-11-11",
            "institution": self.institution.id,
            "type" : self.type.id
        }, HTTP_REFERER='/investiments')
        self.assertEqual(responseInvestiment.status_code, 302)
        self.investiment = Investiment.objects.get(code="ITSA4")

        #Update transaction
        responseTransaction = self.c.put('/transaction/1', json.dumps({
            "investiment": self.investiment.id,
            "action": "BUY",
            "payprice" : 10,
            "quantity" : 10,
            "transaction_date": "2022-11-12",
        }))
        self.assertEqual(responseTransaction.status_code, 204)

        investimentsResponse = self.c.get('/investiments')
        self.assertEqual(investimentsResponse.status_code, 200)

        self.assertEqual(investimentsResponse.context['portfolio'][0].total, 100)
        self.assertEqual(investimentsResponse.context['portfolio'][0].qnt, 10)
        self.assertEqual(investimentsResponse.context['portfolio'][0].position, 'BUY')

        transactionsResponse = self.c.get('/transactions')
        self.assertEqual(transactionsResponse.status_code, 200)
        self.assertEqual(len(transactionsResponse.context['transactions']), 1)

        #Cretae sell transaction lower than buy quantity, investiment continue BUY
        responseTransaction = self.c.post('/transactions', {
            "investiment": self.investiment.id,
            "action": "SELL",
            "payprice" : 10,
            "quantity" : 2,
            "transaction_date": "2022-11-12",
        }, HTTP_REFERER='/transactions')
        self.assertEqual(responseTransaction.status_code, 302)

        investimentsResponse = self.c.get('/investiments')
        self.assertEqual(investimentsResponse.status_code, 200)

        self.assertEqual(investimentsResponse.context['portfolio'][0].total, 80)
        self.assertEqual(investimentsResponse.context['portfolio'][0].qnt, 8)
        self.assertEqual(investimentsResponse.context['portfolio'][0].position, 'BUY')

        #Cretae sell transaction higher than buy quantity, investiment goes to SELL
        responseTransaction = self.c.post('/transactions', {
            "investiment": self.investiment.id,
            "action": "SELL",
            "payprice" : 10,
            "quantity" : 10,
            "transaction_date": "2022-11-12",
        }, HTTP_REFERER='/transactions')
        self.assertEqual(responseTransaction.status_code, 302)

        investimentsResponse = self.c.get('/investiments')
        self.assertEqual(investimentsResponse.status_code, 200)

        self.assertEqual(investimentsResponse.context['portfolio'][0].total, 20)
        self.assertEqual(investimentsResponse.context['portfolio'][0].qnt, 2)
        self.assertEqual(investimentsResponse.context['portfolio'][0].position, 'SELL')

        
        #Cant Delete transaction
        respondeDeleteTransaction = self.c.delete('/transaction/10')
        self.assertEqual(respondeDeleteTransaction.status_code, 404)

        #Delete transaction
        respondeDeleteTransaction = self.c.delete('/transaction/1')
        self.assertEqual(respondeDeleteTransaction.status_code, 201)

    #Update investiment expect return position NONE
    def test_update_investiment_to_none(self):
        # Login user
        self.c.login(username="test", password="test")

        #Create type
        self.type = Type.objects.create(user=self.user, typeName="TypeTest", percent=10, color="#ffffff")
        
        #Create institution
        self.institution = Institution.objects.create(user=self.user, name="Broker")

        # Create investiment
        responseInvestiment = self.c.post('/investiments', {
            "code": "ITSA4",
            "rating" : 1,
            "currency": "R$",
            "payprice" : 10,
            "quantity" : 10,
            "action": "BUY",
            "transaction_date": "2022-11-11",
            "institution": self.institution.id,
            "type" : self.type.id
        }, HTTP_REFERER='/investiments')
        self.assertEqual(responseInvestiment.status_code, 302)
        self.investiment = Investiment.objects.get(code="ITSA4")

        responseTransaction = self.c.post('/transactions', {
            "investiment": self.investiment.id,
            "action": "SELL",
            "payprice" : 10,
            "quantity" : 10,
            "transaction_date": "2022-11-12",
        }, HTTP_REFERER='/transactions')
        self.assertEqual(responseTransaction.status_code, 302)

        investimentsResponse = self.c.get('/investiments')
        self.assertEqual(investimentsResponse.status_code, 200)

        self.assertEqual(investimentsResponse.context['portfolio'][0].total, 100)
        self.assertEqual(investimentsResponse.context['portfolio'][0].qnt, 0)
        self.assertEqual(investimentsResponse.context['portfolio'][0].position, 'NONE')

    #Update investiments
    def test_update_investiments(self):
        # Login user
        self.c.login(username="test", password="test")

        #Create type
        self.type = Type.objects.create(user=self.user, typeName="TypeTest", percent=10, color="#ffffff")
        
        #Create institution
        self.institution = Institution.objects.create(user=self.user, name="Broker")

        # Create investiment
        responseInvestiment = self.c.post('/investiments', {
            "code": "ITSA4",
            "rating" : 1,
            "currency": "R$",
            "payprice" : 5,
            "quantity" : 5,
            "action": "BUY",
            "transaction_date": "2022-11-11",
            "institution": self.institution.id,
            "type" : self.type.id
        }, HTTP_REFERER='/investiments')
        self.assertEqual(responseInvestiment.status_code, 302)
        self.investiment = Investiment.objects.get(code="ITSA4")
        
        #Create new type
        self.newtype = Type.objects.create(user=self.user, typeName="TypeTest 2", percent=20, color="#ffffff")
        
        #Create new institution
        self.newinstitution = Institution.objects.create(user=self.user, name="Broker 2")

        #Cant Update investiment
        respondeEditInvestiment = self.c.put('/investiment/2', json.dumps({
            "rating" : 2,
            "institution": self.newinstitution.id,
            "type" : self.newtype.id
        }))
        self.assertEqual(respondeEditInvestiment.status_code, 404)

        #Update investiment
        respondeEditInvestiment = self.c.put('/investiment/1', json.dumps({
            "rating" : 2,
            "institution": self.newinstitution.id,
            "type" : self.newtype.id
        }))
        self.assertEqual(respondeEditInvestiment.status_code, 204)


        #Cant Delete investiment
        respondeDeleteInvestiment = self.c.delete('/investiment/2')
        self.assertEqual(respondeDeleteInvestiment.status_code, 404)

        #Delete investiment
        respondeDeleteInvestiment = self.c.delete('/investiment/1')
        self.assertEqual(respondeDeleteInvestiment.status_code, 201)
    
    #Creta a Goal
    def test_goal(self):
        # Login user
        self.c.login(username="test", password="test")

        # Post a goal
        response = self.c.post('/create_goal', {
            "value": 10000,
        }, HTTP_REFERER='/dashboard')

        self.assertEqual(Goal.objects.filter(value=10000).count(), 1)
        self.assertEqual(response.status_code, 200)

        # Cant Delete goal
        deleteResponse = self.c.delete('/goal/10', HTTP_REFERER='/dashboard')

        self.assertEqual(Goal.objects.all().count(), 1)
        self.assertEqual(deleteResponse.status_code, 404)

        # Delete goal
        deleteResponse = self.c.delete('/goal/1', HTTP_REFERER='/dashboard')

        self.assertEqual(Goal.objects.all().count(), 0)
        self.assertEqual(deleteResponse.status_code, 201)
