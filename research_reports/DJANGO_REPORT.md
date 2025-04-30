# Research Report

## Intro to Django

### Summary of Work

I researched how to use the Django framework to support the development of our Vending Machine CLI project. Specifically, I focused on setting up Django, connecting it to a MySQL database, and using Django Rest Framework (DRF) to create RESTful APIs. This will be essential for handling backend operations like inventory management, user transactions, and integrating with the Stripe API for payments.

### Motivation

Our project uses Django as the backend framework for the Vending Machine CLI. Django will allow us to build a scalable backend, manage inventory through MySQL, and handle credit card payments using the Stripe API. Additionally, Django Rest Framework (DRF) will help us create REST APIs that can efficiently handle user commands from the CLI. Learning how to integrate Django with MySQL and Stripe is critical for building a functional and secure system.

### Time Spent

- ~45 minutes installing Django and setting up the development environment
- ~2 hours following Django tutorials and reading official documentation
- ~1 hour researching Django Rest Framework (DRF) for RESTful API development
- ~30 minutes learning how to connect Django to a MySQL database

### Results

I started by setting up Django and connecting it to a virtual environment:

```shell
python -m venv venv
source venv/bin/activate
pip install django
```

Next, I initiated a new Django project:

```shell
django-admin startproject vending_machine
cd vending_machine
```

I then created an app within the project to handle core functionalities:

```shell
python manage.py startapp core
```

**Connecting Django to MySQL:**
I installed the required MySQL client:

```shell
pip install mysqlclient
```

I configured `settings.py` for MySQL:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'vending_machine_db',
        'USER': 'root',
        'PASSWORD': 'yourpassword',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}
```

**Creating Models:**
I defined models for `User`, `Snack`, and `Transaction` based on our ERD:

```python
from django.db import models

class User(models.Model):
    user_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    email = models.EmailField()
    payment_info = models.TextField()

class Snack(models.Model):
    snack_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=5, decimal_places=2)
    stock = models.IntegerField()

class Transaction(models.Model):
    transaction_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    snack = models.ForeignKey(Snack, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=5, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)
```

After defining the models, I ran migrations:

```shell
python manage.py makemigrations
python manage.py migrate
```

**Setting up Django Rest Framework:**
I installed DRF:

```shell
pip install djangorestframework
```

Added DRF to `INSTALLED_APPS` in `settings.py`:

```python
INSTALLED_APPS = [
    ...
    'rest_framework',
]
```

**Creating API Endpoints:**
I created serializers to convert model instances into JSON:

```python
from rest_framework import serializers
from .models import User, Snack, Transaction

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'

class SnackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Snack
        fields = '__all__'

class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = '__all__'
```

Created views using DRF's `ModelViewSet`:

```python
from rest_framework import viewsets
from .models import User, Snack, Transaction
from .serializers import UserSerializer, SnackSerializer, TransactionSerializer

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class SnackViewSet(viewsets.ModelViewSet):
    queryset = Snack.objects.all()
    serializer_class = SnackSerializer

class TransactionViewSet(viewsets.ModelViewSet):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
```

Set up URLs in `urls.py`:

```python
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from core import views

router = DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'snacks', views.SnackViewSet)
router.register(r'transactions', views.TransactionViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
]
```

### Sources

-Django Official Documentation[^1]
-Django Rest Framework Documentation[^2]
-Connecting Django to MySQL[^3]
-Stripe API Documentation[^4]
-Simple Django REST Framework Tutorial[^5]

[^1]https://docs.djangoproject.com/en/5.1/
[^2]https://www.django-rest-framework.org/
[^3]https://docs.djangoproject.com/en/5.1/ref/databases/#mysql-notes
[^4]https://docs.stripe.com/
[^5]https://www.django-rest-framework.org/tutorial/quickstart/
