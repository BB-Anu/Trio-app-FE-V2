import time
from django.http import HttpResponse
from .models import *
from datetime import datetime
from django.shortcuts import render, redirect


class MiddlewareExecutionStart(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # This is where request pre-processing can happen if needed
        response = self.get_response(request)
        # This is where post-processing can happen if needed
        return response
    
    def process_exception(self,request,exception):
        return render(request,'error.html',{'error':exception})