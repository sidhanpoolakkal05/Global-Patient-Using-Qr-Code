from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse
from .models import User, Doctor, Hospital

# Create your views here.

