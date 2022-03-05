from django.urls import path

from main.views import *

urlpatterns = [
    path('', index, name='index'),
    path('home/', home, name='home'),
    path('run-parser/', run_parser, name='run-parser'),
    path('stop-parser/', stop_parser, name='stop-parser'),
]
