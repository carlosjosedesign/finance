from django.urls import path
from django.conf import settings
from . import views

app_name = "finance"

urlpatterns = [
    path("", views.index, name="index"),
    path("investiments", views.investiments, name="investiments"),
    path("investiment/<int:id>", views.investiment, name="investiment"),
    path("transactions", views.transactions, name="transactions"),
    path("transaction/<int:id>", views.transaction, name="transaction"),
    path("institutions", views.institutions, name="institutions"),
    path("institution/<int:id>", views.institution, name="institution"),
    path("create_type", views.create_type, name="create_type"),
    path("type/<int:id>", views.type, name="type"),
    path("create_goal", views.create_goal, name="create_goal"),
    path("goal/<int:id>", views.goal, name="goal"),
    path("get-prices", views.getPrices, name="get-prices"),
    path("get-price/<str:code>", views.getPrice, name="get-price"),
    path("setCurrency", views.setCurrency, name="setCurrency"),
    path("setTheme", views.setTheme, name="setTheme"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
]
