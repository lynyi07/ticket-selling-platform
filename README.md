# Team Gryffindor Large Group project

## Team members
The members of the team are:
  * Lyn Yi Cheng
  * Simran Debnath
  * Daniel Holland
  * Brian Jalleh
  * Susetta James
  * Seohyun (Jen) Kwon
  * Jasdeep Panum
  * Erikas (Erik) Staugas
  * Yue (Michelle) Wang

  
## Project structure



## Deployed version of the application
The deployed version of the application can be found at https://bjalleh02.pythonanywhere.com/


## Installation instructions
To install the software and use it in your local development environment, you must first set up and activate a local development environment.  From the root of the project:

```
$ virtualenv venv
$ source venv/bin/activate
```

Install all required packages:

```
$ pip3 install -r requirements.txt
```

Migrate the database:

```
$ python3 manage.py migrate
```

Seed the development database with:

```
$ python3 manage.py seed
```

Run all tests with:
```
$ python3 manage.py test
```

*The above instructions should work in your version of the application.  If there are deviations, declare those here in bold.  Otherwise, remove this line.*


## Sources
The packages used by this application are specified in `requirements.txt`


Task:
Source 

Navbar:
https://getbootstrap.com/docs/4.0/components/navbar/ 

Clearcache command:
https://stackoverflow.com/questions/5942759/best-place-to-clear-cache-when-restarting-django-server

Emails:
https://stackoverflow.com/questions/33054658/django-sending-emails-with-links 

Scroll Animation:
https://www.youtube.com/watch?v=T33NN_pPeNI 

Slide Show Animation:
https://www.youtube.com/watch?v=qDww4CbxtD4&t=185s 

CSS: 
https://getbootstrap.com/docs/4.0/getting-started/introduction/

Test Checkout View and Test Payout View: test with mock objects :
https://docs.python.org/3/library/unittest.mock.html#patch 
https://docs.python.org/3/library/unittest.mock.html#unittest.mock.MagicMock 

Checkout View: handle Stripe errors:
https://stripe.com/docs/api/errors/handling  

Create Stripe customer and retrieve Stripe customer:
https://stripe.com/docs/api/customers/create  

Attach payment method to customer:
https://stripe.com/docs/api/payment_methods/attach  

Modify Stripe customer:
https://stripe.com/docs/api/customers/update  

Create a payment method using JS; Initial payout:
https://stripe.com/docs/payments/accept-a-payment-synchronously?locale=en-GB  

Retrieve payment method:
https://stripe.com/docs/api/payment_methods/retrieve?lang=python 

User Registration Email:
https://pylessons.com/django-email-confirm


## Access credentials

Student Account: 
- Email: joe.doe@kcl.ac.uk 
- Password: Password123 
- (Better to use actual email to receive emails) 

Society Account: 
- Email: robotics@kcl.ac.uk 
- Password: Password123 

Student Union Account: 
- Username: kclsu@kcl.ac.uk 
- Password: Password123


## Important
Our reports contain the following:
- What the application can and can't do for each account
- The code coverage
- The relevant details to check the functionality
- Set up instructions
