
from django.contrib import admin
from django.urls import path,include
from . import views

urlpatterns = [
    path("",views.home,name="dashboard"),
    # path("dashboard",views.dashboard,name="dashboard"),
    path("login",views.user_login,name="login"),
    path("logout",views.user_logout,name="logout"),
    path("report",views.report_view,name='report'),
    path('bill',views.bill,name="category"),
]
