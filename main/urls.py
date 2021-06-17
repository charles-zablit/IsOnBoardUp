from django.contrib import admin
from django.urls import path, include
from .views import *

urlpatterns = [
		path('', MainView),
		path('data/<int:request_length>/', get_data)
]