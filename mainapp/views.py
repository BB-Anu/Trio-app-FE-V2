from django.http import JsonResponse
from django.shortcuts import render,redirect,get_object_or_404
from django.views.generic import ListView, UpdateView, CreateView, DetailView

from user_management.forms import BranchForm, CompanyForm
from .api_call import call_post_method_without_token_app_builder,call_get_method,call_get_method_without_token,call_post_with_method,call_post_method_for_without_token,call_delete_method,call_delete_method_without_token, call_put_method,call_put_method_without_token
import requests
import json
from django.contrib import messages
from django.urls import resolve, reverse
import jwt
from django.contrib.auth import logout
from django.http.request import HttpRequest
from django.http.response import HttpResponseRedirect, HttpResponse
from django.contrib import messages
from .forms import *
from rest_framework import status
from rest_framework.response import Response
from django.contrib import messages
from django.conf import settings
from .api_call import *

BASEURL = 'http://127.0.0.1:9000/'
APP_BUILDER = 'http://127.0.0.1:8000/'

def dashboard(request):
    user_token=request.session['user_token']
    endpoint = 'dashboard/'
        # getting data from backend
    records_response = call_get_method(BASEURL,endpoint,user_token)
    if records_response.status_code not in [200,201]:
            messages.error(request, f"Failed to fetch records. {records_response.json()}", extra_tags="warning")
    else:
            records = records_response.json()
            print('records',records)
            # You can pass 'records' to your template for rendering
            context = {'records': records}
            return render(request, 'dashboard.html', context)
    
    return render(request, 'dashboard.html')

def customer_Screen(request):
    user_token = request.session.get('user_token')
    pk=request.session['user_data']['id']
    print(request.session['user_data'])
    print('pk',pk)
    endpoint = f'customer_screen/{pk}/'
    records_response = call_get_method(BASEURL, endpoint, user_token)
    print('-records_response-',records_response)
    if records_response.status_code in [200, 201]:
        records = records_response.json()
        return render(request, 'customer_Screen.html', {'records': records})
    else:
        messages.error(request, f"Failed to fetch records. {records_response.json()}", extra_tags="warning")
        return render(request, 'customer_Screen.html')




def user_dashboard(request):
    user_token=request.session['user_token']
    endpoint = 'user_dashboard/'
        # getting data from backend
    records_response = call_get_method(BASEURL,endpoint,user_token)
    if records_response.status_code not in [200,201]:
            messages.error(request, f"Failed to fetch records. {records_response.json()}", extra_tags="warning")
    else:
            records = records_response.json()
            # You can pass 'records' to your template for rendering
            context = {'records': records}
            return render(request, 'user_dashboard.html', context)
    return render(request, 'user_dashboard.html')


def setup(request):
    endpoint = 'project_setups/'
    endpoint1 = 'set_up'
    json_data = settings.PROJECT_ID # value is 32
    json_data = {"project_id": settings.PROJECT_ID}
    json_body = json.dumps(json_data)
    appbuilder_response = call_post_method_for_without_token(APP_BUILDER,endpoint,json_body)
    if appbuilder_response.status_code == 201:
        #save all usertype and other table data to new project 
        dic = {}
        records1 = appbuilder_response.json() # all table data structure is [ [{table1},{}],[{table2},{}] ]
        for index,data in enumerate(records1):
            if index == 0:
                dic["usertype"] = data
            elif index == 1:
                dic["screentable"] = data
            elif index == 2:
                dic["screenversion"] = data  

        alltable_data = json.dumps(dic)
        response1 = call_post_method_for_without_token(BASEURL, endpoint1, alltable_data)
        if response1.status_code == 201:
            messages.success(request,'Your System Successfully Setup', extra_tags="success")
        else:
            print("error",response1.json())
            # return redirect('setup')    
    else:
        print("error")
    
    return redirect("dashboard")



def login(request):
    try:
        # Check if the request method is POST
        if request.method == "POST":
            email = request.POST.get('email')
            password = request.POST.get('password')
            payload = {        
                "username" : email,
                "password" : password
            }
            # Convert payload to JSON format
            json_payload = json.dumps(payload)
            print('json_payload',json_payload)
            ENDPOINT = 'api/token/'
            login_response = call_post_method_for_without_token(BASEURL,ENDPOINT,json_payload)
            print('login_response',login_response)
            print('login_response',login_response.json())
            if login_response.status_code == 200:
                login_tokes = login_response.json()
                print('-----',login_tokes)
                request.session['user_token']=login_tokes['access']
                request.session['user_data']=login_tokes['user_data']
                user_id=request.session['user_data']['id']
                request.session['branch']=request.session['user_data']['branch']
                permission=login_tokes['permission']
                permission_list=[]
                for data in permission:
                    permission_list.append(data['function_name'])
                request.session['permission']=permission_list
                print("user_id+++",user_id)
                # if request.session['user_data']['roles']['name'] == 'customer':
                #     return redirect('customer_Screen')
                if request.session['user_data']['is_superuser'] == True:
                    return redirect('select_company')
                elif request.session['user_data']['is_admin']==True:
                    company_id=request.session['user_data']['branch']
                    print('===company==id',company_id)
                    endpoint2=f'UserManagement/company/{company_id}'    
                    records_response2 = call_get_method_without_token(BASEURL,endpoint2)
                    print('records_response.status_code',records_response2.status_code)
                    if records_response2.status_code not in [200,201]:
                        messages.error(request, f"Failed to fetch records. {records_response2.json()}", extra_tags="warning")
                    else:
                        company = records_response2.json()
                        print('----',company )
                    request.session['company']=company_id
                    if company_id is not None:
                        return redirect('select_branch', pk=company_id)
                    else:
                        return redirect('user_dashboard')   
                else:
                    print('===request.session',request.session['user_data']['roles'])
                    request.session['branch']=request.session['user_data']['branch']

                    return redirect('user_dashboard')

            else:
                login_tokes = login_response.json()
                login_error='Invalid Username and Password'
                context={"login_error":login_error}
                return render(request, 'login.html',context)
          
        return render(request, 'login.html')
    except Exception as error:
        return HttpResponse(f'<h1>{error}</h1>')


# create and view table function
def clientprofile(request):
    user_token=request.session['user_token']
    endpoint2='customer_user/'    
    records_response2 = call_get_method(BASEURL,endpoint2,user_token)
    print('records_response.status_code',records_response2.status_code)
    if records_response2.status_code not in [200,201]:
        messages.error(request, f"Failed to fetch records. {records_response2.json()}", extra_tags="warning")
    else:
        users = records_response2.json()
    form=ClientProfileForm(user_choices=users)
    endpoint = 'clientprofile/'
  
    if request.method=="POST":
        form=ClientProfileForm(request.POST,files=request.FILES,user_choices=users)
        if form.is_valid():
            Output = form.cleaned_data
            Output['branch']=request.session['branch']
            Output['created_by']=request.session['user_data']['id']

            for field_name, field in form.fields.items():
                if isinstance(field.widget, forms.DateInput) or isinstance(field, forms.DateField) or isinstance(field, forms.DateTimeField)  or isinstance(field, forms.DecimalField):
                    if Output[field_name]:
                        del Output[field_name]
                        Output[field_name] = request.POST.get(field_name)
                cleaned_data = form.cleaned_data
                files, cleaned_data = image_filescreate(cleaned_data)
                json_data = cleaned_data if files else json.dumps(cleaned_data)
                print('==json_data==,',json_data)
                response = call_post_method_with_token_v2(BASEURL,endpoint,json_data,files)

                print('==response==',response)
                if response['status_code'] == 1:
                    print("error",response)
                    return redirect('clientprofile_list')

                else:
                    messages.success(request,'Data Successfully Saved', extra_tags="success")
                    return redirect('clientprofile_list')
    else:
        print('errorss',form.errors)
    try:
        # getting data from backend
        records_response = call_get_method(BASEURL,endpoint,user_token)
        if records_response.status_code not in [200,201]:
            messages.error(request, f"Failed to fetch records. {records_response.json()}", extra_tags="warning")
        else:
            records = records_response.json()
            # You can pass 'records' to your template for rendering
            context = {'form': form, 'records': records}
            return render(request, 'clientprofile.html', context)
    except Exception as e:
        print("An error occurred: Expecting value: line 1 column 1 (char 0)")
    context={
        'form':form,
    }
    return render(request,'clientprofile.html',context)

def clientprofile_list(request):
    user_token=request.session['user_token']
    endpoint = 'clientprofile/'
        # getting data from backend
    records_response = call_get_method(BASEURL,endpoint,user_token)
    if records_response.status_code not in [200,201]:
            messages.error(request, f"Failed to fetch records. {records_response.json()}", extra_tags="warning")
    else:
            records = records_response.json()
            # You can pass 'records' to your template for rendering
            context = {'records': records}
            return render(request, 'clientprofile_list.html', context)
    return render(request,'clientprofile_list.html',context)

# edit function
def clientprofile_edit(request,pk):
    user_token=request.session['user_token']
    endpoint2='customer_user/'    
    records_response2 = call_get_method(BASEURL,endpoint2,user_token)

    print('records_response.status_code',records_response2.status_code)
    if records_response2.status_code not in [200,201]:
        messages.error(request, f"Failed to fetch records. {records_response2.json()}", extra_tags="warning")
    else:
        users = records_response2.json()
    clientprofile = call_get_method(BASEURL, f'clientprofile/{pk}/',user_token)
    
    if clientprofile.status_code in [200,201]:
        clientprofile_data = clientprofile.json()
        print('------',clientprofile)

    else:
        print('error------',clientprofile)
        messages.error(request, 'Failed to retrieve data for clientprofile. Please check your connection and try again.', extra_tags='warning')
        return redirect('clientprofile')

    if request.method=="POST":
        form=ClientProfileForm(request.POST,request.FILES,user_choices=users, initial=clientprofile_data)
        if form.is_valid():
            updated_data = form.cleaned_data
            updated_data['branch']=request.session['branch']
            updated_data['updated_by']=request.session['user_data']['id']

            for field_name, field in form.fields.items():
                if isinstance(field.widget, forms.DateInput) or isinstance(field, forms.DateField) or isinstance(field, forms.DateTimeField) or isinstance(field, forms.DecimalField):
                    if updated_data[field_name]:
                        del updated_data[field_name]
                        updated_data[field_name] = request.POST.get(field_name)
            # Serialize the updated data as JSON
                cleaned_data = form.cleaned_data
                files, cleaned_data = image_filescreate(cleaned_data)
                json_data = cleaned_data if files else json.dumps(cleaned_data)
                print('==json_data==,',json_data)
            response = call_put_method_without_token(BASEURL, f'clientprofile/{pk}/', json_data)

            if response.status_code in [200,201]: 
                messages.success(request, 'Your data has been successfully saved', extra_tags='success')
                return redirect('clientprofile') 
            else:
                error_message = response.json()
                messages.error(request, f"Oops..! {error_message}", extra_tags='warning')
        else:
            print("An error occurred: Expecting value: line 1 column 1 (char 0)")
    else:
        form = ClientProfileForm(initial=clientprofile_data,user_choices=users)

    context={
        'form':form,
    }
    return render(request,'clientprofile_edit.html',context)

def clientprofile_delete(request,pk):
    user_token=request.session['user_token']
    end_point = f'clientprofile/{pk}/'
    clientprofile = call_delete_method(BASEURL, end_point,user_token)
    if clientprofile.status_code not in [200,201]:
        messages.error(request, 'Failed to delete data for clientprofile. Please try again.', extra_tags='warning')
        return redirect('clientprofile_list')
    else:
        messages.success(request, 'Successfully deleted data for clientprofile', extra_tags='success')
        return redirect('clientprofile-list')

# create and view table function
def documentgroup(request):
    form=DocumentGroupForm()
    # user_id=request.session['user_data']['id']
    # print("user_id",user_id)
    user_token=request.session['user_token']

    endpoint = 'documentgroup/'
    if request.method=="POST":
        form=DocumentGroupForm(request.POST)
        if form.is_valid():
            Output = form.cleaned_data
            Output['branch']=request.session['branch']
            Output['created_by']=request.session['user_data']['id']

            # Output['created_by']=user_id
            for field_name, field in form.fields.items():
                if isinstance(field.widget, forms.DateInput) or isinstance(field, forms.DateField) or isinstance(field, forms.DateTimeField):
                    if Output[field_name]:
                        del Output[field_name]
                        Output[field_name] = request.POST.get(field_name)
            json_data=json.dumps(Output)
            response = call_post_method_for_without_token(BASEURL,endpoint,json_data)
            if response.status_code not in [200,201]:
                print("error",response)
            else:
                messages.success(request,'Data Successfully Saved', extra_tags="success")
                return redirect('documentgroup_list')
    else:
        print('errorss',form.errors)
    try:
        # getting data from backend
        records_response = call_get_method(BASEURL,endpoint,user_token)
        if records_response.status_code not in [200,201]:
            messages.error(request, f"Failed to fetch records. {records_response.json()}", extra_tags="warning")
        else:
            records = records_response.json()
            # You can pass 'records' to your template for rendering
            context = {'form': form, 'records': records}
            return render(request, 'documentgroup.html', context)
    except Exception as e:
        print("An error occurred: Expecting value: line 1 column 1 (char 0)")
    context={
        'form':form,
    }
    return render(request,'documentgroup.html',context)

def documentgroup_list(request):
    user_token=request.session['user_token']
    endpoint = 'documentgroup/'
        # getting data from backend
    records_response = call_get_method_without_token(BASEURL,endpoint)
    if records_response.status_code not in [200,201]:
            messages.error(request, f"Failed to fetch records. {records_response.json()}", extra_tags="warning")
    else:
            records = records_response.json()
            # You can pass 'records' to your template for rendering
            context = {'records': records}
            return render(request, 'documentgroup_list.html', context)
    return render(request,'documentgroup_list.html',context)
# edit function
def documentgroup_edit(request,pk):
    documentgroup = call_get_method_without_token(BASEURL, f'documentgroup/{pk}/')
    
    if documentgroup.status_code in [200,201]:
        documentgroup_data = documentgroup.json()
    else:
        print('error------',documentgroup)
        messages.error(request, 'Failed to retrieve data for documentgroup. Please check your connection and try again.', extra_tags='warning')
        return redirect('documentgroup')

    if request.method=="POST":
        form=DocumentGroupForm(request.POST, initial=documentgroup_data)
        if form.is_valid():
            updated_data = form.cleaned_data
            updated_data['branch']=request.session['branch']
            updated_data['updated_by']=request.session['user_data']['id']

            for field_name, field in form.fields.items():
                if isinstance(field.widget, forms.DateInput) or isinstance(field, forms.DateField) or isinstance(field, forms.DateTimeField):
                    if updated_data[field_name]:
                        del updated_data[field_name]
                        updated_data[field_name] = request.POST.get(field_name)
            # Serialize the updated data as JSON
            json_data = json.dumps(updated_data)
            response = call_put_method_without_token(BASEURL, f'documentgroup/{pk}/', json_data)

            if response.status_code in [200,201]: 
                messages.success(request, 'Your data has been successfully saved', extra_tags='success')
                return redirect('documentgroup') 
            else:
                error_message = response.json()
                messages.error(request, f"Oops..! {error_message}", extra_tags='warning')
        else:
            print("An error occurred: Expecting value: line 1 column 1 (char 0)")
    else:
        form = DocumentGroupForm(initial=documentgroup_data)

    context={
        'form':form,
    }
    return render(request,'documentgroup_edit.html',context)

def documentgroup_delete(request,pk):
    end_point = f'documentgroup/{pk}/'
    documentgroup = call_delete_method_without_token(BASEURL, end_point)
    if documentgroup.status_code not in [200,201]:
        messages.error(request, 'Failed to delete data for documentgroup. Please try again.', extra_tags='warning')
        return redirect('documentgroup')
    else:
        messages.success(request, 'Successfully deleted data for documentgroup', extra_tags='success')
        return redirect('documentgroup')

# create and view table function
def customdocumententity(request):
    user_token=request.session['user_token']

    form=CustomDocumentEntityForm()
    endpoint = 'customdocumententity/'
    if request.method=="POST":
        form=CustomDocumentEntityForm(request.POST)
        if form.is_valid():
            Output = form.cleaned_data
            Output['branch']=request.session['branch']
            Output['created_by']=request.session['user_data']['id']

            for field_name, field in form.fields.items():
                if isinstance(field.widget, forms.DateInput) or isinstance(field, forms.DateField) or isinstance(field, forms.DateTimeField):
                    if Output[field_name]:
                        del Output[field_name]
                        Output[field_name] = request.POST.get(field_name)
            json_data=json.dumps(Output)
            response = call_post_method_for_without_token(BASEURL,endpoint,json_data)
            if response.status_code not in [200,201]:
                print("error",response)
            else:
                messages.success(request,'Data Successfully Saved', extra_tags="success")
                return redirect('customdocumententity_list')
    else:
        print('errorss',form.errors)
    try:
        # getting data from backend
        records_response = call_get_method(BASEURL,endpoint,user_token)
        if records_response.status_code not in [200,201]:
            messages.error(request, f"Failed to fetch records. {records_response.json()}", extra_tags="warning")
        else:
            records = records_response.json()
            # You can pass 'records' to your template for rendering
            context = {'form': form, 'records': records}
            return render(request, 'customdocumententity.html', context)
    except Exception as e:
        print("An error occurred: Expecting value: line 1 column 1 (char 0)")
    context={
        'form':form,
    }
    return render(request,'customdocumententity.html',context)

def customdocumententity_list(request):
    user_token=request.session['user_token']
    endpoint = 'customdocumententity/'
        # getting data from backend
    records_response = call_get_method(BASEURL,endpoint,user_token)
    if records_response.status_code not in [200,201]:
            messages.error(request, f"Failed to fetch records. {records_response.json()}", extra_tags="warning")
    else:
            records = records_response.json()
            # You can pass 'records' to your template for rendering
            context = {'records': records}
            return render(request, 'customdocumententity_list.html', context)
    return render(request,'customdocumententity_list.html',context)

# edit function
def customdocumententity_edit(request,pk):
    user_token=request.session['user_token']

    customdocumententity = call_get_method(BASEURL, f'customdocumententity/{pk}/',user_token)
    
    if customdocumententity.status_code in [200,201]:
        customdocumententity_data = customdocumententity.json()
    else:
        print('error------',customdocumententity)
        messages.error(request, 'Failed to retrieve data for customdocumententity. Please check your connection and try again.', extra_tags='warning')
        return redirect('customdocumententity_list')

    if request.method=="POST":
        form=CustomDocumentEntityForm(request.POST, initial=customdocumententity_data)
        if form.is_valid():
            updated_data = form.cleaned_data
            updated_data['branch']=request.session['branch']
            updated_data['updated_by']=request.session['user_data']['id']
            for field_name, field in form.fields.items():
                if isinstance(field.widget, forms.DateInput) or isinstance(field, forms.DateField) or isinstance(field, forms.DateTimeField):
                    if updated_data[field_name]:
                        del updated_data[field_name]
                        updated_data[field_name] = request.POST.get(field_name)
            # Serialize the updated data as JSON
            json_data = json.dumps(updated_data)
            response = call_put_method_without_token(BASEURL, f'customdocumententity/{pk}/', json_data)

            if response.status_code in [200,201]: 
                messages.success(request, 'Your data has been successfully saved', extra_tags='success')
                return redirect('customdocumententity_list') 
            else:
                error_message = response.json()
                messages.error(request, f"Oops..! {error_message}", extra_tags='warning')
        else:
            print("An error occurred: Expecting value: line 1 column 1 (char 0)")
    else:
        form = CustomDocumentEntityForm(initial=customdocumententity_data)

    context={
        'form':form,
    }
    return render(request,'customdocumententity_edit.html',context)

def customdocumententity_delete(request,pk):
    end_point = f'customdocumententity/{pk}/'
    customdocumententity = call_delete_method_without_token(BASEURL, end_point)
    if customdocumententity.status_code not in [200,201]:
        messages.error(request, 'Failed to delete data for customdocumententity. Please try again.', extra_tags='warning')
        return redirect('customdocumententity_list')
    else:
        messages.success(request, 'Successfully deleted data for customdocumententity', extra_tags='success')
        return redirect('customdocumententity_list')

# create and view table function
def tasktemplate(request):
    user_token=request.session['user_token']
    form=TaskTemplateForm()
    endpoint = 'tasktemplate/'
    if request.method=="POST":
        form=TaskTemplateForm(request.POST)
        if form.is_valid():
            Output = form.cleaned_data
            Output['branch']=request.session['branch']
            Output['created_by']=request.session['user_data']['id']

            for field_name, field in form.fields.items():
                if isinstance(field.widget, forms.DateInput) or isinstance(field, forms.DateField) or isinstance(field, forms.DateTimeField):
                    if Output[field_name]:
                        del Output[field_name]
                        Output[field_name] = request.POST.get(field_name)
            json_data=json.dumps(Output)
            response = call_post_method_for_without_token(BASEURL,endpoint,json_data)
            if response.status_code not in [200,201]:
                print("error",response)
            else:
                messages.success(request,'Data Successfully Saved', extra_tags="success")
                return redirect('tasktemplate_list')
    else:
        print('errorss',form.errors)
    try:
        # getting data from backend
        records_response = call_get_method(BASEURL,endpoint,user_token)
        if records_response.status_code not in [200,201]:
            messages.error(request, f"Failed to fetch records. {records_response.json()}", extra_tags="warning")
        else:
            records = records_response.json()
            # You can pass 'records' to your template for rendering
            context = {'form': form, 'records': records}
            return render(request, 'tasktemplate.html', context)
    except Exception as e:
        print("An error occurred: Expecting value: line 1 column 1 (char 0)")
    context={
        'form':form,
    }
    return render(request,'tasktemplate.html',context)

def tasktemplate_list(request):
    user_token=request.session['user_token']
    endpoint = 'tasktemplate/'
        # getting data from backend
    records_response = call_get_method_without_token(BASEURL,endpoint)
    if records_response.status_code not in [200,201]:
            messages.error(request, f"Failed to fetch records. {records_response.json()}", extra_tags="warning")
    else:
            records = records_response.json()
            # You can pass 'records' to your template for rendering
            context = {'records': records}
            return render(request, 'tasktemplate_list.html', context)
    return render(request,'tasktemplate_list.html',context)

# edit function
def tasktemplate_edit(request,pk):
    tasktemplate = call_get_method_without_token(BASEURL, f'tasktemplate/{pk}/')
    
    if tasktemplate.status_code in [200,201]:
        tasktemplate_data = tasktemplate.json()
    else:
        print('error------',tasktemplate)
        messages.error(request, 'Failed to retrieve data for tasktemplate. Please check your connection and try again.', extra_tags='warning')
        return redirect('tasktemplate')

    if request.method=="POST":
        form=TaskTemplateForm(request.POST, initial=tasktemplate_data)
        if form.is_valid():
            updated_data = form.cleaned_data
            updated_data['branch']=request.session['branch']
            updated_data['updated_by']=request.session['user_data']['id']

            for field_name, field in form.fields.items():
                if isinstance(field.widget, forms.DateInput) or isinstance(field, forms.DateField) or isinstance(field, forms.DateTimeField):
                    if updated_data[field_name]:
                        del updated_data[field_name]
                        updated_data[field_name] = request.POST.get(field_name)
            # Serialize the updated data as JSON
            json_data = json.dumps(updated_data)
            response = call_put_method_without_token(BASEURL, f'tasktemplate/{pk}/', json_data)

            if response.status_code in [200,201]: 
                messages.success(request, 'Your data has been successfully saved', extra_tags='success')
                return redirect('tasktemplate') 
            else:
                error_message = response.json()
                messages.error(request, f"Oops..! {error_message}", extra_tags='warning')
        else:
            print("An error occurred: Expecting value: line 1 column 1 (char 0)")
    else:
        form = TaskTemplateForm(initial=tasktemplate_data)

    context={
        'form':form,
    }
    return render(request,'tasktemplate_edit.html',context)

def tasktemplate_delete(request,pk):
    end_point = f'tasktemplate/{pk}/'
    tasktemplate = call_delete_method_without_token(BASEURL, end_point)
    if tasktemplate.status_code not in [200,201]:
        messages.error(request, 'Failed to delete data for tasktemplate. Please try again.', extra_tags='warning')
        return redirect('tasktemplate')
    else:
        messages.success(request, 'Successfully deleted data for tasktemplate', extra_tags='success')
        return redirect('tasktemplate')

# create and view table function
def triogroup(request):
    user_token=request.session['user_token']
    form=TRIOGroupForm()
    endpoint = 'triogroup/'
    if request.method=="POST":
        form=TRIOGroupForm(request.POST)
        if form.is_valid():
            Output = form.cleaned_data
            Output['branch']=request.session['branch']
            Output['created_by']=request.session['user_data']['id']
            for field_name, field in form.fields.items():
                if isinstance(field.widget, forms.DateInput) or isinstance(field, forms.DateField) or isinstance(field, forms.DateTimeField):
                    if Output[field_name]:
                        del Output[field_name]
                        Output[field_name] = request.POST.get(field_name)
            json_data=json.dumps(Output)
            response = call_post_method_for_without_token(BASEURL,endpoint,json_data)
            if response.status_code not in [200,201]:
                print("error",response)
            else:
                messages.success(request,'Data Successfully Saved', extra_tags="success")
                return redirect('triogroup_list')
    else:
        print('errorss',form.errors)
    try:
        # getting data from backend
        records_response = call_get_method(BASEURL,endpoint,user_token)
        if records_response.status_code not in [200,201]:
            messages.error(request, f"Failed to fetch records. {records_response.json()}", extra_tags="warning")
        else:
            records = records_response.json()
            # You can pass 'records' to your template for rendering
            context = {'form': form, 'records': records}
            return render(request, 'triogroup.html', context)
    except Exception as e:
        print("An error occurred: Expecting value: line 1 column 1 (char 0)")
    context={
        'form':form,
    }
    return render(request,'triogroup.html',context)

def triogroup_list(request):
    user_token=request.session['user_token']
    endpoint = 'triogroup/'
        # getting data from backend
    records_response = call_get_method(BASEURL,endpoint,user_token)
    if records_response.status_code not in [200,201]:
            messages.error(request, f"Failed to fetch records. {records_response.json()}", extra_tags="warning")
    else:
            records = records_response.json()
            # You can pass 'records' to your template for rendering
            context = {'records': records}
            return render(request, 'triogroup_list.html', context)
    return render(request,'triogroup_list.html',context)


# edit function
def triogroup_edit(request,pk):
    triogroup = call_get_method_without_token(BASEURL, f'triogroup/{pk}/')
    
    if triogroup.status_code in [200,201]:
        triogroup_data = triogroup.json()
    else:
        print('error------',triogroup)
        messages.error(request, 'Failed to retrieve data for triogroup. Please check your connection and try again.', extra_tags='warning')
        return redirect('triogroup')

    if request.method=="POST":
        form=TRIOGroupForm(request.POST, initial=triogroup_data)
        if form.is_valid():
            updated_data = form.cleaned_data
            updated_data['branch']=request.session['branch']
            updated_data['updated_by']=request.session['user_data']['id']

            for field_name, field in form.fields.items():
                if isinstance(field.widget, forms.DateInput) or isinstance(field, forms.DateField) or isinstance(field, forms.DateTimeField):
                    if updated_data[field_name]:
                        del updated_data[field_name]
                        updated_data[field_name] = request.POST.get(field_name)
            # Serialize the updated data as JSON
            json_data = json.dumps(updated_data)
            response = call_put_method_without_token(BASEURL, f'triogroup/{pk}/', json_data)

            if response.status_code in [200,201]: 
                messages.success(request, 'Your data has been successfully saved', extra_tags='success')
                return redirect('triogroup_list') 
            else:
                error_message = response.json()
                messages.error(request, f"Oops..! {error_message}", extra_tags='warning')
        else:
            print("An error occurred: Expecting value: line 1 column 1 (char 0)")
    else:
        form = TRIOGroupForm(initial=triogroup_data)

    context={
        'form':form,
    }
    return render(request,'triogroup_edit.html',context)

def triogroup_delete(request,pk):
    end_point = f'triogroup/{pk}/'
    triogroup = call_delete_method_without_token(BASEURL, end_point)
    if triogroup.status_code not in [200,201]:
        messages.error(request, 'Failed to delete data for triogroup. Please try again.', extra_tags='warning')
        return redirect('triogroup')
    else:
        messages.success(request, 'Successfully deleted data for triogroup', extra_tags='success')
        return redirect('triogroup')

# create and view table function
def loancase(request):
    user_token=request.session['user_token']

    endpoint2='clientprofile/'    
    records_response2 = call_get_method(BASEURL,endpoint2,user_token)
    print('records_response.status_code',records_response2.status_code)
    if records_response2.status_code not in [200,201]:
        messages.error(request, f"Failed to fetch records. {records_response2.json()}", extra_tags="warning")
    else:
        client_choice = records_response2.json()
        print('client_choices',client_choice)
    form=LoanCaseForm(client_choices=client_choice)
    endpoint = 'loancase/'
    if request.method=="POST":
        form=LoanCaseForm(request.POST,client_choices=client_choice)
        if form.is_valid():
            Output = form.cleaned_data
            Output['branch']=request.session['branch']
            Output['created_by']=request.session['user_data']['id']

            for field_name, field in form.fields.items():
                if isinstance(field.widget, forms.DateInput) or isinstance(field, forms.DateField) or isinstance(field, forms.DateTimeField) or isinstance(field, forms.DecimalField):
                    if Output[field_name]:
                        del Output[field_name]
                        Output[field_name] = request.POST.get(field_name)
            json_data=json.dumps(Output)
            response = call_post_method_for_without_token(BASEURL,endpoint,json_data)
            if response.status_code not in [200,201]:
                print("error",response)
            else:
                messages.success(request,'Data Successfully Saved', extra_tags="success")
                return redirect('loancase_list')
    else:
        print('errorss',form.errors)
    # try:
    #     # getting data from backend
    #     records_response = call_get_method_without_token(BASEURL,endpoint,user_token)
    #     if records_response.status_code not in [200,201]:
    #         messages.error(request, f"Failed to fetch records. {records_response.json()}", extra_tags="warning")
    #     else:
    #         records = records_response.json()
    #         # You can pass 'records' to your template for rendering
    #         context = {'form': form, 'records': records}
    #         return render(request, 'loancase.html', context)
    # except Exception as e:
    #     print("An error occurred: Expecting value: line 1 column 1 (char 0)")
    context={
        'form':form,'screen_name':'Loan Case'
    }
    return render(request,'loancase.html',context)

def appproved_loancase_list(request):
    user_token=request.session['user_token']
    endpoint = 'approved_loancase/'
        # getting data from backend
    records_response = call_get_method(BASEURL,endpoint,user_token)
    if records_response.status_code not in [200,201]:
            messages.error(request, f"Failed to fetch records. {records_response.json()}", extra_tags="warning")
    else:
            records = records_response.json()
            print('rec---',records)
            # You can pass 'records' to your template for rendering
            context = {'records': records,'screen_name':'Approved Loans List'}
            return render(request, 'approved_loancase_list.html', context)
    return render(request,'approved_loancase_list.html',context)



def loancase_list(request):
    user_token=request.session['user_token']
    endpoint = 'loancase/'
        # getting data from backend
    records_response = call_get_method(BASEURL,endpoint,user_token)
    if records_response.status_code not in [200,201]:
            messages.error(request, f"Failed to fetch records. {records_response.json()}", extra_tags="warning")
    else:
            records = records_response.json()
            print('rec---',records)
            # You can pass 'records' to your template for rendering
            context = {'records': records,'screen_name':'Loan Case List'}
            return render(request, 'loancase_list.html', context)
    return render(request,'loancase_list.html',context)

def loancase_details(request, pk):
    user_token = request.session['user_token']
    endpoint = f'loancase_detail/{pk}'

    # Getting data from backend
    records_response = call_get_method(BASEURL, endpoint, user_token)

    if records_response.status_code not in [200, 201]:
        messages.error(request, f"Failed to fetch records. {records_response.json()}", extra_tags="warning")
        return render(request, 'loancase_detail.html', {'screen_name': 'Loan Case Detail'})
    else:
        records = records_response.json()
        print('---records',records)
        case = records.get('case', {})
        print('case', case)
        assignment = records.get('assignment', {})
        print('assignment', assignment)
        documents = records.get('docs', [])
        print('documents', documents)
        timesheets = records.get('timesheet', [])
        print('timesheets', timesheets)
        due_date = records.get('due_date', [])
        print('due_date', due_date)
        client=records.get('client',{})
        print('client',client)

        context = {
            'screen_name': 'Loan Case Detail',
            'case': case,
            'client':client,
            'assignment': assignment,
            'documents': documents,
            'timesheets': timesheets,
            'due_date':due_date
        }
        return render(request, 'loancase_detail.html', context)

# edit function
def loancase_edit(request,pk):
    user_token=request.session['user_token']

    endpoint2='clientprofile/'    
    records_response2 = call_get_method(BASEURL,endpoint2,user_token)
    print('records_response.status_code',records_response2.status_code)
    if records_response2.status_code not in [200,201]:
        messages.error(request, f"Failed to fetch records. {records_response2.json()}", extra_tags="warning")
    else:
        client_choice = records_response2.json()
        print('client_choices',client_choice)
    loancase = call_get_method_without_token(BASEURL, f'loancase/{pk}/')
    
    if loancase.status_code in [200,201]:
        loancase_data = loancase.json()
    else:
        print('error------',loancase)
        messages.error(request, 'Failed to retrieve data for loancase. Please check your connection and try again.', extra_tags='warning')
        return redirect('loancase')

    if request.method=="POST":
        form=LoanCaseForm(request.POST, initial=loancase_data,client_choices=client_choice)
        if form.is_valid():
            updated_data = form.cleaned_data
            updated_data['branch']=request.session['branch']
            updated_data['updated_by']=request.session['user_data']['id']

            for field_name, field in form.fields.items():
                if isinstance(field.widget, forms.DateInput) or isinstance(field, forms.DateField) or isinstance(field, forms.DateTimeField):
                    if updated_data[field_name]:
                        del updated_data[field_name]
                        updated_data[field_name] = request.POST.get(field_name)
            # Serialize the updated data as JSON
            json_data = json.dumps(updated_data)
            response = call_put_method_without_token(BASEURL, f'loancase/{pk}/', json_data)

            if response.status_code in [200,201]: 
                messages.success(request, 'Your data has been successfully saved', extra_tags='success')
                return redirect('loancase') 
            else:
                error_message = response.json()
                messages.error(request, f"Oops..! {error_message}", extra_tags='warning')
        else:
            print("An error occurred: Expecting value: line 1 column 1 (char 0)")
    else:
        form = LoanCaseForm(initial=loancase_data,client_choices=client_choice)

    context={
        'form':form,
    }
    return render(request,'loancase_edit.html',context)

def loancase_delete(request,pk):
    end_point = f'loancase/{pk}/'
    loancase = call_delete_method_without_token(BASEURL, end_point)
    if loancase.status_code not in [200,201]:
        messages.error(request, 'Failed to delete data for loancase. Please try again.', extra_tags='warning')
        return redirect('loancase_list')
    else:
        messages.success(request, 'Successfully deleted data for loancase', extra_tags='success')
        return redirect('loancase_list')



def loancase_approve(request, pk):
    try:
        user_token = request.session.get('user_token')
        json_data = json.dumps(pk)
        document = call_put_method(BASEURL, f'loancase_approve/{pk}/', json_data,user_token)
        print('--',document)
        print('--',document.status_code)
        if document.status_code not in [200, 201]:
            messages.error(request, 'Failed to approve loancase. Please try again.', extra_tags='warning')
        else:
            messages.success(request, 'loancase approved successfully.', extra_tags='success')
    except Exception as e:
        messages.error(request, f'Error: {str(e)}', extra_tags='danger')

    return redirect('loancase_list')


def loancase_reject(request):
    try:
        user_token = request.session.get('user_token')
        if request.method == "POST":
            pk = request.POST.get("customer_id")
            reason = request.POST.get("rejection_reason")
            print(pk,reason)
            json_data = json.dumps({"pk": pk, "reason": reason})
            print('json_data',json_data)
            document = call_put_method_without_token(BASEURL, f'loancase_reject/{pk}/{reason}/', json_data)
            print('---document',document.status_code)
            if document.status_code not in [200, 201]:
                messages.error(request, 'Failed to reject loancase. Please try again.', extra_tags='warning')
            else:
                messages.success(request, 'loancase rejected successfully.', extra_tags='success')
    except Exception as e:
        messages.error(request, f'Error: {str(e)}', extra_tags='danger')

    return redirect('loancase_list') 

# create and view table function
def projects(request):
    user_token=request.session['user_token']

    endpoint2='userprofile/'    
    records_response2 = call_get_method_without_token(BASEURL,endpoint2)
    print('records_response.status_code',records_response2.status_code)
    if records_response2.status_code not in [200,201]:
        messages.error(request, f"Failed to fetch records. {records_response2.json()}", extra_tags="warning")
    else:
        client_choice = records_response2.json()
        print('client_choices',client_choice)
    form=ProjectsForm(client_choices=client_choice)
    endpoint = 'projects/'
    if request.method=="POST":
        form=ProjectsForm(request.POST,client_choices=client_choice)
        if form.is_valid():
            Output = form.cleaned_data
            Output['branch']=request.session['branch']
            Output['created_by']=request.session['user_data']['id']

            for field_name, field in form.fields.items():
                if isinstance(field.widget, forms.DateInput) or isinstance(field, forms.DateField) or isinstance(field, forms.DateTimeField):
                    if Output[field_name]:
                        del Output[field_name]
                        Output[field_name] = request.POST.get(field_name)
            json_data=json.dumps(Output)
            response = call_post_method_for_without_token(BASEURL,endpoint,json_data)
            if response.status_code not in [200,201]:
                print("error",response)
            else:
                messages.success(request,'Data Successfully Saved', extra_tags="success")
                return redirect('projects_list')
    else:
        print('errorss',form.errors)
    try:
        # getting data from backend
        records_response = call_get_method(BASEURL,endpoint,user_token)
        if records_response.status_code not in [200,201]:
            messages.error(request, f"Failed to fetch records. {records_response.json()}", extra_tags="warning")
        else:
            records = records_response.json()
            # You can pass 'records' to your template for rendering
            context = {'form': form, 'records': records}
            return render(request, 'projects.html', context)
    except Exception as e:
        print("An error occurred: Expecting value: line 1 column 1 (char 0)")
    context={
        'form':form,
    }
    return render(request,'projects.html',context)

def projects_list(request):
    user_token=request.session['user_token']
    endpoint = 'projects/'
        # getting data from backend
    records_response = call_get_method_without_token(BASEURL,endpoint)
    if records_response.status_code not in [200,201]:
            messages.error(request, f"Failed to fetch records. {records_response.json()}", extra_tags="warning")
    else:
            records = records_response.json()
            # You can pass 'records' to your template for rendering
            context = {'records': records}
            return render(request, 'projects_list.html', context)
    return render(request,'projects_list.html',context)

# edit function
def projects_edit(request,pk):
    endpoint2='clientprofile/'    
    records_response2 = call_get_method_without_token(BASEURL,endpoint2)
    print('records_response.status_code',records_response2.status_code)
    if records_response2.status_code not in [200,201]:
        messages.error(request, f"Failed to fetch records. {records_response2.json()}", extra_tags="warning")
    else:
        client_choice = records_response2.json()
        print('client_choices',client_choice)
    projects = call_get_method_without_token(BASEURL, f'projects/{pk}/')
    
    if projects.status_code in [200,201]:
        projects_data = projects.json()
    else:
        print('error------',projects)
        messages.error(request, 'Failed to retrieve data for projects. Please check your connection and try again.', extra_tags='warning')
        return redirect('projects')

    if request.method=="POST":
        form=ProjectsForm(request.POST, initial=projects_data,client_choices=client_choice)
        if form.is_valid():
            updated_data = form.cleaned_data
            updated_data['branch']=request.session['branch']
            updated_data['updated_by']=request.session['user_data']['id']

            for field_name, field in form.fields.items():
                if isinstance(field.widget, forms.DateInput) or isinstance(field, forms.DateField) or isinstance(field, forms.DateTimeField):
                    if updated_data[field_name]:
                        del updated_data[field_name]
                        updated_data[field_name] = request.POST.get(field_name)
            # Serialize the updated data as JSON
            json_data = json.dumps(updated_data)
            response = call_put_method_without_token(BASEURL, f'projects/{pk}/', json_data)

            if response.status_code in [200,201]: 
                messages.success(request, 'Your data has been successfully saved', extra_tags='success')
                return redirect('projects') 
            else:
                error_message = response.json()
                messages.error(request, f"Oops..! {error_message}", extra_tags='warning')
        else:
            print("An error occurred: Expecting value: line 1 column 1 (char 0)")
    else:
        form = ProjectsForm(initial=projects_data,client_choices=client_choice)

    context={
        'form':form,
    }
    return render(request,'projects_edit.html',context)

def projects_delete(request,pk):
    end_point = f'projects/{pk}/'
    projects = call_delete_method_without_token(BASEURL, end_point)
    if projects.status_code not in [200,201]:
        messages.error(request, 'Failed to delete data for projects. Please try again.', extra_tags='warning')
        return redirect('projects')
    else:
        messages.success(request, 'Successfully deleted data for projects', extra_tags='success')
        return redirect('projects')

# create and view table function
def documenttype(request):
    user_token=request.session['user_token']

    # endpoint2='documentgroup/'    
    # records_response2 = call_get_method_without_token(BASEURL,endpoint2)
    # print('records_response.status_code',records_response2.status_code)
    # if records_response2.status_code not in [200,201]:
    #     messages.error(request, f"Failed to fetch records. {records_response2.json()}", extra_tags="warning")
    # else:
    #     groups = records_response2.json()
    #     print('client_choices',groups)
    form=DocumentTypeForm()
    endpoint = 'documenttype/'
    if request.method=="POST":
        form=DocumentTypeForm(request.POST)
        if form.is_valid():
            Output = form.cleaned_data
            Output['branch']=request.session['branch']

            for field_name, field in form.fields.items():
                if isinstance(field.widget, forms.DateInput) or isinstance(field, forms.DateField) or isinstance(field, forms.DateTimeField):
                    if Output[field_name]:
                        del Output[field_name]
                        Output[field_name] = request.POST.get(field_name)
            json_data=json.dumps(Output)
            response = call_post_method_for_without_token(BASEURL,endpoint,json_data)
            if response.status_code not in [200,201]:
                print("error",response)
            else:
                messages.success(request,'Data Successfully Saved', extra_tags="success")
                return redirect('documenttype_list')
    else:
        print('errorss',form.errors)
    try:
        # getting data from backend
        records_response = call_get_method(BASEURL,endpoint,user_token)
        if records_response.status_code not in [200,201]:
            messages.error(request, f"Failed to fetch records. {records_response.json()}", extra_tags="warning")
        else:
            records = records_response.json()
            # You can pass 'records' to your template for rendering
            context = {'form': form, 'records': records}
            return render(request, 'documenttype.html', context)
    except Exception as e:
        print("An error occurred: Expecting value: line 1 column 1 (char 0)")
    context={
        'form':form,
    }
    return render(request,'documenttype.html',context)

def documenttype_list(request):
    user_token=request.session['user_token']
    endpoint = 'documenttype/'
        # getting data from backend
    records_response = call_get_method_without_token(BASEURL,endpoint)
    if records_response.status_code not in [200,201]:
            messages.error(request, f"Failed to fetch records. {records_response.json()}", extra_tags="warning")
    else:
            records = records_response.json()
            # You can pass 'records' to your template for rendering
            context = {'records': records}
            return render(request, 'documenttype_list.html', context)
    return render(request,'documenttype_list.html',context)

# edit function
def documenttype_edit(request,pk):
    endpoint2='documentgroup/'    
    records_response2 = call_get_method_without_token(BASEURL,endpoint2)
    print('records_response.status_code',records_response2.status_code)
    if records_response2.status_code not in [200,201]:
        messages.error(request, f"Failed to fetch records. {records_response2.json()}", extra_tags="warning")
    else:
        groups = records_response2.json()
        print('client_choices',groups)
    documenttype = call_get_method_without_token(BASEURL, f'documenttype/{pk}/')
    
    if documenttype.status_code in [200,201]:
        documenttype_data = documenttype.json()
    else:
        print('error------',documenttype)
        messages.error(request, 'Failed to retrieve data for documenttype. Please check your connection and try again.', extra_tags='warning')
        return redirect('documenttype_list')

    if request.method=="POST":
        form=DocumentTypeForm(request.POST, initial=documenttype_data)
        if form.is_valid():
            updated_data = form.cleaned_data
            updated_data['branch']=request.session['branch']

            for field_name, field in form.fields.items():
                if isinstance(field.widget, forms.DateInput) or isinstance(field, forms.DateField) or isinstance(field, forms.DateTimeField):
                    if updated_data[field_name]:
                        del updated_data[field_name]
                        updated_data[field_name] = request.POST.get(field_name)
            # Serialize the updated data as JSON
            json_data = json.dumps(updated_data)
            response = call_put_method_without_token(BASEURL, f'documenttype/{pk}/', json_data)

            if response.status_code in [200,201]: 
                messages.success(request, 'Your data has been successfully saved', extra_tags='success')
                return redirect('documenttype_list') 
            else:
                error_message = response.json()
                messages.error(request, f"Oops..! {error_message}", extra_tags='warning')
        else:
            print("An error occurred: Expecting value: line 1 column 1 (char 0)")
    else:
        form = DocumentTypeForm(initial=documenttype_data)

    context={
        'form':form,
    }
    return render(request,'documenttype_edit.html',context)

def documenttype_delete(request,pk):
    end_point = f'documenttype/{pk}/'
    documenttype = call_delete_method_without_token(BASEURL, end_point)
    if documenttype.status_code not in [200,201]:
        messages.error(request, 'Failed to delete data for documenttype. Please try again.', extra_tags='warning')
        return redirect('documenttype_list')
    else:
        messages.success(request, 'Successfully deleted data for documenttype', extra_tags='success')
        return redirect('documenttype_list')

# create and view table function
def foldermaster(request):
    user_token=request.session['user_token']

    endpoint1='clientprofile/'    
    records_response2 = call_get_method(BASEURL,endpoint1,user_token)
    print('records_response.status_code',records_response2.status_code)
    if records_response2.status_code not in [200,201]:
        messages.error(request, f"Failed to fetch records. {records_response2.json()}", extra_tags="warning")
    else:
        clients = records_response2.json()
    print('clients',clients)
    endpoint2='customdocumententity/'    
    records_response2 = call_get_method(BASEURL,endpoint2,user_token)
    print('records_response.status_code',records_response2.status_code)
    if records_response2.status_code not in [200,201]:
        messages.error(request, f"Failed to fetch records. {records_response2.json()}", extra_tags="warning")
    else:
        entity = records_response2.json()
    endpoint3='foldermaster/'    
    records_response2 = call_get_method(BASEURL,endpoint3,user_token)
    print('records_response.status_code',records_response2.status_code)
    if records_response2.status_code not in [200,201]:
        messages.error(request, f"Failed to fetch records. {records_response2.json()}", extra_tags="warning")
    else:
        parent_folder = records_response2.json()
    form=FolderMasterForm(client_choices=clients,entity_choices=entity,parent_folder_choices=parent_folder)
    endpoint = 'foldermaster/'
    if request.method=="POST":
        form=FolderMasterForm(request.POST,client_choices=clients,entity_choices=entity,parent_folder_choices=parent_folder)
        if form.is_valid():
            Output = form.cleaned_data
            Output['branch']=request.session['branch']
            Output['created_by']=request.session['user_data']['id']

            for field_name, field in form.fields.items():
                if isinstance(field.widget, forms.DateInput) or isinstance(field, forms.DateField) or isinstance(field, forms.DateTimeField):
                    if Output[field_name]:
                        del Output[field_name]
                        Output[field_name] = request.POST.get(field_name)
            json_data=json.dumps(Output)
            response = call_post_method_for_without_token(BASEURL,endpoint,json_data)
            if response.status_code not in [200,201]:
                print("error",response)
            else:
                messages.success(request,'Data Successfully Saved', extra_tags="success")
                return redirect('foldermaster_list')
    else:
        print('errorss',form.errors)
    try:
        # getting data from backend
        records_response = call_get_method(BASEURL,endpoint,user_token)
        if records_response.status_code not in [200,201]:
            messages.error(request, f"Failed to fetch records. {records_response.json()}", extra_tags="warning")
        else:
            records = records_response.json()
            # You can pass 'records' to your template for rendering
            context = {'form': form, 'records': records}
            return render(request, 'foldermaster.html', context)
    except Exception as e:
        print("An error occurred: Expecting value: line 1 column 1 (char 0)")
    context={
        'form':form,
    }
    return render(request,'foldermaster.html',context)

def foldermaster_list(request):
    user_token=request.session['user_token']
    endpoint = 'foldermaster/'
        # getting data from backend
    records_response = call_get_method(BASEURL,endpoint,user_token)
    if records_response.status_code not in [200,201]:
            messages.error(request, f"Failed to fetch records. {records_response.json()}", extra_tags="warning")
    else:
            records = records_response.json()
            # You can pass 'records' to your template for rendering
            context = {'records': records}
            return render(request, 'foldermaster_list.html', context)
    return render(request,'foldermaster_list.html',context)

# edit function
def foldermaster_edit(request,pk):
    user_token=request.session['user_token']

    endpoint1='clientprofile/'    
    records_response2 = call_get_method(BASEURL,endpoint1,user_token)
    print('records_response.status_code',records_response2.status_code)
    if records_response2.status_code not in [200,201]:
        messages.error(request, f"Failed to fetch records. {records_response2.json()}", extra_tags="warning")
    else:
        clients = records_response2.json()
    endpoint2='customdocumententity/'    
    records_response2 = call_get_method_without_token(BASEURL,endpoint2)
    print('records_response.status_code',records_response2.status_code)
    if records_response2.status_code not in [200,201]:
        messages.error(request, f"Failed to fetch records. {records_response2.json()}", extra_tags="warning")
    else:
        entity = records_response2.json()
    endpoint3='foldermaster/'    
    records_response2 = call_get_method_without_token(BASEURL,endpoint3)
    print('records_response.status_code',records_response2.status_code)
    if records_response2.status_code not in [200,201]:
        messages.error(request, f"Failed to fetch records. {records_response2.json()}", extra_tags="warning")
    else:
        parent_folder = records_response2.json()
    foldermaster = call_get_method_without_token(BASEURL, f'foldermaster/{pk}/')
    
    if foldermaster.status_code in [200,201]:
        foldermaster_data = foldermaster.json()
    else:
        print('error------',foldermaster)
        messages.error(request, 'Failed to retrieve data for foldermaster. Please check your connection and try again.', extra_tags='warning')
        return redirect('foldermaster')

    if request.method=="POST":
        form=FolderMasterForm(request.POST, initial=foldermaster_data,client_choices=clients,entity_choices=entity,parent_folder_choices=parent_folder)
        if form.is_valid():
            updated_data = form.cleaned_data
            updated_data['branch']=request.session['branch']
            updated_data['updated_by']=request.session['user_data']['id']

            for field_name, field in form.fields.items():
                if isinstance(field.widget, forms.DateInput) or isinstance(field, forms.DateField) or isinstance(field, forms.DateTimeField):
                    if updated_data[field_name]:
                        del updated_data[field_name]
                        updated_data[field_name] = request.POST.get(field_name)
            # Serialize the updated data as JSON
            json_data = json.dumps(updated_data)
            response = call_put_method_without_token(BASEURL, f'foldermaster/{pk}/', json_data)

            if response.status_code in [200,201]: 
                messages.success(request, 'Your data has been successfully saved', extra_tags='success')
                return redirect('foldermaster') 
            else:
                error_message = response.json()
                messages.error(request, f"Oops..! {error_message}", extra_tags='warning')
        else:
            print("An error occurred: Expecting value: line 1 column 1 (char 0)")
    else:
        form = FolderMasterForm(initial=foldermaster_data,client_choices=clients,entity_choices=entity,parent_folder_choices=parent_folder)

    context={
        'form':form,
    }
    return render(request,'foldermaster_edit.html',context)

def foldermaster_delete(request,pk):
    end_point = f'foldermaster/{pk}/'
    foldermaster = call_delete_method_without_token(BASEURL, end_point)
    if foldermaster.status_code not in [200,201]:
        messages.error(request, 'Failed to delete data for foldermaster. Please try again.', extra_tags='warning')
        return redirect('foldermaster')
    else:
        messages.success(request, 'Successfully deleted data for foldermaster', extra_tags='success')
        return redirect('foldermaster')

# create and view table function

# create and view table function
def trioassignment(request):
    user_token=request.session['user_token']

    endpoint1='loancase/'    
    records_response2 = call_get_method(BASEURL,endpoint1,user_token)
    print('records_response.status_code',records_response2.status_code)
    if records_response2.status_code not in [200,201]:
        messages.error(request, f"Failed to fetch records. {records_response2.json()}", extra_tags="warning")
    else:
        clients = records_response2.json()
    endpoint2='triogroup/'    
    records_response2 = call_get_method(BASEURL,endpoint2,user_token)
    print('records_response.status_code',records_response2.status_code)
    if records_response2.status_code not in [200,201]:
        messages.error(request, f"Failed to fetch records. {records_response2.json()}", extra_tags="warning")
    else:
        entity = records_response2.json()
    form=TRIOAssignmentForm(client_choices=clients,group_choices=entity)
    endpoint = 'trioassignment/'
    if request.method=="POST":
        form=TRIOAssignmentForm(request.POST,client_choices=clients,group_choices=entity)
        if form.is_valid():
            Output = form.cleaned_data
            Output['branch']=request.session['branch']

            for field_name, field in form.fields.items():
                if isinstance(field.widget, forms.DateInput) or isinstance(field, forms.DateField) or isinstance(field, forms.DateTimeField):
                    if Output[field_name]:
                        del Output[field_name]
                        Output[field_name] = request.POST.get(field_name)
            json_data=json.dumps(Output)
            response = call_post_method_for_without_token(BASEURL,endpoint,json_data)
            if response.status_code not in [200,201]:
                print("error",response)
            else:
                messages.success(request,'Data Successfully Saved', extra_tags="success")
                return redirect('trioassignment_list')
    else:
        print('errorss',form.errors)
    try:
        # getting data from backend
        records_response = call_get_method(BASEURL,endpoint,user_token)
        if records_response.status_code not in [200,201]:
            messages.error(request, f"Failed to fetch records. {records_response.json()}", extra_tags="warning")
        else:
            records = records_response.json()
            # You can pass 'records' to your template for rendering
            context = {'form': form, 'records': records}
            return render(request, 'trioassignment.html', context)
    except Exception as e:
        print("An error occurred: Expecting value: line 1 column 1 (char 0)")
    context={
        'form':form,
    }
    return render(request,'trioassignment.html',context)

def trioassignment_list(request):
    user_token=request.session['user_token']
    endpoint = 'trioassignment/'
        # getting data from backend
    records_response = call_get_method(BASEURL,endpoint,user_token)
    if records_response.status_code not in [200,201]:
            messages.error(request, f"Failed to fetch records. {records_response.json()}", extra_tags="warning")
    else:
            records = records_response.json()
            # You can pass 'records' to your template for rendering
            context = {'records': records}
            return render(request, 'trioassignment_list.html', context)
    return render(request,'trioassignment_list.html',context)


# edit function
def trioassignment_edit(request,pk):
    endpoint1='clientprofile/'    
    records_response2 = call_get_method_without_token(BASEURL,endpoint1)
    print('records_response.status_code',records_response2.status_code)
    if records_response2.status_code not in [200,201]:
        messages.error(request, f"Failed to fetch records. {records_response2.json()}", extra_tags="warning")
    else:
        clients = records_response2.json()
    endpoint2='customdocumententity/'    
    records_response2 = call_get_method_without_token(BASEURL,endpoint2)
    print('records_response.status_code',records_response2.status_code)
    if records_response2.status_code not in [200,201]:
        messages.error(request, f"Failed to fetch records. {records_response2.json()}", extra_tags="warning")
    else:
        entity = records_response2.json()
    trioassignment = call_get_method_without_token(BASEURL, f'trioassignment/{pk}/')
    
    if trioassignment.status_code in [200,201]:
        trioassignment_data = trioassignment.json()
    else:
        print('error------',trioassignment)
        messages.error(request, 'Failed to retrieve data for trioassignment. Please check your connection and try again.', extra_tags='warning')
        return redirect('trioassignment')

    if request.method=="POST":
        form=TRIOAssignmentForm(request.POST, initial=trioassignment_data,client_choices=clients,group_choices=entity)
        if form.is_valid():
            updated_data = form.cleaned_data
            updated_data['branch']=request.session['branch']
            updated_data['updated_by']=request.session['user_data']['id']

            for field_name, field in form.fields.items():
                if isinstance(field.widget, forms.DateInput) or isinstance(field, forms.DateField) or isinstance(field, forms.DateTimeField):
                    if updated_data[field_name]:
                        del updated_data[field_name]
                        updated_data[field_name] = request.POST.get(field_name)
            # Serialize the updated data as JSON
            json_data = json.dumps(updated_data)
            response = call_put_method_without_token(BASEURL, f'trioassignment/{pk}/', json_data)

            if response.status_code in [200,201]: 
                messages.success(request, 'Your data has been successfully saved', extra_tags='success')
                return redirect('trioassignment') 
            else:
                error_message = response.json()
                messages.error(request, f"Oops..! {error_message}", extra_tags='warning')
        else:
            print("An error occurred: Expecting value: line 1 column 1 (char 0)")
    else:
        form = TRIOAssignmentForm(initial=trioassignment_data,client_choices=clients,group_choices=entity)

    context={
        'form':form,
    }
    return render(request,'trioassignment_edit.html',context)

def trioassignment_delete(request,pk):
    end_point = f'trioassignment/{pk}/'
    trioassignment = call_delete_method_without_token(BASEURL, end_point)
    if trioassignment.status_code not in [200,201]:
        messages.error(request, 'Failed to delete data for trioassignment. Please try again.', extra_tags='warning')
        return redirect('trioassignment')
    else:
        messages.success(request, 'Successfully deleted data for trioassignment', extra_tags='success')
        return redirect('trioassignment')

# create and view table function
def auditlog(request):
    user_token=request.session['user_token']

    endpoint1='UserManagement/user/'    
    records_response2 = call_get_method(BASEURL,endpoint1,user_token)
    print('records_response.status_code',records_response2.status_code)
    if records_response2.status_code not in [200,201]:
        messages.error(request, f"Failed to fetch records. {records_response2.json()}", extra_tags="warning")
    else:
        clients = records_response2.json()
    endpoint2='loancase/'    
    records_response2 = call_get_method_without_token(BASEURL,endpoint2)
    print('records_response.status_code',records_response2.status_code)
    if records_response2.status_code not in [200,201]:
        messages.error(request, f"Failed to fetch records. {records_response2.json()}", extra_tags="warning")
    else:
        entity = records_response2.json()

    form=AuditLogForm(user_choices=clients,case_choices=entity)
    endpoint = 'auditlog/'
    if request.method=="POST":
        form=AuditLogForm(request.POST,user_choices=clients,case_choices=entity)
        if form.is_valid():
            Output = form.cleaned_data
            Output['branch']=request.session['branch']
            Output['created_by']=request.session['user_data']['id']

            for field_name, field in form.fields.items():
                if isinstance(field.widget, forms.DateInput) or isinstance(field, forms.DateField) or isinstance(field, forms.DateTimeField):
                    if Output[field_name]:
                        del Output[field_name]
                        Output[field_name] = request.POST.get(field_name)
            json_data=json.dumps(Output)
            response = call_post_method_for_without_token(BASEURL,endpoint,json_data)
            if response.status_code not in [200,201]:
                print("error",response)
            else:
                messages.success(request,'Data Successfully Saved', extra_tags="success")
                return redirect('auditlog_list')
    else:
        print('errorss',form.errors)
    try:
        # getting data from backend
        records_response = call_get_method(BASEURL,endpoint,user_token)
        if records_response.status_code not in [200,201]:
            messages.error(request, f"Failed to fetch records. {records_response.json()}", extra_tags="warning")
        else:
            records = records_response.json()
            # You can pass 'records' to your template for rendering
            context = {'form': form, 'records': records}
            return render(request, 'auditlog.html', context)
    except Exception as e:
        print("An error occurred: Expecting value: line 1 column 1 (char 0)")
    context={
        'form':form,
    }
    return render(request,'auditlog.html',context)

def auditlog_list(request):
    user_token=request.session['user_token']
    endpoint = 'auditlog/'
        # getting data from backend
    records_response = call_get_method_without_token(BASEURL,endpoint)
    if records_response.status_code not in [200,201]:
            messages.error(request, f"Failed to fetch records. {records_response.json()}", extra_tags="warning")
    else:
            records = records_response.json()
            # You can pass 'records' to your template for rendering
            context = {'records': records}
            return render(request, 'auditlog_list.html', context)
    return render(request,'auditlog_list.html',context)

# edit function
def auditlog_edit(request,pk):
    user_token=request.session['user_token']
    endpoint2='UserManagement/user/'    
    records_response2 = call_get_method(BASEURL,endpoint2,user_token)
    print('records_response.status_code',records_response2.status_code)
    if records_response2.status_code not in [200,201]:
        messages.error(request, f"Failed to fetch records. {records_response2.json()}", extra_tags="warning")
    else:
        clients = records_response2.json()
    endpoint2='loancase/'    
    records_response2 = call_get_method_without_token(BASEURL,endpoint2)
    print('records_response.status_code',records_response2.status_code)
    if records_response2.status_code not in [200,201]:
        messages.error(request, f"Failed to fetch records. {records_response2.json()}", extra_tags="warning")
    else:
        entity = records_response2.json()
    auditlog = call_get_method_without_token(BASEURL, f'auditlog/{pk}/')
    
    if auditlog.status_code in [200,201]:
        auditlog_data = auditlog.json()
    else:
        print('error------',auditlog)
        messages.error(request, 'Failed to retrieve data for auditlog. Please check your connection and try again.', extra_tags='warning')
        return redirect('auditlog')

    if request.method=="POST":
        form=AuditLogForm(request.POST, initial=auditlog_data,user_choices=clients,case_choices=entity)
        if form.is_valid():
            updated_data = form.cleaned_data
            updated_data['branch']=request.session['branch']
            updated_data['updated_by']=request.session['user_data']['id']

            for field_name, field in form.fields.items():
                if isinstance(field.widget, forms.DateInput) or isinstance(field, forms.DateField) or isinstance(field, forms.DateTimeField):
                    if updated_data[field_name]:
                        del updated_data[field_name]
                        updated_data[field_name] = request.POST.get(field_name)
            # Serialize the updated data as JSON
            json_data = json.dumps(updated_data)
            response = call_put_method_without_token(BASEURL, f'auditlog/{pk}/', json_data)

            if response.status_code in [200,201]: 
                messages.success(request, 'Your data has been successfully saved', extra_tags='success')
                return redirect('auditlog') 
            else:
                error_message = response.json()
                messages.error(request, f"Oops..! {error_message}", extra_tags='warning')
        else:
            print("An error occurred: Expecting value: line 1 column 1 (char 0)")
    else:
        form = AuditLogForm(initial=auditlog_data,user_choices=clients,case_choices=entity)

    context={
        'form':form,
    }
    return render(request,'auditlog_edit.html',context)

def auditlog_delete(request,pk):
    end_point = f'auditlog/{pk}/'
    auditlog = call_delete_method_without_token(BASEURL, end_point)
    if auditlog.status_code not in [200,201]:
        messages.error(request, 'Failed to delete data for auditlog. Please try again.', extra_tags='warning')
        return redirect('auditlog')
    else:
        messages.success(request, 'Successfully deleted data for auditlog', extra_tags='success')
        return redirect('auditlog')

# create and view table function
def compliancechecklist(request):
    user_token=request.session['user_token']

    endpoint1='loancase/'    
    records_response2 = call_get_method_without_token(BASEURL,endpoint1)
    print('records_response.status_code',records_response2.status_code)
    if records_response2.status_code not in [200,201]:
        messages.error(request, f"Failed to fetch records. {records_response2.json()}", extra_tags="warning")
    else:
        clients = records_response2.json()
    form=ComplianceChecklistForm(case_choices=clients)
    endpoint = 'compliancechecklist/'
    if request.method=="POST":
        form=ComplianceChecklistForm(request.POST,case_choices=clients)
        if form.is_valid():
            Output = form.cleaned_data
            Output['branch']=request.session['branch']
            Output['created_by']=request.session['user_data']['id']

            for field_name, field in form.fields.items():
                if isinstance(field.widget, forms.DateInput) or isinstance(field, forms.DateField) or isinstance(field, forms.DateTimeField):
                    if Output[field_name]:
                        del Output[field_name]
                        Output[field_name] = request.POST.get(field_name)
            json_data=json.dumps(Output)
            response = call_post_method_for_without_token(BASEURL,endpoint,json_data)
            if response.status_code not in [200,201]:
                print("error",response)
            else:
                messages.success(request,'Data Successfully Saved', extra_tags="success")
                return redirect('compliancechecklist_list')
    else:
        print('errorss',form.errors)
    try:
        # getting data from backend
        records_response = call_get_method(BASEURL,endpoint,user_token)
        if records_response.status_code not in [200,201]:
            messages.error(request, f"Failed to fetch records. {records_response.json()}", extra_tags="warning")
        else:
            records = records_response.json()
            # You can pass 'records' to your template for rendering
            context = {'form': form, 'records': records}
            return render(request, 'compliancechecklist.html', context)
    except Exception as e:
        print("An error occurred: Expecting value: line 1 column 1 (char 0)")
    context={
        'form':form,
    }
    return render(request,'compliancechecklist.html',context)

def compliancechecklist_list(request):
    user_token=request.session['user_token']
    endpoint = 'compliancechecklist/'
        # getting data from backend
    records_response = call_get_method_without_token(BASEURL,endpoint)
    if records_response.status_code not in [200,201]:
            messages.error(request, f"Failed to fetch records. {records_response.json()}", extra_tags="warning")
    else:
            records = records_response.json()
            # You can pass 'records' to your template for rendering
            context = {'records': records}
            return render(request, 'compliancechecklist_list.html', context)
    return render(request,'compliancechecklist_list.html',context)

# edit function
def compliancechecklist_edit(request,pk):
    endpoint1='loancase/'    
    records_response2 = call_get_method_without_token(BASEURL,endpoint1)
    print('records_response.status_code',records_response2.status_code)
    if records_response2.status_code not in [200,201]:
        messages.error(request, f"Failed to fetch records. {records_response2.json()}", extra_tags="warning")
    else:
        clients = records_response2.json()
    compliancechecklist = call_get_method_without_token(BASEURL, f'compliancechecklist/{pk}/')
    
    if compliancechecklist.status_code in [200,201]:
        compliancechecklist_data = compliancechecklist.json()
    else:
        print('error------',compliancechecklist)
        messages.error(request, 'Failed to retrieve data for compliancechecklist. Please check your connection and try again.', extra_tags='warning')
        return redirect('compliancechecklist')

    if request.method=="POST":
        form=ComplianceChecklistForm(request.POST, initial=compliancechecklist_data,case_choices=clients)
        if form.is_valid():
            updated_data = form.cleaned_data
            updated_data['branch']=request.session['branch']
            updated_data['updated_by']=request.session['user_data']['id']

            for field_name, field in form.fields.items():
                if isinstance(field.widget, forms.DateInput) or isinstance(field, forms.DateField) or isinstance(field, forms.DateTimeField):
                    if updated_data[field_name]:
                        del updated_data[field_name]
                        updated_data[field_name] = request.POST.get(field_name)
            # Serialize the updated data as JSON
            json_data = json.dumps(updated_data)
            response = call_put_method_without_token(BASEURL, f'compliancechecklist/{pk}/', json_data)

            if response.status_code in [200,201]: 
                messages.success(request, 'Your data has been successfully saved', extra_tags='success')
                return redirect('compliancechecklist') 
            else:
                error_message = response.json()
                messages.error(request, f"Oops..! {error_message}", extra_tags='warning')
        else:
            print("An error occurred: Expecting value: line 1 column 1 (char 0)")
    else:
        form = ComplianceChecklistForm(initial=compliancechecklist_data,case_choices=clients)

    context={
        'form':form,
    }
    return render(request,'compliancechecklist_edit.html',context)

def compliancechecklist_delete(request,pk):
    end_point = f'compliancechecklist/{pk}/'
    compliancechecklist = call_delete_method_without_token(BASEURL, end_point)
    if compliancechecklist.status_code not in [200,201]:
        messages.error(request, 'Failed to delete data for compliancechecklist. Please try again.', extra_tags='warning')
        return redirect('compliancechecklist')
    else:
        messages.success(request, 'Successfully deleted data for compliancechecklist', extra_tags='success')
        return redirect('compliancechecklist')

# create and view table function
def document(request):
    user_token = request.session.get('user_token')
    branch = request.session.get('branch')
    uploaded_by = request.session.get('user_data', {}).get('id')

    # Fetch loan cases for dropdown
    endpoint1 = 'case_dcoument/'    
    records_response2 = call_get_method(BASEURL, endpoint1, user_token)
    
    if records_response2.status_code not in [200, 201]:
        messages.error(request, f"Failed to fetch loan cases. {records_response2.json()}", extra_tags="warning")
        clients = []
    else:
        clients = records_response2.json()

    form = DocumentForm(case_choices=clients)
    endpoint = 'document/'

    if request.method == "POST":
        form = DocumentForm(request.POST, files=request.FILES, case_choices=clients)
        if form.is_valid():
            cleaned_data = form.cleaned_data
            # Override or include additional session data
            cleaned_data['branch'] = branch
            cleaned_data['uploaded_by'] = uploaded_by

            # Ensure correct date values from request.POST (if any DateInput fields)
            for field_name, field in form.fields.items():
                if isinstance(field.widget, forms.DateInput) or isinstance(field, forms.DateField) or isinstance(field, forms.DateTimeField):
                    cleaned_data[field_name] = request.POST.get(field_name)

            # Handle files if present
            files, cleaned_data = image_filescreate(cleaned_data)
            json_data = cleaned_data if files else json.dumps(cleaned_data)

            print('==json_data==', json_data)
            response = call_post_method_with_token_v2(BASEURL, endpoint, json_data, files)
            print('==response==', response)

            if response.get('status_code') == 1:
                messages.error(request, f"Error: {response.get('message', 'Unknown error')}", extra_tags="danger")
            else:
                messages.success(request, 'Data Successfully Saved', extra_tags="success")
                return redirect('document_list')
        else:
            print('Form errors:', form.errors)

    # Fetch existing documents for display
    try:
        records_response = call_get_method(BASEURL, endpoint, user_token)
        if records_response.status_code not in [200, 201]:
            messages.error(request, f"Failed to fetch document records. {records_response.json()}", extra_tags="warning")
            records = []
        else:
            records = records_response.json()
    except Exception as e:
        print("An error occurred while fetching records:", str(e))
        records = []

    context = {
        'form': form,
        'records': records,
    }
    return render(request, 'document.html', context)

def document_list(request):
    try:
        user_token=request.session['user_token']
        endpoint = 'document/'
        records_response = call_get_method(BASEURL,endpoint,user_token)
        if records_response.status_code not in [200,201]:
            messages.error(request, f"Failed to fetch records. {records_response.json()}", extra_tags="warning")
        else:
            records = records_response.json()
            # You can pass 'records' to your template for rendering
            context = {'records': records}
            return render(request, 'document_list.html', context)
    except Exception as e:
        print("An error occurred: Expecting value: line 1 column 1 (char 0)")
    
    return render(request,'document_list.html',context)


def client_documents(request):
    try:
        user_token=request.session['user_token']

        endpoint = 'document/'
        records_response = call_get_method(BASEURL,endpoint,user_token)
        if records_response.status_code not in [200,201]:
            messages.error(request, f"Failed to fetch records. {records_response.json()}", extra_tags="warning")
        else:
            records = records_response.json()
            # You can pass 'records' to your template for rendering
            context = {'records': records}
            return render(request, 'customer_documents.html', context)
    except Exception as e:
        print("An error occurred: Expecting value: line 1 column 1 (char 0)")
    
    return render(request,'customer_documents.html',context)

def client_document(request,case):
    user_token=request.session['user_token']

    form=ClientDocumentForm()
    endpoint = 'document/'
    if request.method=="POST":
        form=ClientDocumentForm(request.POST,files=request.FILES,)
        if form.is_valid():
            Output = form.cleaned_data
            Output['branch']=request.session['branch']
            Output['case'] = case
            Output['uploaded_by']=request.session['user_data']['id']
            for field_name, field in form.fields.items():
                if isinstance(field.widget, forms.DateInput) or isinstance(field, forms.DateField) or isinstance(field, forms.DateTimeField):
                    if Output[field_name]:
                        del Output[field_name]
                        Output[field_name] = request.POST.get(field_name)
                cleaned_data = form.cleaned_data
                files, cleaned_data = image_filescreate(cleaned_data)
                json_data = cleaned_data if files else json.dumps(cleaned_data)
                print('==json_data==,',json_data)
                response = call_post_method_with_token_v2(BASEURL,endpoint,json_data,files)

                print('==response==',response)
                if response['status_code'] == 1:
                    print("error",response)
            else:
                messages.success(request,'Data Successfully Saved', extra_tags="success")
                return redirect('document_list')
    else:
        print('errorss',form.errors)
    try:
        # getting data from backend
        records_response = call_get_method(BASEURL,endpoint,user_token)
        if records_response.status_code not in [200,201]:
            messages.error(request, f"Failed to fetch records. {records_response.json()}", extra_tags="warning")
        else:
            records = records_response.json()
            # You can pass 'records' to your template for rendering
            context = {'form': form, 'records': records}
            return render(request, 'document.html', context)
    except Exception as e:
        print("An error occurred: Expecting value: line 1 column 1 (char 0)")
    context={
        'form':form,
    }
    return render(request,'document.html',context)

def client_document_list(request, case):
    context = {}  
    print('-----case',case)
    try:
        user_token = request.session['user_token']
        endpoint1 = 'loancase/'    
        records_response2 = call_get_method(BASEURL, endpoint1, user_token)

        if records_response2.status_code not in [200, 201]:
            messages.error(request, f"Failed to fetch records. {records_response2.json()}", extra_tags="warning")
            clients = []
        else:
            clients = records_response2.json()
        form = ClientDocumentForm()

        if request.method == "POST":
            form = ClientDocumentForm(request.POST, files=request.FILES, )
            if form.is_valid():
                Output = form.cleaned_data
                Output['branch'] = request.session['branch']
                Output['case'] = case
                Output['uploaded_by'] = request.session['user_data']['id']

                for field_name, field in form.fields.items():
                    if isinstance(field.widget, forms.DateInput) or isinstance(field, forms.DateField) or isinstance(field, forms.DateTimeField):
                        if Output[field_name]:
                            del Output[field_name]
                            Output[field_name] = request.POST.get(field_name)

                cleaned_data = form.cleaned_data
                files, cleaned_data = image_filescreate(cleaned_data)
                json_data = cleaned_data if files else json.dumps(cleaned_data)

                response = call_post_method_with_token_v2(BASEURL, 'document/', json_data, files)

                if response['status_code'] == 1:
                    print("error", response)
                else:
                    messages.success(request, 'Data Successfully Saved', extra_tags="success")
                    return redirect('document_list')

        # Fetch the documents for both GET and POST
        endpoint = f'client_document/{case}/'
        records_response = call_get_method(BASEURL, endpoint, user_token)
        if records_response.status_code not in [200, 201]:
            messages.error(request, f"Failed to fetch records. {records_response.json()}", extra_tags="warning")
            records = []
        else:
            records = records_response.json()
            print('---',records)

        context = {'records': records, 'form': form ,'case': case}

    except Exception as e:
        print("An error occurred:", e)
        messages.error(request, "An unexpected error occurred.", extra_tags="danger")
        context={
        'form':form,
        }
    return render(request, 'customer_document_list.html', context)

# edit function
def document_edit(request,pk):
    user_token=request.session['user_token']
    endpoint1='loancase/'    
    records_response2 = call_get_method(BASEURL,endpoint1,user_token)
    print('records_response.status_code',records_response2.status_code)
    if records_response2.status_code not in [200,201]:
        messages.error(request, f"Failed to fetch records. {records_response2.json()}", extra_tags="warning")
    else:
        clients = records_response2.json()
    document = call_get_method_without_token(BASEURL, f'document/{pk}/')
    
    if document.status_code in [200,201]:
        document_data = document.json()
        print('---',document_data)
    else:
        print('error------',document)
        messages.error(request, 'Failed to retrieve data for document. Please check your connection and try again.', extra_tags='warning')
        return redirect('document_list')

    # if request.method=="POST":
    #     form=DocumentForm(request.POST,request.FILES, initial=document_data,case_choices=clients)
    #     if form.is_valid():
    #         updated_data = form.cleaned_data
    #         for field_name, field in form.fields.items():
    #             if isinstance(field.widget, forms.DateInput) or isinstance(field, forms.DateField) or isinstance(field, forms.DateTimeField):
    #                 if updated_data[field_name]:
    #                     del updated_data[field_name]
    #                     updated_data[field_name] = request.POST.get(field_name)
    #         # Serialize the updated data as JSON
    #         json_data = json.dumps(updated_data)
    #         print('json_data',json_data)
    #         response = call_put_method(BASEURL, f'document/{pk}/', json_data,user_token)

    #         if response.status_code in [200,201]: 
    #             messages.success(request, 'Your data has been successfully saved', extra_tags='success')
    #             return redirect('document_list') 
    #         else:
    #             error_message = response.json()
    #             messages.error(request, f"Oops..! {error_message}", extra_tags='warning')
    if request.method == "POST":
        form = DocumentForm(request.POST, request.FILES, initial=document_data, case_choices=clients)
        if form.is_valid():
            updated_data = form.cleaned_data

            # Remove file-type fields from cleaned_data before json.dumps
            file_fields = []
            for field_name, field in form.fields.items():
                if isinstance(field.widget, forms.DateInput) or isinstance(field, forms.DateField) or isinstance(field, forms.DateTimeField):
                    if updated_data[field_name]:
                        updated_data[field_name] = request.POST.get(field_name)
                if hasattr(updated_data[field_name], 'file'):  # File fields like TemporaryUploadedFile
                    file_fields.append(field_name)

            for f in file_fields:
                updated_data.pop(f)

            # Serialize to JSON
            json_data = json.dumps(updated_data)
            print('json_data', json_data)

            # Upload JSON data
            response = call_put_method(BASEURL, f'document/{pk}/', json_data, user_token)

            # Optionally: Handle file upload separately (depends on your API design)

            if response.status_code in [200, 201]: 
                messages.success(request, 'Your data has been successfully saved', extra_tags='success')
                return redirect('document_list') 
            else:
                error_message = response.json()
                messages.error(request, f"Oops..! {error_message}", extra_tags='warning')

        else:
            print("An error occurred: Expecting value: line 1 column 1 (char 0)")
    else:
        form = DocumentForm(initial=document_data,case_choices=clients)

    context={
        'form':form,
    }
    return render(request,'document_edit.html',context)

def document_approve(request, pk):
    try:
        user_token = request.session.get('user_token')
        json_data = json.dumps(pk)
        document = call_put_method_without_token(BASEURL, f'document_approve/{pk}/', json_data)
        print('--',document)
        print('--',document.status_code)
        if document.status_code not in [200, 201]:
            messages.error(request, 'Failed to approve document. Please try again.', extra_tags='warning')
        else:
            messages.success(request, 'Document approved successfully.', extra_tags='success')
    except Exception as e:
        messages.error(request, f'Error: {str(e)}', extra_tags='danger')

    return redirect('document_list')


def timesheet_approve(request, pk):
    try:
        user_token = request.session.get('user_token')
        json_data = json.dumps(pk)
        document = call_put_method(BASEURL, f'timesheet_approve/{pk}/', json_data,user_token)
        print('--',document)
        print('--',document.status_code)
        if document.status_code not in [200, 201]:
            messages.error(request, 'Failed to approve timesheetentry. Please try again.', extra_tags='warning')
        else:
            messages.success(request, 'timesheetentry approved successfully.', extra_tags='success')
    except Exception as e:
        messages.error(request, f'Error: {str(e)}', extra_tags='danger')

    return redirect('tasktimesheet_approval_list')


def timesheet_reject(request):
    try:
        user_token = request.session.get('user_token')
        if request.method == "POST":
            pk = request.POST.get("customer_id")
            reason = request.POST.get("rejection_reason")
            print(pk,reason)
            json_data = json.dumps({"pk": pk, "reason": reason})
            print('json_data',json_data)
            document = call_put_method_without_token(BASEURL, f'timesheet_reject/{pk}/{reason}/', json_data)
            print('---document',document.status_code)
            if document.status_code not in [200, 201]:
                messages.error(request, 'Failed to reject timesheet. Please try again.', extra_tags='warning')
            else:
                messages.success(request, 'timesheet rejected successfully.', extra_tags='success')
    except Exception as e:
        messages.error(request, f'Error: {str(e)}', extra_tags='danger')

    return redirect('tasktimesheet_approval_list') 


def timesheetentry_approve(request, pk):
    try:
        print('entry approval')
        user_token = request.session.get('user_token')
        json_data = json.dumps(pk)
        document = call_put_method(BASEURL, f'timesheetentry_approve/{pk}/', json_data,user_token)
        print('--',document)
        print('--',document.status_code)
        if document.status_code not in [200, 201]:
            messages.error(request, 'Failed to approve timesheetentry. Please try again.', extra_tags='warning')
        else:
            messages.success(request, 'timesheetentry approved successfully.', extra_tags='success')
    except Exception as e:
        messages.error(request, f'Error: {str(e)}', extra_tags='danger')

    return redirect('timesheetentry_approval_list')


def timesheetentry_reject(request):
    try:
        user_token = request.session.get('user_token')
        if request.method == "POST":
            pk = request.POST.get("customer_id")
            reason = request.POST.get("rejection_reason")
            print(pk,reason)
            json_data = json.dumps({"pk": pk, "reason": reason})
            print('json_data',json_data)
            document = call_put_method_without_token(BASEURL, f'timesheetentry_reject/{pk}/{reason}/', json_data)
            print('---document',document.status_code)
            if document.status_code not in [200, 201]:
                messages.error(request, 'Failed to reject timesheetentry. Please try again.', extra_tags='warning')
            else:
                messages.success(request, 'timesheetentry rejected successfully.', extra_tags='success')
    except Exception as e:
        messages.error(request, f'Error: {str(e)}', extra_tags='danger')

    return redirect('timesheetentry_approval_list') 


def document_reject(request):
    try:
        user_token = request.session.get('user_token')
        if request.method == "POST":
            pk = request.POST.get("customer_id")
            reason = request.POST.get("rejection_reason")
            print(pk,reason)
            json_data = json.dumps({"pk": pk, "reason": reason})
            print('json_data',json_data)
            document = call_put_method_without_token(BASEURL, f'document_reject/{pk}/{reason}/', json_data)
            print('---document',document.status_code)
            if document.status_code not in [200, 201]:
                messages.error(request, 'Failed to reject document. Please try again.', extra_tags='warning')
            else:
                messages.success(request, 'Document rejected successfully.', extra_tags='success')
    except Exception as e:
        messages.error(request, f'Error: {str(e)}', extra_tags='danger')

    return redirect('document_list') 

def document_delete(request,pk):
    end_point = f'document/{pk}/'
    document = call_delete_method_without_token(BASEURL, end_point)
    if document.status_code not in [200,201]:
        messages.error(request, 'Failed to delete data for document. Please try again.', extra_tags='warning')
        return redirect('document_list')
    else:
        messages.success(request, 'Successfully deleted data for document', extra_tags='success')
        return redirect('document_list')

# create and view table function
def riskassessment(request):
    user_token=request.session['user_token']
    endpoint2='UserManagement/user/'    
    records_response2 = call_get_method(BASEURL,endpoint2,user_token)

    print('records_response.status_code',records_response2.status_code)
    if records_response2.status_code not in [200,201]:
        messages.error(request, f"Failed to fetch records. {records_response2.json()}", extra_tags="warning")
    else:
        clients = records_response2.json()
    endpoint2='loancase/'    
    records_response2 = call_get_method_without_token(BASEURL,endpoint2)
    print('records_response.status_code',records_response2.status_code)
    if records_response2.status_code not in [200,201]:
        messages.error(request, f"Failed to fetch records. {records_response2.json()}", extra_tags="warning")
    else:
        entity = records_response2.json()
    form=RiskAssessmentForm(user_choices=clients,case_choices=entity)
    endpoint = 'riskassessment/'
    if request.method=="POST":
        form=RiskAssessmentForm(request.POST,user_choices=clients,case_choices=entity)
        if form.is_valid():
            Output = form.cleaned_data
            Output['branch']=request.session['branch']
            Output['created_by']=request.session['user_data']['id']

            for field_name, field in form.fields.items():
                if isinstance(field.widget, forms.DateInput) or isinstance(field, forms.DateField) or isinstance(field, forms.DateTimeField):
                    if Output[field_name]:
                        del Output[field_name]
                        Output[field_name] = request.POST.get(field_name)
            json_data=json.dumps(Output)
            response = call_post_method_for_without_token(BASEURL,endpoint,json_data)
            if response.status_code not in [200,201]:
                print("error",response)
            else:
                messages.success(request,'Data Successfully Saved', extra_tags="success")
                return redirect('riskassessment_list')
    else:
        print('errorss',form.errors)
    try:
        # getting data from backend
        records_response = call_get_method(BASEURL,endpoint,user_token)
        if records_response.status_code not in [200,201]:
            messages.error(request, f"Failed to fetch records. {records_response.json()}", extra_tags="warning")
        else:
            records = records_response.json()
            # You can pass 'records' to your template for rendering
            context = {'form': form, 'records': records}
            return render(request, 'riskassessment.html', context)
    except Exception as e:
        print("An error occurred: Expecting value: line 1 column 1 (char 0)")
    context={
        'form':form,
    }
    return render(request,'riskassessment.html',context)

def riskassessment_list(request):
    user_token=request.session['user_token']
    endpoint = 'riskassessment/'
        # getting data from backend
    records_response = call_get_method_without_token(BASEURL,endpoint)
    if records_response.status_code not in [200,201]:
            messages.error(request, f"Failed to fetch records. {records_response.json()}", extra_tags="warning")
    else:
            records = records_response.json()
            # You can pass 'records' to your template for rendering
            context = {'records': records}
            return render(request, 'riskassessment_list.html', context)
    return render(request,'riskassessment_list.html',context)

# edit function
def riskassessment_edit(request,pk):
    user_token=request.session['user_token']
    endpoint2='UserManagement/user/'    
    records_response2 = call_get_method(BASEURL,endpoint2,user_token)

    print('records_response.status_code',records_response2.status_code)
    if records_response2.status_code not in [200,201]:
        messages.error(request, f"Failed to fetch records. {records_response2.json()}", extra_tags="warning")
    else:
        clients = records_response2.json()
    endpoint2='loancase/'    
    records_response2 = call_get_method_without_token(BASEURL,endpoint2)
    print('records_response.status_code',records_response2.status_code)
    if records_response2.status_code not in [200,201]:
        messages.error(request, f"Failed to fetch records. {records_response2.json()}", extra_tags="warning")
    else:
        entity = records_response2.json()
    riskassessment = call_get_method_without_token(BASEURL, f'riskassessment/{pk}/')
    
    if riskassessment.status_code in [200,201]:
        riskassessment_data = riskassessment.json()
    else:
        print('error------',riskassessment)
        messages.error(request, 'Failed to retrieve data for riskassessment. Please check your connection and try again.', extra_tags='warning')
        return redirect('riskassessment')

    if request.method=="POST":
        form=RiskAssessmentForm(request.POST, initial=riskassessment_data,user_choices=clients,case_choices=entity)
        if form.is_valid():
            updated_data = form.cleaned_data
            for field_name, field in form.fields.items():
                if isinstance(field.widget, forms.DateInput) or isinstance(field, forms.DateField) or isinstance(field, forms.DateTimeField):
                    if updated_data[field_name]:
                        del updated_data[field_name]
                        updated_data[field_name] = request.POST.get(field_name)
            # Serialize the updated data as JSON
            json_data = json.dumps(updated_data)
            response = call_put_method_without_token(BASEURL, f'riskassessment/{pk}/', json_data)

            if response.status_code in [200,201]: 
                messages.success(request, 'Your data has been successfully saved', extra_tags='success')
                return redirect('riskassessment') 
            else:
                error_message = response.json()
                messages.error(request, f"Oops..! {error_message}", extra_tags='warning')
        else:
            print("An error occurred: Expecting value: line 1 column 1 (char 0)")
    else:
        form = RiskAssessmentForm(initial=riskassessment_data,user_choices=clients,case_choices=entity)

    context={
        'form':form,
    }
    return render(request,'riskassessment_edit.html',context)

def riskassessment_delete(request,pk):
    end_point = f'riskassessment/{pk}/'
    riskassessment = call_delete_method_without_token(BASEURL, end_point)
    if riskassessment.status_code not in [200,201]:
        messages.error(request, 'Failed to delete data for riskassessment. Please try again.', extra_tags='warning')
        return redirect('riskassessment')
    else:
        messages.success(request, 'Successfully deleted data for riskassessment', extra_tags='success')
        return redirect('riskassessment')

# create and view table function
def clientquery(request):
    user_token=request.session['user_token']

    endpoint1='clientprofile/'    
    records_response2 = call_get_method(BASEURL,endpoint1,user_token)
    print('records_response.status_code',records_response2.status_code)
    if records_response2.status_code not in [200,201]:
        messages.error(request, f"Failed to fetch records. {records_response2.json()}", extra_tags="warning")
    else:
        clients = records_response2.json()
    endpoint2='projects/'    
    records_response2 = call_get_method(BASEURL,endpoint2,user_token)
    print('records_response.status_code',records_response2.status_code)
    if records_response2.status_code not in [200,201]:
        messages.error(request, f"Failed to fetch records. {records_response2.json()}", extra_tags="warning")
    else:
        entity = records_response2.json()
    form=ClientQueryForm(client_choices=clients,project_choices=entity)
    endpoint = 'clientquery/'
    if request.method=="POST":
        form=ClientQueryForm(request.POST,client_choices=clients,project_choices=entity)
        if form.is_valid():
            Output = form.cleaned_data
            Output['branch']=request.session['branch']
            Output['created_by']=request.session['user_data']['id']

            for field_name, field in form.fields.items():
                if isinstance(field.widget, forms.DateInput) or isinstance(field, forms.DateField) or isinstance(field, forms.DateTimeField):
                    if Output[field_name]:
                        del Output[field_name]
                        Output[field_name] = request.POST.get(field_name)
            json_data=json.dumps(Output)
            response = call_post_method_for_without_token(BASEURL,endpoint,json_data)
            if response.status_code not in [200,201]:
                print("error",response)
            else:
                messages.success(request,'Data Successfully Saved', extra_tags="success")
                return redirect('clientquery_list')
    else:
        print('errorss',form.errors)
    try:
        # getting data from backend
        records_response = call_get_method(BASEURL,endpoint,user_token)
        if records_response.status_code not in [200,201]:
            messages.error(request, f"Failed to fetch records. {records_response.json()}", extra_tags="warning")
        else:
            records = records_response.json()
            # You can pass 'records' to your template for rendering
            context = {'form': form, 'records': records}
            return render(request, 'clientquery.html', context)
    except Exception as e:
        print("An error occurred: Expecting value: line 1 column 1 (char 0)")
    context={
        'form':form,
    }
    return render(request,'clientquery.html',context)

def clientquery_list(request):
    user_token=request.session['user_token']
    endpoint = 'clientquery/'
        # getting data from backend
    records_response = call_get_method(BASEURL,endpoint,user_token)
    if records_response.status_code not in [200,201]:
            messages.error(request, f"Failed to fetch records. {records_response.json()}", extra_tags="warning")
    else:
            records = records_response.json()
            # You can pass 'records' to your template for rendering
            context = {'records': records}
            return render(request, 'clientquery_list.html', context)
    return render(request,'clientquery_list.html',context)

# edit function
def clientquery_edit(request,pk):
    endpoint1='clientprofile/'    
    records_response2 = call_get_method_without_token(BASEURL,endpoint1)
    print('records_response.status_code',records_response2.status_code)
    if records_response2.status_code not in [200,201]:
        messages.error(request, f"Failed to fetch records. {records_response2.json()}", extra_tags="warning")
    else:
        clients = records_response2.json()
    endpoint2='projects/'    
    records_response2 = call_get_method_without_token(BASEURL,endpoint2)
    print('records_response.status_code',records_response2.status_code)
    if records_response2.status_code not in [200,201]:
        messages.error(request, f"Failed to fetch records. {records_response2.json()}", extra_tags="warning")
    else:
        entity = records_response2.json()

    clientquery = call_get_method_without_token(BASEURL, f'clientquery/{pk}/')
    
    if clientquery.status_code in [200,201]:
        clientquery_data = clientquery.json()
    else:
        print('error------',clientquery)
        messages.error(request, 'Failed to retrieve data for clientquery. Please check your connection and try again.', extra_tags='warning')
        return redirect('clientquery')

    if request.method=="POST":
        form=ClientQueryForm(request.POST, initial=clientquery_data,client_choices=clients,project_choices=entity)
        if form.is_valid():
            updated_data = form.cleaned_data
            for field_name, field in form.fields.items():
                if isinstance(field.widget, forms.DateInput) or isinstance(field, forms.DateField) or isinstance(field, forms.DateTimeField):
                    if updated_data[field_name]:
                        del updated_data[field_name]
                        updated_data[field_name] = request.POST.get(field_name)
            # Serialize the updated data as JSON
            json_data = json.dumps(updated_data)
            response = call_put_method_without_token(BASEURL, f'clientquery/{pk}/', json_data)

            if response.status_code in [200,201]: 
                messages.success(request, 'Your data has been successfully saved', extra_tags='success')
                return redirect('clientquery') 
            else:
                error_message = response.json()
                messages.error(request, f"Oops..! {error_message}", extra_tags='warning')
        else:
            print("An error occurred: Expecting value: line 1 column 1 (char 0)")
    else:
        form = ClientQueryForm(initial=clientquery_data,client_choices=clients,project_choices=entity)

    context={
        'form':form,
    }
    return render(request,'clientquery_edit.html',context)

def clientquery_delete(request,pk):
    end_point = f'clientquery/{pk}/'
    clientquery = call_delete_method_without_token(BASEURL, end_point)
    if clientquery.status_code not in [200,201]:
        messages.error(request, 'Failed to delete data for clientquery. Please try again.', extra_tags='warning')
        return redirect('clientquery')
    else:
        messages.success(request, 'Successfully deleted data for clientquery', extra_tags='success')
        return redirect('clientquery')

# create and view table function
def timesheet(request):
    user_token=request.session['user_token']

    endpoint1='UserManagement/user/'    
    records_response2 = call_get_method(BASEURL,endpoint1,user_token)
    print('records_response.status_code',records_response2.status_code)
    if records_response2.status_code not in [200,201]:
        messages.error(request, f"Failed to fetch records. {records_response2.json()}", extra_tags="warning")
    else:
        clients = records_response2.json()
    endpoint2='projects/'    
    records_response2 = call_get_method_without_token(BASEURL,endpoint2)
    print('records_response.status_code',records_response2.status_code)
    if records_response2.status_code not in [200,201]:
        messages.error(request, f"Failed to fetch records. {records_response2.json()}", extra_tags="warning")
    else:
        entity = records_response2.json()
    form=TimeSheetForm(employee_choices=clients,project_choices=entity)
    endpoint = 'timesheet/'
    if request.method=="POST":
        form=TimeSheetForm(request.POST,employee_choices=clients,project_choices=entity)
        if form.is_valid():
            Output = form.cleaned_data
            Output['branch']=request.session['branch']
            Output['created_by']=request.session['user_data']['id']

            for field_name, field in form.fields.items():
                if isinstance(field.widget, forms.DateInput) or isinstance(field, forms.DateField) or isinstance(field, forms.DateTimeField):
                    if Output[field_name]:
                        del Output[field_name]
                        Output[field_name] = request.POST.get(field_name)
            json_data=json.dumps(Output)
            response = call_post_method_for_without_token(BASEURL,endpoint,json_data)
            if response.status_code not in [200,201]:
                print("error",response)
            else:
                messages.success(request,'Data Successfully Saved', extra_tags="success")
                return redirect('timesheet_list')
    else:
        print('errorss',form.errors)
    context={
        'form':form,
    }
    return render(request,'timesheet.html',context)



def timesheet_list(request):
    user_token=request.session['user_token']
    endpoint = 'timesheet/'
        # getting data from backend
    records_response = call_get_method_without_token(BASEURL,endpoint)
    if records_response.status_code not in [200,201]:
            messages.error(request, f"Failed to fetch records. {records_response.json()}", extra_tags="warning")
    else:
            records = records_response.json()
            # You can pass 'records' to your template for rendering
            context = {'records': records}
            return render(request, 'timesheet_list.html', context)
    return render(request,'timesheet_list.html',context)


# edit function
def timesheet_edit(request,pk):
    endpoint1='UserManagement/user/'    
    records_response2 = call_get_method_without_token(BASEURL,endpoint1)
    print('records_response.status_code',records_response2.status_code)
    if records_response2.status_code not in [200,201]:
        messages.error(request, f"Failed to fetch records. {records_response2.json()}", extra_tags="warning")
    else:
        clients = records_response2.json()
    endpoint2='projects/'    
    records_response2 = call_get_method_without_token(BASEURL,endpoint2)
    print('records_response.status_code',records_response2.status_code)
    if records_response2.status_code not in [200,201]:
        messages.error(request, f"Failed to fetch records. {records_response2.json()}", extra_tags="warning")
    else:
        entity = records_response2.json()
    timesheet = call_get_method_without_token(BASEURL, f'timesheet/{pk}/')
    
    if timesheet.status_code in [200,201]:
        timesheet_data = timesheet.json()
    else:
        print('error------',timesheet)
        messages.error(request, 'Failed to retrieve data for timesheet. Please check your connection and try again.', extra_tags='warning')
        return redirect('timesheet')

    if request.method=="POST":
        form=TimeSheetForm(request.POST, initial=timesheet_data,employee_choices=clients,project_choices=entity)
        if form.is_valid():
            updated_data = form.cleaned_data
            for field_name, field in form.fields.items():
                if isinstance(field.widget, forms.DateInput) or isinstance(field, forms.DateField) or isinstance(field, forms.DateTimeField):
                    if updated_data[field_name]:
                        del updated_data[field_name]
                        updated_data[field_name] = request.POST.get(field_name)
            # Serialize the updated data as JSON
            json_data = json.dumps(updated_data)
            response = call_put_method_without_token(BASEURL, f'timesheet/{pk}/', json_data)

            if response.status_code in [200,201]: 
                messages.success(request, 'Your data has been successfully saved', extra_tags='success')
                return redirect('timesheet') 
            else:
                error_message = response.json()
                messages.error(request, f"Oops..! {error_message}", extra_tags='warning')
        else:
            print("An error occurred: Expecting value: line 1 column 1 (char 0)")
    else:
        form = TimeSheetForm(initial=timesheet_data,employee_choices=clients,project_choices=entity)

    context={
        'form':form,
    }
    return render(request,'timesheet_edit.html',context)

def timesheet_delete(request,pk):
    end_point = f'timesheet/{pk}/'
    timesheet = call_delete_method_without_token(BASEURL, end_point)
    if timesheet.status_code not in [200,201]:
        messages.error(request, 'Failed to delete data for timesheet. Please try again.', extra_tags='warning')
        return redirect('timesheet')
    else:
        messages.success(request, 'Successfully deleted data for timesheet', extra_tags='success')
        return redirect('timesheet')

# create and view table function
def documentupload(request):
    endpoint1='documenttype/'    
    records_response2 = call_get_method_without_token(BASEURL,endpoint1)
    print('records_response.status_code',records_response2.status_code)
    if records_response2.status_code not in [200,201]:
        messages.error(request, f"Failed to fetch records. {records_response2.json()}", extra_tags="warning")
    else:
        clients = records_response2.json()
    print('----',clients)
    endpoint2='customdocumententity/'    
    records_response2 = call_get_method_without_token(BASEURL,endpoint2)
    print('records_response.status_code',records_response2.status_code)
    if records_response2.status_code not in [200,201]:
        messages.error(request, f"Failed to fetch records. {records_response2.json()}", extra_tags="warning")
    else:
        entity = records_response2.json()
    endpoint3='foldermaster/'    
    records_response2 = call_get_method_without_token(BASEURL,endpoint3)
    print('records_response.status_code',records_response2.status_code)
    if records_response2.status_code not in [200,201]:
        messages.error(request, f"Failed to fetch records. {records_response2.json()}", extra_tags="warning")
    else:
        folder = records_response2.json()
    form=DocumentUploadForm(document_choices=clients,entity_choices=entity,folder_choices=folder)
    endpoint = 'documentupload/'
    if request.method=="POST":
        form=DocumentUploadForm(request.POST,request.FILES,document_choices=clients,entity_choices=entity,folder_choices=folder)
        if form.is_valid():
            Output = form.cleaned_data
            Output['branch']=request.session['branch']
            Output['created_by']=request.session['user_data']['id']

            for field_name, field in form.fields.items():
                if isinstance(field.widget, forms.DateInput) or isinstance(field, forms.DateField) or isinstance(field, forms.DateTimeField):
                    if Output[field_name]:
                        del Output[field_name]
                        Output[field_name] = request.POST.get(field_name)
            # json_data=json.dumps(Output)
            # response = call_post_method_for_without_token(BASEURL,endpoint,json_data)
            # if response.status_code not in [200,201]:
            #     print("error",response)

            cleaned_data = form.cleaned_data
            files, cleaned_data = image_filescreate(cleaned_data)
            json_data = cleaned_data if files else json.dumps(cleaned_data)
            print('==json_data==,',json_data)
            response = call_post_method_with_token_v2(BASEURL,endpoint,json_data,files)
            print('==response==',response)
            if response['status_code'] == 1:
                print("error",response)
            else:
                messages.success(request,'Data Successfully Saved', extra_tags="success")
                return redirect('documentupload_list')
        else:
            print('errorss',form.errors)
    try:
        # getting data from backend
        records_response = call_get_method_without_token(BASEURL,endpoint)
        if records_response.status_code not in [200,201]:
            messages.error(request, f"Failed to fetch records. {records_response.json()}", extra_tags="warning")
        else:
            records = records_response.json()
            # You can pass 'records' to your template for rendering
            context = {'form': form, 'records': records}
            return render(request, 'documentupload.html', context)
    except Exception as e:
        print("An error occurred: Expecting value: line 1 column 1 (char 0)")
    context={
        'form':form,
    }
    return render(request,'documentupload.html',context)

def documentupload_list(request):
    user_token=request.session['user_token']
    endpoint = 'documentupload/'
        # getting data from backend
    records_response = call_get_method_without_token(BASEURL,endpoint)
    if records_response.status_code not in [200,201]:
            messages.error(request, f"Failed to fetch records. {records_response.json()}", extra_tags="warning")
    else:
            records = records_response.json()
            # You can pass 'records' to your template for rendering
            context = {'records': records}
            return render(request, 'documentupload_list.html', context)
    return render(request,'documentupload_list.html',context)

# edit function
def documentupload_edit(request,pk):
    endpoint1='documenttype/'    
    records_response2 = call_get_method_without_token(BASEURL,endpoint1)
    print('records_response.status_code',records_response2.status_code)
    if records_response2.status_code not in [200,201]:
        messages.error(request, f"Failed to fetch records. {records_response2.json()}", extra_tags="warning")
    else:
        clients = records_response2.json()
    endpoint2='customdocumententity/'    
    records_response2 = call_get_method_without_token(BASEURL,endpoint2)
    print('records_response.status_code',records_response2.status_code)
    if records_response2.status_code not in [200,201]:
        messages.error(request, f"Failed to fetch records. {records_response2.json()}", extra_tags="warning")
    else:
        entity = records_response2.json()
    endpoint3='foldermaster/'    
    records_response2 = call_get_method_without_token(BASEURL,endpoint3)
    print('records_response.status_code',records_response2.status_code)
    if records_response2.status_code not in [200,201]:
        messages.error(request, f"Failed to fetch records. {records_response2.json()}", extra_tags="warning")
    else:
        folder = records_response2.json()
    documentupload = call_get_method_without_token(BASEURL, f'documentupload/{pk}/')
    
    if documentupload.status_code in [200,201]:
        documentupload_data = documentupload.json()
    else:
        print('error------',documentupload)
        messages.error(request, 'Failed to retrieve data for documentupload. Please check your connection and try again.', extra_tags='warning')
        return redirect('documentupload_list')

    if request.method=="POST":
        form=DocumentUploadForm(request.POST, initial=documentupload_data,document_choices=clients,entity_choices=entity,folder_choices=folder)
        if form.is_valid():
            updated_data = form.cleaned_data
            for field_name, field in form.fields.items():
                if isinstance(field.widget, forms.DateInput) or isinstance(field, forms.DateField) or isinstance(field, forms.DateTimeField):
                    if updated_data[field_name]:
                        del updated_data[field_name]
                        updated_data[field_name] = request.POST.get(field_name)
            # Serialize the updated data as JSON
            json_data = json.dumps(updated_data)
            response = call_put_method_without_token(BASEURL, f'documentupload/{pk}/', json_data)

            if response.status_code in [200,201]: 
                messages.success(request, 'Your data has been successfully saved', extra_tags='success')
                return redirect('documentupload_list') 
            else:
                error_message = response.json()
                messages.error(request, f"Oops..! {error_message}", extra_tags='warning')
        else:
            print("An error occurred: Expecting value: line 1 column 1 (char 0)")
    else:
        form = DocumentUploadForm(initial=documentupload_data,document_choices=clients,entity_choices=entity,folder_choices=folder)

    context={
        'form':form,
    }
    return render(request,'documentupload_edit.html',context)

def documentupload_delete(request,pk):
    end_point = f'documentupload/{pk}/'
    documentupload = call_delete_method_without_token(BASEURL, end_point)
    if documentupload.status_code not in [200,201]:
        messages.error(request, 'Failed to delete data for documentupload. Please try again.', extra_tags='warning')
        return redirect('documentupload_list')
    else:
        messages.success(request, 'Successfully deleted data for documentupload', extra_tags='success')
        return redirect('documentupload_list')

# create and view table function
def documentuploadaudit1(request):
    endpoint1='documenttype/'    
    records_response2 = call_get_method_without_token(BASEURL,endpoint1)
    print('records_response.status_code',records_response2.status_code)
    if records_response2.status_code not in [200,201]:
        messages.error(request, f"Failed to fetch records. {records_response2.json()}", extra_tags="warning")
    else:
        clients = records_response2.json()
    endpoint3='foldermaster/'    
    records_response2 = call_get_method_without_token(BASEURL,endpoint3)
    print('records_response.status_code',records_response2.status_code)
    if records_response2.status_code not in [200,201]:
        messages.error(request, f"Failed to fetch records. {records_response2.json()}", extra_tags="warning")
    else:
        folder = records_response2.json()
    form=DocumentUploadAudit1Form(document_choices=clients,folder_choices=folder)
    endpoint = 'documentuploadaudit1/'
    if request.method=="POST":
        form=DocumentUploadAudit1Form(request.POST,document_choices=clients,folder_choices=folder)
        if form.is_valid():
            Output = form.cleaned_data
            Output['branch']=request.session['branch']
            Output['created_by']=request.session['user_data']['id']

            for field_name, field in form.fields.items():
                if isinstance(field.widget, forms.DateInput) or isinstance(field, forms.DateField) or isinstance(field, forms.DateTimeField):
                    if Output[field_name]:
                        del Output[field_name]
                        Output[field_name] = request.POST.get(field_name)
            json_data=json.dumps(Output)
            response = call_post_method_for_without_token(BASEURL,endpoint,json_data)
            if response.status_code not in [200,201]:
                print("error",response)
            else:
                messages.success(request,'Data Successfully Saved', extra_tags="success")
                return redirect('documentuploadaudit1_list')
    else:
        print('errorss',form.errors)
    try:
        # getting data from backend
        records_response = call_get_method_without_token(BASEURL,endpoint)
        if records_response.status_code not in [200,201]:
            messages.error(request, f"Failed to fetch records. {records_response.json()}", extra_tags="warning")
        else:
            records = records_response.json()
            # You can pass 'records' to your template for rendering
            context = {'form': form, 'records': records}
            return render(request, 'documentuploadaudit1.html', context)
    except Exception as e:
        print("An error occurred: Expecting value: line 1 column 1 (char 0)")
    context={
        'form':form,
    }
    return render(request,'documentuploadaudit1.html',context)

def documentuploadaudit1_list(request):
    user_token=request.session['user_token']
    endpoint = 'documentuploadaudit1/'
        # getting data from backend
    records_response = call_get_method_without_token(BASEURL,endpoint)
    if records_response.status_code not in [200,201]:
            messages.error(request, f"Failed to fetch records. {records_response.json()}", extra_tags="warning")
    else:
            records = records_response.json()
            # You can pass 'records' to your template for rendering
            context = {'records': records}
            return render(request, 'documentuploadaudit1_list.html', context)
    return render(request,'documentuploadaudit1_list.html',context)

# edit function
def documentuploadaudit1_edit(request,pk):
    endpoint1='documenttype/'    
    records_response2 = call_get_method_without_token(BASEURL,endpoint1)
    print('records_response.status_code',records_response2.status_code)
    if records_response2.status_code not in [200,201]:
        messages.error(request, f"Failed to fetch records. {records_response2.json()}", extra_tags="warning")
    else:
        clients = records_response2.json()
    endpoint3='foldermaster/'    
    records_response2 = call_get_method_without_token(BASEURL,endpoint3)
    print('records_response.status_code',records_response2.status_code)
    if records_response2.status_code not in [200,201]:
        messages.error(request, f"Failed to fetch records. {records_response2.json()}", extra_tags="warning")
    else:
        folder = records_response2.json()
    documentuploadaudit1 = call_get_method_without_token(BASEURL, f'documentuploadaudit1/{pk}/')
    
    if documentuploadaudit1.status_code in [200,201]:
        documentuploadaudit1_data = documentuploadaudit1.json()
    else:
        print('error------',documentuploadaudit1)
        messages.error(request, 'Failed to retrieve data for documentuploadaudit1. Please check your connection and try again.', extra_tags='warning')
        return redirect('documentuploadaudit1')

    if request.method=="POST":
        form=DocumentUploadAudit1Form(request.POST, initial=documentuploadaudit1_data,document_choices=clients,folder_choices=folder)
        if form.is_valid():
            updated_data = form.cleaned_data
            for field_name, field in form.fields.items():
                if isinstance(field.widget, forms.DateInput) or isinstance(field, forms.DateField) or isinstance(field, forms.DateTimeField):
                    if updated_data[field_name]:
                        del updated_data[field_name]
                        updated_data[field_name] = request.POST.get(field_name)
            # Serialize the updated data as JSON
            json_data = json.dumps(updated_data)
            response = call_put_method_without_token(BASEURL, f'documentuploadaudit1/{pk}/', json_data)

            if response.status_code in [200,201]: 
                messages.success(request, 'Your data has been successfully saved', extra_tags='success')
                return redirect('documentuploadaudit1') 
            else:
                error_message = response.json()
                messages.error(request, f"Oops..! {error_message}", extra_tags='warning')
        else:
            print("An error occurred: Expecting value: line 1 column 1 (char 0)")
    else:
        form = DocumentUploadAudit1Form(initial=documentuploadaudit1_data,document_choices=clients,folder_choices=folder)

    context={
        'form':form,
    }
    return render(request,'documentuploadaudit1_edit.html',context)

def documentuploadaudit1_delete(request,pk):
    end_point = f'documentuploadaudit1/{pk}/'
    documentuploadaudit1 = call_delete_method_without_token(BASEURL, end_point)
    if documentuploadaudit1.status_code not in [200,201]:
        messages.error(request, 'Failed to delete data for documentuploadaudit1. Please try again.', extra_tags='warning')
        return redirect('documentuploadaudit1')
    else:
        messages.success(request, 'Successfully deleted data for documentuploadaudit1', extra_tags='success')
        return redirect('documentuploadaudit1')

# create and view table function
def documentuploadhistory1(request):
    endpoint1='documenttype/'    
    records_response2 = call_get_method_without_token(BASEURL,endpoint1)
    print('records_response.status_code',records_response2.status_code)
    if records_response2.status_code not in [200,201]:
        messages.error(request, f"Failed to fetch records. {records_response2.json()}", extra_tags="warning")
    else:
        clients = records_response2.json()
    endpoint3='foldermaster/'    
    records_response2 = call_get_method_without_token(BASEURL,endpoint3)
    print('records_response.status_code',records_response2.status_code)
    if records_response2.status_code not in [200,201]:
        messages.error(request, f"Failed to fetch records. {records_response2.json()}", extra_tags="warning")
    else:
        folder = records_response2.json()
    form=DocumentUploadHistory1Form(document_choices=clients,folder_choices=folder)
    endpoint = 'documentuploadhistory1/'
    if request.method=="POST":
        form=DocumentUploadHistory1Form(request.POST,document_choices=clients,folder_choices=folder)
        if form.is_valid():
            Output = form.cleaned_data
            Output['branch']=request.session['branch']
            Output['created_by']=request.session['user_data']['id']

            for field_name, field in form.fields.items():
                if isinstance(field.widget, forms.DateInput) or isinstance(field, forms.DateField) or isinstance(field, forms.DateTimeField):
                    if Output[field_name]:
                        del Output[field_name]
                        Output[field_name] = request.POST.get(field_name)
            json_data=json.dumps(Output)
            response = call_post_method_for_without_token(BASEURL,endpoint,json_data)
            if response.status_code not in [200,201]:
                print("error",response)
            else:
                messages.success(request,'Data Successfully Saved', extra_tags="success")
                return redirect('documentuploadhistory1_list')
    else:
        print('errorss',form.errors)
    try:
        # getting data from backend
        records_response = call_get_method_without_token(BASEURL,endpoint)
        if records_response.status_code not in [200,201]:
            messages.error(request, f"Failed to fetch records. {records_response.json()}", extra_tags="warning")
        else:
            records = records_response.json()
            # You can pass 'records' to your template for rendering
            context = {'form': form, 'records': records}
            return render(request, 'documentuploadhistory1.html', context)
    except Exception as e:
        print("An error occurred: Expecting value: line 1 column 1 (char 0)")
    context={
        'form':form,
    }
    return render(request,'documentuploadhistory1.html',context)

def documentuploadhistory1_list(request):
    user_token=request.session['user_token']
    endpoint = 'documentuploadhistory1/'
        # getting data from backend
    records_response = call_get_method_without_token(BASEURL,endpoint)
    if records_response.status_code not in [200,201]:
            messages.error(request, f"Failed to fetch records. {records_response.json()}", extra_tags="warning")
    else:
            records = records_response.json()
            # You can pass 'records' to your template for rendering
            context = {'records': records}
            return render(request, 'documentuploadhistory1_list.html', context)
    return render(request,'documentuploadhistory1_list.html',context)

# edit function
def documentuploadhistory1_edit(request,pk):
    endpoint1='documenttype/'    
    records_response2 = call_get_method_without_token(BASEURL,endpoint1)
    print('records_response.status_code',records_response2.status_code)
    if records_response2.status_code not in [200,201]:
        messages.error(request, f"Failed to fetch records. {records_response2.json()}", extra_tags="warning")
    else:
        clients = records_response2.json()
    endpoint3='foldermaster/'    
    records_response2 = call_get_method_without_token(BASEURL,endpoint3)
    print('records_response.status_code',records_response2.status_code)
    if records_response2.status_code not in [200,201]:
        messages.error(request, f"Failed to fetch records. {records_response2.json()}", extra_tags="warning")
    else:
        folder = records_response2.json()
    documentuploadhistory1 = call_get_method_without_token(BASEURL, f'documentuploadhistory1/{pk}/')
    
    if documentuploadhistory1.status_code in [200,201]:
        documentuploadhistory1_data = documentuploadhistory1.json()
    else:
        print('error------',documentuploadhistory1)
        messages.error(request, 'Failed to retrieve data for documentuploadhistory1. Please check your connection and try again.', extra_tags='warning')
        return redirect('documentuploadhistory1')

    if request.method=="POST":
        form=DocumentUploadHistory1Form(request.POST, initial=documentuploadhistory1_data,document_choices=clients,folder_choices=folder)
        if form.is_valid():
            updated_data = form.cleaned_data
            for field_name, field in form.fields.items():
                if isinstance(field.widget, forms.DateInput) or isinstance(field, forms.DateField) or isinstance(field, forms.DateTimeField):
                    if updated_data[field_name]:
                        del updated_data[field_name]
                        updated_data[field_name] = request.POST.get(field_name)
            # Serialize the updated data as JSON
            json_data = json.dumps(updated_data)
            response = call_put_method_without_token(BASEURL, f'documentuploadhistory1/{pk}/', json_data)

            if response.status_code in [200,201]: 
                messages.success(request, 'Your data has been successfully saved', extra_tags='success')
                return redirect('documentuploadhistory1') 
            else:
                error_message = response.json()
                messages.error(request, f"Oops..! {error_message}", extra_tags='warning')
        else:
            print("An error occurred: Expecting value: line 1 column 1 (char 0)")
    else:
        form = DocumentUploadHistory1Form(initial=documentuploadhistory1_data,document_choices=clients,folder_choices=folder)

    context={
        'form':form,
    }
    return render(request,'documentuploadhistory1_edit.html',context)

def documentuploadhistory1_delete(request,pk):
    end_point = f'documentuploadhistory1/{pk}/'
    documentuploadhistory1 = call_delete_method_without_token(BASEURL, end_point)
    if documentuploadhistory1.status_code not in [200,201]:
        messages.error(request, 'Failed to delete data for documentuploadhistory1. Please try again.', extra_tags='warning')
        return redirect('documentuploadhistory1')
    else:
        messages.success(request, 'Successfully deleted data for documentuploadhistory1', extra_tags='success')
        return redirect('documentuploadhistory1')

# create and view table function
def userprofile(request):
    user_token=request.session['user_token']
    endpoint2='UserManagement/user/'    
    records_response2 = call_get_method(BASEURL,endpoint2,user_token)
    print('records_response.status_code',records_response2.status_code)
    if records_response2.status_code not in [200,201]:
        messages.error(request, f"Failed to fetch records. {records_response2.json()}", extra_tags="warning")
    else:
        clients = records_response2.json()
    # endpoint3='UserManagement/role/'    
    # records_response2 = call_get_method_without_token(BASEURL,endpoint3)
    # print('records_response.status_code',records_response2.status_code)
    # if records_response2.status_code not in [200,201]:
    #     messages.error(request, f"Failed to fetch records. {records_response2.json()}", extra_tags="warning")
    # else:
    #     folder = records_response2.json()
    form=UserProfileForm(user_choices=clients)
    endpoint = 'userprofile/'
    if request.method=="POST":
        form=UserProfileForm(request.POST,user_choices=clients)
        if form.is_valid():
            Output = form.cleaned_data
            Output['branch']=request.session['branch']

            for field_name, field in form.fields.items():
                if isinstance(field.widget, forms.DateInput) or isinstance(field, forms.DateField) or isinstance(field, forms.DateTimeField):
                    if Output[field_name]:
                        del Output[field_name]
                        Output[field_name] = request.POST.get(field_name)
            json_data=json.dumps(Output)
            print('------',user_token)
            response = call_post_with_method(BASEURL,endpoint,json_data,user_token)
            if response.status_code not in [200,201]:
                print("error",response)
            else:
                messages.success(request,'Data Successfully Saved', extra_tags="success")
                return redirect('userprofile_list')
    else:
        print('errorss',form.errors)
    try:
        # getting data from backend
        records_response = call_get_method_without_token(BASEURL,endpoint)
        if records_response.status_code not in [200,201]:
            messages.error(request, f"Failed to fetch records. {records_response.json()}", extra_tags="warning")
        else:
            records = records_response.json()
            # You can pass 'records' to your template for rendering
            context = {'form': form, 'records': records}
            return render(request, 'userprofile.html', context)
    except Exception as e:
        print("An error occurred: Expecting value: line 1 column 1 (char 0)")
    context={
        'form':form,
    }
    return render(request,'userprofile.html',context)

def userprofile_list(request):
    user_token=request.session['user_token']
    endpoint = 'userprofile/'
    try:
        # getting data from backend
        records_response = call_get_method(BASEURL,endpoint,user_token)
        if records_response.status_code not in [200,201]:
            messages.error(request, f"Failed to fetch records. {records_response.json()}", extra_tags="warning")
        else:
            records = records_response.json()
            # You can pass 'records' to your template for rendering
            context = {'records': records}
            return render(request, 'userprofile_list.html', context)
    except Exception as e:
        print("An error occurred: Expecting value: line 1 column 1 (char 0)")
    return render(request,'userprofile_list.html')

# edit function
def userprofile_edit(request,pk):
    user_token=request.session['user_token']

    endpoint1='UserManagement/user/'    
    records_response2 = call_get_method(BASEURL,endpoint1,user_token)
    print('records_response.status_code',records_response2.status_code)
    if records_response2.status_code not in [200,201]:
        messages.error(request, f"Failed to fetch records. {records_response2.json()}", extra_tags="warning")
    else:
        clients = records_response2.json()
    # endpoint3='UserManagement/role/'    
    # records_response2 = call_get_method_without_token(BASEURL,endpoint3)
    # print('records_response.status_code',records_response2.status_code)
    # if records_response2.status_code not in [200,201]:
    #     messages.error(request, f"Failed to fetch records. {records_response2.json()}", extra_tags="warning")
    # else:
    #     folder = records_response2.json()
    userprofile = call_get_method(BASEURL, f'userprofile/{pk}/',user_token)
    
    if userprofile.status_code in [200,201]:
        userprofile_data = userprofile.json()
    else:
        print('error------',userprofile)
        messages.error(request, 'Failed to retrieve data for userprofile. Please check your connection and try again.', extra_tags='warning')
        return redirect('userprofile')

    if request.method=="POST":
        form=UserProfileForm(request.POST, initial=userprofile_data,user_choices=clients,)
        if form.is_valid():
            updated_data = form.cleaned_data
            for field_name, field in form.fields.items():
                if isinstance(field.widget, forms.DateInput) or isinstance(field, forms.DateField) or isinstance(field, forms.DateTimeField):
                    if updated_data[field_name]:
                        del updated_data[field_name]
                        updated_data[field_name] = request.POST.get(field_name)
            # Serialize the updated data as JSON
            json_data = json.dumps(updated_data)
            response = call_put_method_without_token(BASEURL, f'userprofile/{pk}/', json_data)

            if response.status_code in [200,201]: 
                messages.success(request, 'Your data has been successfully saved', extra_tags='success')
                return redirect('userprofile_list') 
            else:
                error_message = response.json()
                messages.error(request, f"Oops..! {error_message}", extra_tags='warning')
        else:
            print("An error occurred: Expecting value: line 1 column 1 (char 0)")
    else:
        form = UserProfileForm(initial=userprofile_data,user_choices=clients,)

    context={
        'form':form,
    }
    return render(request,'userprofile_edit.html',context)

def userprofile_delete(request,pk):
    end_point = f'userprofile/{pk}/'
    userprofile = call_delete_method_without_token(BASEURL, end_point)
    if userprofile.status_code not in [200,201]:
        messages.error(request, 'Failed to delete data for userprofile. Please try again.', extra_tags='warning')
        return redirect('userprofile_list')
    else:
        messages.success(request, 'Successfully deleted data for userprofile', extra_tags='success')
        return redirect('userprofile_list')


# create and view table function
def documentaccess(request):
    user_token=request.session['user_token']
    endpoint1='UserManagement/user/'    
    records_response2 = call_get_method(BASEURL,endpoint1,user_token)
    print('records_response.status_code',records_response2.status_code)
    if records_response2.status_code not in [200,201]:
        messages.error(request, f"Failed to fetch records. {records_response2.json()}", extra_tags="warning")
    else:
        clients = records_response2.json()
    endpoint3='documentupload/'    
    records_response2 = call_get_method_without_token(BASEURL,endpoint3)
    print('records_response.status_code',records_response2.status_code)
    if records_response2.status_code not in [200,201]:
        messages.error(request, f"Failed to fetch records. {records_response2.json()}", extra_tags="warning")
    else:
        folder = records_response2.json()
    form=DocumentAccessForm(user_choices=clients,document_choices=folder)
    endpoint = 'documentaccess/'
    if request.method=="POST":
        form=DocumentAccessForm(request.POST,user_choices=clients,document_choices=folder)
        if form.is_valid():
            Output = form.cleaned_data
            Output['branch']=request.session['branch']
            Output['created_by']=request.session['user_data']['id']

            for field_name, field in form.fields.items():
                if isinstance(field.widget, forms.DateInput) or isinstance(field, forms.DateField) or isinstance(field, forms.DateTimeField):
                    if Output[field_name]:
                        del Output[field_name]
                        Output[field_name] = request.POST.get(field_name)
            json_data=json.dumps(Output)
            response = call_post_method_for_without_token(BASEURL,endpoint,json_data)
            if response.status_code not in [200,201]:
                print("error",response)
            else:
                messages.success(request,'Data Successfully Saved', extra_tags="success")
                return redirect('documentaccess')
    else:
        print('errorss',form.errors)
    try:
        # getting data from backend
        records_response = call_get_method_without_token(BASEURL,endpoint)
        if records_response.status_code not in [200,201]:
            messages.error(request, f"Failed to fetch records. {records_response.json()}", extra_tags="warning")
        else:
            records = records_response.json()
            # You can pass 'records' to your template for rendering
            context = {'form': form, 'records': records}
            return render(request, 'documentaccess.html', context)
    except Exception as e:
        print("An error occurred: Expecting value: line 1 column 1 (char 0)")
    context={
        'form':form,
    }
    return render(request,'documentaccess.html',context)

def documentaccess_list(request):
    try:
        endpoint = 'documentaccess/'
        # getting data from backend
        records_response = call_get_method_without_token(BASEURL,endpoint)
        if records_response.status_code not in [200,201]:
            messages.error(request, f"Failed to fetch records. {records_response.json()}", extra_tags="warning")
        else:
            records = records_response.json()
            # You can pass 'records' to your template for rendering
            context = { 'records': records}
            return render(request, 'documentaccess_list.html', context)
    except Exception as e:
        print("An error occurred: Expecting value: line 1 column 1 (char 0)")
    return render(request,'documentaccess_list.html',context)

# edit function
def documentaccess_edit(request,pk):
    endpoint1='UserManagement/user/'    
    records_response2 = call_get_method_without_token(BASEURL,endpoint1)
    print('records_response.status_code',records_response2.status_code)
    if records_response2.status_code not in [200,201]:
        messages.error(request, f"Failed to fetch records. {records_response2.json()}", extra_tags="warning")
    else:
        clients = records_response2.json()
    endpoint3='documentupload/'    
    records_response2 = call_get_method_without_token(BASEURL,endpoint3)
    print('records_response.status_code',records_response2.status_code)
    if records_response2.status_code not in [200,201]:
        messages.error(request, f"Failed to fetch records. {records_response2.json()}", extra_tags="warning")
    else:
        folder = records_response2.json()
    documentaccess = call_get_method_without_token(BASEURL, f'documentaccess/{pk}/')
    
    if documentaccess.status_code in [200,201]:
        documentaccess_data = documentaccess.json()
    else:
        print('error------',documentaccess)
        messages.error(request, 'Failed to retrieve data for documentaccess. Please check your connection and try again.', extra_tags='warning')
        return redirect('documentaccess')

    if request.method=="POST":
        form=DocumentAccessForm(request.POST, initial=documentaccess_data,user_choices=clients,document_choices=folder)
        if form.is_valid():
            updated_data = form.cleaned_data
            for field_name, field in form.fields.items():
                if isinstance(field.widget, forms.DateInput) or isinstance(field, forms.DateField) or isinstance(field, forms.DateTimeField):
                    if updated_data[field_name]:
                        del updated_data[field_name]
                        updated_data[field_name] = request.POST.get(field_name)
            # Serialize the updated data as JSON
            json_data = json.dumps(updated_data)
            response = call_put_method_without_token(BASEURL, f'documentaccess/{pk}/', json_data)

            if response.status_code in [200,201]: 
                messages.success(request, 'Your data has been successfully saved', extra_tags='success')
                return redirect('documentaccess') 
            else:
                error_message = response.json()
                messages.error(request, f"Oops..! {error_message}", extra_tags='warning')
        else:
            print("An error occurred: Expecting value: line 1 column 1 (char 0)")
    else:
        form = DocumentAccessForm(initial=documentaccess_data,user_choices=clients,document_choices=folder)

    context={
        'form':form,
    }
    return render(request,'documentaccess_edit.html',context)

def documentaccess_delete(request,pk):
    end_point = f'documentaccess/{pk}/'
    documentaccess = call_delete_method_without_token(BASEURL, end_point)
    if documentaccess.status_code not in [200,201]:
        messages.error(request, 'Failed to delete data for documentaccess. Please try again.', extra_tags='warning')
        return redirect('documentaccess')
    else:
        messages.success(request, 'Successfully deleted data for documentaccess', extra_tags='success')
        return redirect('documentaccess')

# create and view table function
def filedownloadreason(request):
   
    endpoint3='documentupload/'    
    records_response2 = call_get_method_without_token(BASEURL,endpoint3)
    print('records_response.status_code',records_response2.status_code)
    if records_response2.status_code not in [200,201]:
        messages.error(request, f"Failed to fetch records. {records_response2.json()}", extra_tags="warning")
    else:
        folder = records_response2.json()
    form=FileDownloadReasonForm(document_choices=folder)
    endpoint = 'filedownloadreason/'
    if request.method=="POST":
        form=FileDownloadReasonForm(request.POST,document_choices=folder)
        if form.is_valid():
            Output = form.cleaned_data
            Output['branch']=request.session['branch']
            Output['created_by']=request.session['user_data']['id']

            for field_name, field in form.fields.items():
                if isinstance(field.widget, forms.DateInput) or isinstance(field, forms.DateField) or isinstance(field, forms.DateTimeField):
                    if Output[field_name]:
                        del Output[field_name]
                        Output[field_name] = request.POST.get(field_name)
            json_data=json.dumps(Output)
            response = call_post_method_for_without_token(BASEURL,endpoint,json_data)
            if response.status_code not in [200,201]:
                print("error",response)
            else:
                messages.success(request,'Data Successfully Saved', extra_tags="success")
                return redirect('filedownloadreason_list')
    else:
        print('errorss',form.errors)
    try:
        # getting data from backend
        records_response = call_get_method_without_token(BASEURL,endpoint)
        if records_response.status_code not in [200,201]:
            messages.error(request, f"Failed to fetch records. {records_response.json()}", extra_tags="warning")
        else:
            records = records_response.json()
            # You can pass 'records' to your template for rendering
            context = {'form': form, 'records': records}
            return render(request, 'filedownloadreason.html', context)
    except Exception as e:
        print("An error occurred: Expecting value: line 1 column 1 (char 0)")
    context={
        'form':form,
    }
    return render(request,'filedownloadreason.html',context)

def filedownloadreason_list(request):
    user_token=request.session['user_token']
    endpoint = 'filedownloadreason/'
        # getting data from backend
    records_response = call_get_method_without_token(BASEURL,endpoint)
    if records_response.status_code not in [200,201]:
            messages.error(request, f"Failed to fetch records. {records_response.json()}", extra_tags="warning")
    else:
            records = records_response.json()
            # You can pass 'records' to your template for rendering
            context = {'records': records}
            return render(request, 'filedownloadreason_list.html', context)
    return render(request,'filedownloadreason_list.html',context)

# edit function
def filedownloadreason_edit(request,pk):
    filedownloadreason = call_get_method_without_token(BASEURL, f'filedownloadreason/{pk}/')
    
    if filedownloadreason.status_code in [200,201]:
        filedownloadreason_data = filedownloadreason.json()
    else:
        print('error------',filedownloadreason)
        messages.error(request, 'Failed to retrieve data for filedownloadreason. Please check your connection and try again.', extra_tags='warning')
        return redirect('filedownloadreason')

    if request.method=="POST":
        form=FileDownloadReasonForm(request.POST, initial=filedownloadreason_data)
        if form.is_valid():
            updated_data = form.cleaned_data
            for field_name, field in form.fields.items():
                if isinstance(field.widget, forms.DateInput) or isinstance(field, forms.DateField) or isinstance(field, forms.DateTimeField):
                    if updated_data[field_name]:
                        del updated_data[field_name]
                        updated_data[field_name] = request.POST.get(field_name)
            # Serialize the updated data as JSON
            json_data = json.dumps(updated_data)
            response = call_put_method_without_token(BASEURL, f'filedownloadreason/{pk}/', json_data)

            if response.status_code in [200,201]: 
                messages.success(request, 'Your data has been successfully saved', extra_tags='success')
                return redirect('filedownloadreason') 
            else:
                error_message = response.json()
                messages.error(request, f"Oops..! {error_message}", extra_tags='warning')
        else:
            print("An error occurred: Expecting value: line 1 column 1 (char 0)")
    else:
        form = FileDownloadReasonForm(initial=filedownloadreason_data)

    context={
        'form':form,
    }
    return render(request,'filedownloadreason_edit.html',context)

def filedownloadreason_delete(request,pk):
    end_point = f'filedownloadreason/{pk}/'
    filedownloadreason = call_delete_method_without_token(BASEURL, end_point)
    if filedownloadreason.status_code not in [200,201]:
        messages.error(request, 'Failed to delete data for filedownloadreason. Please try again.', extra_tags='warning')
        return redirect('filedownloadreason')
    else:
        messages.success(request, 'Successfully deleted data for filedownloadreason', extra_tags='success')
        return redirect('filedownloadreason')

# create and view table function
def caseassignment(request):
    user_token=request.session['user_token']

    endpoint1='customer_user/'    
    records_response2 = call_get_method(BASEURL,endpoint1,user_token)
    print('records_response.status_code',records_response2.status_code)
    if records_response2.status_code not in [200,201]:
        messages.error(request, f"Failed to fetch records. {records_response2.json()}", extra_tags="warning")
    else:
        clients = records_response2.json()
    endpoint1='userprofile/'    
    records_response2 = call_get_method_without_token(BASEURL,endpoint1)
    print('userprofile',records_response2.json())
    if records_response2.status_code not in [200,201]:
        messages.error(request, f"Failed to fetch records. {records_response2.json()}", extra_tags="warning")
    else:
        Profiles = records_response2.json()
        print("Profiles",Profiles)

    endpoint3='loancase/'    
    records_response2 = call_get_method_without_token(BASEURL,endpoint3)
    print('records_response.status_code',records_response2.status_code)
    if records_response2.status_code not in [200,201]:
        messages.error(request, f"Failed to fetch records. {records_response2.json()}", extra_tags="warning")
    else:
        folder = records_response2.json()
        print("foldddd",folder)
    form=CaseAssignmentForm(user_choices=clients,case_choices=folder,assigned_to_choices=Profiles)
    endpoint = 'caseassignment/'
    if request.method=="POST":
        form=CaseAssignmentForm(request.POST,user_choices=clients,case_choices=folder,assigned_to_choices=Profiles)
        if form.is_valid():
            Output = form.cleaned_data
            Output['branch']=request.session['branch']

            for field_name, field in form.fields.items():
                if isinstance(field.widget, forms.DateInput) or isinstance(field, forms.DateField) or isinstance(field, forms.DateTimeField):
                    if Output[field_name]:
                        del Output[field_name]
                        Output[field_name] = request.POST.get(field_name)
            json_data=json.dumps(Output)
            response = call_post_method_for_without_token(BASEURL,endpoint,json_data)
            print('-----',response)
            if response.status_code not in [200,201]:
                print("error",response)
            else:
                messages.success(request,'Data Successfully Saved', extra_tags="success")
                return redirect('caseassignment_list')
    else:
        print('errorss',form.errors)
    try:
        # getting data from backend
        records_response = call_get_method_without_token(BASEURL,endpoint)
        if records_response.status_code not in [200,201]:
            messages.error(request, f"Failed to fetch records. {records_response.json()}", extra_tags="warning")
        else:
            records = records_response.json()
            # You can pass 'records' to your template for rendering
            context = {'form': form, 'records': records}
            return render(request, 'caseassignment.html', context)
    except Exception as e:
        print("An error occurred: Expecting value: line 1 column 1 (char 0)")
    context={
        'form':form,
    }
    return render(request,'caseassignment.html',context)

def caseassignment_list(request):
    try:
        user_token=request.session['user_token']
        endpoint = 'caseassignment/'
        records_response = call_get_method_without_token(BASEURL,endpoint)
        if records_response.status_code not in [200,201]:
            messages.error(request, f"Failed to fetch records. {records_response.json()}", extra_tags="warning")
        else:
            records = records_response.json()
            print('---',records)
            # You can pass 'records' to your template for rendering
            context = {'records': records}
            return render(request, 'caseassignment_list.html', context)
    except Exception as e:
        print("An error occurred: Expecting value: line 1 column 1 (char 0)")
    return render(request,'caseassignment_list.html')


# edit function
def caseassignment_edit(request,pk):
    user_token=request.session['user_token']
    endpoint1='customer_user/'    
    records_response2 = call_get_method_without_token(BASEURL,endpoint1)
    print('records_response.status_code',records_response2.status_code)
    if records_response2.status_code not in [200,201]:
        messages.error(request, f"Failed to fetch records. {records_response2.json()}", extra_tags="warning")
    else:
        clients = records_response2.json()
    endpoint1='userprofile/'    
    records_response2 = call_get_method_without_token(BASEURL,endpoint1)
    print('userprofile',records_response2.json())
    if records_response2.status_code not in [200,201]:
        messages.error(request, f"Failed to fetch records. {records_response2.json()}", extra_tags="warning")
    else:
        Profiles = records_response2.json()
        print("Profiles",Profiles)

    endpoint3='loancase/'    
    records_response2 = call_get_method_without_token(BASEURL,endpoint3)
    print('records_response.status_code',records_response2.status_code)
    if records_response2.status_code not in [200,201]:
        messages.error(request, f"Failed to fetch records. {records_response2.json()}", extra_tags="warning")
    else:
        folder = records_response2.json()
    caseassignment = call_get_method_without_token(BASEURL, f'caseassignment/{pk}/')
    
    if caseassignment.status_code in [200,201]:
        caseassignment_data = caseassignment.json()
    else:
        print('error------',caseassignment)
        messages.error(request, 'Failed to retrieve data for caseassignment. Please check your connection and try again.', extra_tags='warning')
        return redirect('caseassignment_list')
    endpoint4='userprofile/'    
    records_response2 = call_get_method(BASEURL,endpoint4,user_token)
    print('records_response.status_code',records_response2.status_code)
    if records_response2.status_code not in [200,201]:
        messages.error(request, f"Failed to fetch records. {records_response2.json()}", extra_tags="warning")
    else:
        users = records_response2.json()
    if request.method=="POST":
        form=CaseAssignmentForm(request.POST, initial=caseassignment_data,user_choices=clients,case_choices=folder,assigned_to_choices=Profiles)
        if form.is_valid():
            updated_data = form.cleaned_data
            for field_name, field in form.fields.items():
                if isinstance(field.widget, forms.DateInput) or isinstance(field, forms.DateField) or isinstance(field, forms.DateTimeField):
                    if updated_data[field_name]:
                        del updated_data[field_name]
                        updated_data[field_name] = request.POST.get(field_name)
            # Serialize the updated data as JSON
            json_data = json.dumps(updated_data)
            response = call_put_method_without_token(BASEURL, f'caseassignment/{pk}/', json_data)

            if response.status_code in [200,201]: 
                messages.success(request, 'Your data has been successfully saved', extra_tags='success')
                return redirect('caseassignment_list') 
            else:
                error_message = response.json()
                messages.error(request, f"Oops..! {error_message}", extra_tags='warning')
        else:
            print("An error occurred: Expecting value: line 1 column 1 (char 0)")
    else:
        form = CaseAssignmentForm(initial=caseassignment_data,user_choices=clients,case_choices=folder,assigned_to_choices=Profiles)

    context={
        'form':form,
    }
    return render(request,'caseassignment_edit.html',context)

def caseassignment_delete(request,pk):
    end_point = f'caseassignment/{pk}/'
    caseassignment = call_delete_method_without_token(BASEURL, end_point)
    if caseassignment.status_code not in [200,201]:
        messages.error(request, 'Failed to delete data for caseassignment. Please try again.', extra_tags='warning')
        return redirect('caseassignment_list')
    else:
        messages.success(request, 'Successfully deleted data for caseassignment', extra_tags='success')
        return redirect('caseassignment_list')

# create and view table function
def triogroupmember(request):
    user_token=request.session['user_token']
    endpoint1='trio_group_user/'    
    records_response2 = call_get_method(BASEURL,endpoint1,user_token)
    print('records_response.status_code',records_response2.status_code)
    if records_response2.status_code not in [200,201]:
        messages.error(request, f"Failed to fetch records. {records_response2.json()}", extra_tags="warning")
    else:
        clients = records_response2.json()
        print('---',clients)
    endpoint3='triogroup/'    
    records_response2 = call_get_method(BASEURL,endpoint3,user_token)
    print('records_response.status_code',records_response2.status_code)
    if records_response2.status_code not in [200,201]:
        messages.error(request, f"Failed to fetch records. {records_response2.json()}", extra_tags="warning")
    else:
        folder = records_response2.json()
    form=TRIOGroupMemberForm(user_choices=clients,case_choices=folder)
    endpoint = 'triogroupmember/'
    if request.method=="POST":
        form=TRIOGroupMemberForm(request.POST,user_choices=clients,case_choices=folder)
        if form.is_valid():
            Output = form.cleaned_data
            Output['branch']=request.session['branch']
            Output['created_by']=request.session['user_data']['id']

            for field_name, field in form.fields.items():
                if isinstance(field.widget, forms.DateInput) or isinstance(field, forms.DateField) or isinstance(field, forms.DateTimeField):
                    if Output[field_name]:
                        del Output[field_name]
                        Output[field_name] = request.POST.get(field_name)
            json_data=json.dumps(Output)
            response = call_post_method_for_without_token(BASEURL,endpoint,json_data)
            if response.status_code not in [200,201]:
                print("error",response)
                
            else:
                messages.success(request,'Data Successfully Saved', extra_tags="success")
                return redirect('triogroupmember_list')
    else:
        print('errorss',form.errors)
    try:
        # getting data from backend
        records_response = call_get_method(BASEURL,endpoint,user_token)
        if records_response.status_code not in [200,201]:
            messages.error(request, f"Failed to fetch records. {records_response.json()}", extra_tags="warning")
        else:
            records = records_response.json()
            # You can pass 'records' to your template for rendering
            context = {'form': form, 'records': records}
            return render(request, 'triogroupmember.html', context)
    except Exception as e:
        print("An error occurred: Expecting value: line 1 column 1 (char 0)")
    context={
        'form':form,
    }
    return render(request,'triogroupmember.html',context)

def triogroupmember_list(request):
    user_token=request.session['user_token']
    endpoint = 'triogroupmember/'
    try:
        # getting data from backend
        records_response = call_get_method(BASEURL,endpoint,user_token)
        if records_response.status_code not in [200,201]:
            messages.error(request, f"Failed to fetch records. {records_response.json()}", extra_tags="warning")
        else:
            records = records_response.json()
            print('---',records)
            # You can pass 'records' to your template for rendering
            context = {'records': records}
            return render(request, 'triogroupmember_list.html', context)
    except Exception as e:
        print("An error occurred: Expecting value: line 1 column 1 (char 0)")
    return render(request,'triogroupmember_list.html')

# edit function
def triogroupmember_edit(request,pk):
    user_token=request.session['user_token']
    endpoint1='userprofile/'    
    records_response2 = call_get_method(BASEURL,endpoint1,user_token)
    print('records_response.status_code',records_response2.status_code)
    if records_response2.status_code not in [200,201]:
        messages.error(request, f"Failed to fetch records. {records_response2.json()}", extra_tags="warning")
    else:
        clients = records_response2.json()
    endpoint3='triogroup/'    
    records_response2 = call_get_method(BASEURL,endpoint3,user_token)
    print('records_response.status_code',records_response2.status_code)
    if records_response2.status_code not in [200,201]:
        messages.error(request, f"Failed to fetch records. {records_response2.json()}", extra_tags="warning")
    else:
        folder = records_response2.json()
    triogroupmember = call_get_method(BASEURL, f'triogroupmember/{pk}/',user_token)
    print('------',triogroupmember.json())
    
    if triogroupmember.status_code in [200,201]:
        triogroupmember_data = triogroupmember.json()
    else:
        print('error------',triogroupmember)
        messages.error(request, 'Failed to retrieve data for triogroupmember. Please check your connection and try again.', extra_tags='warning')
        return redirect('triogroupmember_list')

    if request.method=="POST":
        form=TRIOGroupMemberForm(request.POST,initial=triogroupmember_data,user_choices=clients,case_choices=folder)
        print('Form initial data:', form.initial)

        if form.is_valid():
            updated_data = form.cleaned_data
            for field_name, field in form.fields.items():
                if isinstance(field.widget, forms.DateInput) or isinstance(field, forms.DateField) or isinstance(field, forms.DateTimeField):
                    if updated_data[field_name]:
                        del updated_data[field_name]
                        updated_data[field_name] = request.POST.get(field_name)
            # Serialize the updated data as JSON
            json_data = json.dumps(updated_data)
            response = call_put_method_without_token(BASEURL, f'triogroupmember/{pk}/', json_data)

            if response.status_code in [200,201]: 
                messages.success(request, 'Your data has been successfully saved', extra_tags='success')
                return redirect('triogroupmember_list') 
            else:
                error_message = response.json()
                messages.error(request, f"Oops..! {error_message}", extra_tags='warning')
        else:
            print("An error occurred: Expecting value: line 1 column 1 (char 0)")
    else:
        form = TRIOGroupMemberForm(initial=triogroupmember_data,user_choices=clients,case_choices=folder)
        print('Form initial data:', form.initial)

    context={
        'form':form,
    }
    return render(request,'triogroupmember_edit.html',context)

def triogroupmember_delete(request,pk):
    end_point = f'triogroupmember/{pk}/'
    triogroupmember = call_delete_method_without_token(BASEURL, end_point)
    if triogroupmember.status_code not in [200,201]:
        messages.error(request, 'Failed to delete data for triogroupmember. Please try again.', extra_tags='warning')
        return redirect('triogroupmember_list')
    else:
        messages.success(request, 'Successfully deleted data for triogroupmember', extra_tags='success')
        return redirect('triogroupmember_list')

# create and view table function
def trioprofile(request):
    user_token=request.session['user_token']
    endpoint2='trio_user/'    
    records_response2 = call_get_method(BASEURL,endpoint2,user_token)
    print('records_response.status_code',records_response2.status_code)
    if records_response2.status_code not in [200,201]:
        messages.error(request, f"Failed to fetch records. {records_response2.json()}", extra_tags="warning")
    else:
        clients = records_response2.json()
        print('--clients--',clients)
    endpoint3='tasktemplate/'    
    records_response2 = call_get_method(BASEURL,endpoint3,user_token)
    print('records_response.status_code',records_response2.status_code)
    if records_response2.status_code not in [200,201]:
        messages.error(request, f"Failed to fetch records. {records_response2.json()}", extra_tags="warning")
    else:
        folder = records_response2.json()
        print('folder',folder)
    endpoint = 'trioprofile/'

    form=TRIOProfileForm(user_choices=clients,task_template_choices=folder)
    if request.method=="POST":
        form=TRIOProfileForm(request.POST,user_choices=clients,task_template_choices=folder)
        if form.is_valid():
            Output = form.cleaned_data
            Output['branch']=request.session['branch']

            for field_name, field in form.fields.items():
                if isinstance(field.widget, forms.DateInput) or isinstance(field, forms.DateField) or isinstance(field, forms.DateTimeField):
                    if Output[field_name]:
                        del Output[field_name]
                        Output[field_name] = request.POST.get(field_name)
            json_data=json.dumps(Output)
            response = call_post_with_method(BASEURL,endpoint,json_data,user_token)
            if response.status_code not in [200,201]:
                print("error",response.json())
            else:
                messages.success(request,'Data Successfully Saved', extra_tags="success")
                return redirect('trioprofile_list')
    else:
        print('errorss',form.errors)
    try:
        # getting data from backend
        records_response = call_get_method_without_token(BASEURL,endpoint)
        if records_response.status_code not in [200,201]:
            messages.error(request, f"Failed to fetch records. {records_response.json()}", extra_tags="warning")
        else:
            records = records_response.json()
            # You can pass 'records' to your template for rendering
            context = {'form': form, 'records': records}
            return render(request, 'trioprofile.html', context)
    except Exception as e:
        print("An error occurred: Expecting value: line 1 column 1 (char 0)")
    context={
        'form':form,
    }
    return render(request,'trioprofile.html',context)

def trioprofile_list(request):
    user_token=request.session['user_token']
    endpoint = 'trioprofile/'
    try:
        # getting data from backend
        records_response = call_get_method(BASEURL,endpoint,user_token)
        if records_response.status_code not in [200,201]:
            messages.error(request, f"Failed to fetch records. {records_response.json()}", extra_tags="warning")
        else:
            records = records_response.json()
            print('records',records)
            # You can pass 'records' to your template for rendering
            context = {'records': records}
            return render(request, 'trioprofile_list.html', context)
    except Exception as e:
        print("An error occurred: Expecting value: line 1 column 1 (char 0)")
    return render(request,'trioprofile_list.html')

# edit function
def trioprofile_edit(request,pk):
    user_token=request.session['user_token']

    endpoint1='trio_user/'    
    records_response2 = call_get_method(BASEURL,endpoint1,user_token)
    print('records_response.status_code',records_response2.status_code)
    if records_response2.status_code not in [200,201]:
        messages.error(request, f"Failed to fetch records. {records_response2.json()}", extra_tags="warning")
    else:
        clients = records_response2.json()
        print('-clients-',clients)
    endpoint3='tasktemplate/'    
    records_response2 = call_get_method(BASEURL,endpoint3,user_token)
    print('records_response.status_code',records_response2.status_code)
    if records_response2.status_code not in [200,201]:
        messages.error(request, f"Failed to fetch records. {records_response2.json()}", extra_tags="warning")
    else:
        folder = records_response2.json()
    trioprofile = call_get_method(BASEURL, f'trioprofile/{pk}/',user_token)
    
    if trioprofile.status_code in [200,201]:
        trioprofile_data = trioprofile.json()
        print('profile data------',trioprofile_data)
        # Flatten initial data
        if isinstance(trioprofile_data.get('user'), dict):
            trioprofile_data['user'] = trioprofile_data['user']['id']
        if isinstance(trioprofile_data.get('task_template'), dict):
            trioprofile_data['task_template'] = trioprofile_data['task_template']['id']

    else:
        print('error------',trioprofile)
        messages.error(request, 'Failed to retrieve data for trioprofile. Please check your connection and try again.', extra_tags='warning')
        return redirect('trioprofile')

    if request.method=="POST":
        form=TRIOProfileForm(request.POST, initial=trioprofile_data,user_choices=clients,task_template_choices=folder)
        if form.is_valid():
            updated_data = form.cleaned_data
            for field_name, field in form.fields.items():
                if isinstance(field.widget, forms.DateInput) or isinstance(field, forms.DateField) or isinstance(field, forms.DateTimeField):
                    if updated_data[field_name]:
                        del updated_data[field_name]
                        updated_data[field_name] = request.POST.get(field_name)
            # Serialize the updated data as JSON
            json_data = json.dumps(updated_data)
            response = call_put_method_without_token(BASEURL, f'trioprofile/{pk}/', json_data)

            if response.status_code in [200,201]: 
                messages.success(request, 'Your data has been successfully saved', extra_tags='success')
                return redirect('trioprofile_list') 
            else:
                error_message = response.json()
                messages.error(request, f"Oops..! {error_message}", extra_tags='warning')
        else:
            print("An error occurred: Expecting value: line 1 column 1 (char 0)")
    else:
        form = TRIOProfileForm(initial=trioprofile_data,user_choices=clients,task_template_choices=folder)

    context={
        'form':form,
    }
    return render(request,'trioprofile_edit.html',context)

def trioprofile_delete(request,pk):
    end_point = f'trioprofile/{pk}/'
    trioprofile = call_delete_method_without_token(BASEURL, end_point)
    if trioprofile.status_code not in [200,201]:
        messages.error(request, 'Failed to delete data for trioprofile. Please try again.', extra_tags='warning')
        return redirect('trioprofile_list')
    else:
        messages.success(request, 'Successfully deleted data for trioprofile', extra_tags='success')
        return redirect('trioprofile_list')

# create and view table function
def finalreport(request):
    endpoint1='trioassignment/'    
    records_response2 = call_get_method_without_token(BASEURL,endpoint1)
    print('records_response.status_code',records_response2.status_code)
    if records_response2.status_code not in [200,201]:
        messages.error(request, f"Failed to fetch records. {records_response2.json()}", extra_tags="warning")
    else:
        clients = records_response2.json()
    form=FinalReportForm(role_choices=clients)
    endpoint = 'finalreport/'
    if request.method=="POST":
        form=FinalReportForm(request.POST,role_choices=clients)
        if form.is_valid():
            Output = form.cleaned_data
            Output['branch']=request.session['branch']
            Output['created_by']=request.session['user_data']['id']

            for field_name, field in form.fields.items():
                if isinstance(field.widget, forms.DateInput) or isinstance(field, forms.DateField) or isinstance(field, forms.DateTimeField):
                    if Output[field_name]:
                        del Output[field_name]
                        Output[field_name] = request.POST.get(field_name)
            json_data=json.dumps(Output)
            response = call_post_method_for_without_token(BASEURL,endpoint,json_data)
            if response.status_code not in [200,201]:
                print("error",response)
            else:
                messages.success(request,'Data Successfully Saved', extra_tags="success")
                return redirect('finalreport_list')
    else:
        print('errorss',form.errors)
    try:
        # getting data from backend
        records_response = call_get_method_without_token(BASEURL,endpoint)
        if records_response.status_code not in [200,201]:
            messages.error(request, f"Failed to fetch records. {records_response.json()}", extra_tags="warning")
        else:
            records = records_response.json()
            # You can pass 'records' to your template for rendering
            context = {'form': form, 'records': records}
            return render(request, 'finalreport.html', context)
    except Exception as e:
        print("An error occurred: Expecting value: line 1 column 1 (char 0)")
    context={
        'form':form,
    }
    return render(request,'finalreport.html',context)

def finalreport_list(request):
    endpoint = 'finalreport/'
    try:
        # getting data from backend
        records_response = call_get_method_without_token(BASEURL,endpoint)
        if records_response.status_code not in [200,201]:
            messages.error(request, f"Failed to fetch records. {records_response.json()}", extra_tags="warning")
        else:
            records = records_response.json()
            # You can pass 'records' to your template for rendering
            context = {'records': records}
            return render(request, 'finalreport_list.html', context)
    except Exception as e:
        print("An error occurred: Expecting value: line 1 column 1 (char 0)")
    return render(request,'finalreport_list.html')

# edit function
def finalreport_edit(request,pk):
    endpoint1='trioassignment/'    
    records_response2 = call_get_method_without_token(BASEURL,endpoint1)
    print('records_response.status_code',records_response2.status_code)
    if records_response2.status_code not in [200,201]:
        messages.error(request, f"Failed to fetch records. {records_response2.json()}", extra_tags="warning")
    else:
        clients = records_response2.json()
    finalreport = call_get_method_without_token(BASEURL, f'finalreport/{pk}/')
    
    if finalreport.status_code in [200,201]:
        finalreport_data = finalreport.json()
    else:
        print('error------',finalreport)
        messages.error(request, 'Failed to retrieve data for finalreport. Please check your connection and try again.', extra_tags='warning')
        return redirect('finalreport')

    if request.method=="POST":
        form=FinalReportForm(request.POST, initial=finalreport_data,role_choices=clients)
        if form.is_valid():
            updated_data = form.cleaned_data
            for field_name, field in form.fields.items():
                if isinstance(field.widget, forms.DateInput) or isinstance(field, forms.DateField) or isinstance(field, forms.DateTimeField):
                    if updated_data[field_name]:
                        del updated_data[field_name]
                        updated_data[field_name] = request.POST.get(field_name)
            # Serialize the updated data as JSON
            json_data = json.dumps(updated_data)
            response = call_put_method_without_token(BASEURL, f'finalreport/{pk}/', json_data)

            if response.status_code in [200,201]: 
                messages.success(request, 'Your data has been successfully saved', extra_tags='success')
                return redirect('finalreport') 
            else:
                error_message = response.json()
                messages.error(request, f"Oops..! {error_message}", extra_tags='warning')
        else:
            print("An error occurred: Expecting value: line 1 column 1 (char 0)")
    else:
        form = FinalReportForm(initial=finalreport_data,role_choices=clients)

    context={
        'form':form,
    }
    return render(request,'finalreport_edit.html',context)

def finalreport_delete(request,pk):
    end_point = f'finalreport/{pk}/'
    finalreport = call_delete_method_without_token(BASEURL, end_point)
    if finalreport.status_code not in [200,201]:
        messages.error(request, 'Failed to delete data for finalreport. Please try again.', extra_tags='warning')
        return redirect('finalreport')
    else:
        messages.success(request, 'Successfully deleted data for finalreport', extra_tags='success')
        return redirect('finalreport')

# create and view table function
def task(request):
    user_token=request.session['user_token']
    endpoint1='trioassignment/'    
    records_response2 = call_get_method(BASEURL,endpoint1,user_token)
    print('records_response.status_code',records_response2.status_code)
    if records_response2.status_code not in [200,201]:
        messages.error(request, f"Failed to fetch records. {records_response2.json()}", extra_tags="warning")
    else:
        clients = records_response2.json()
        print('clients)')
    endpoint1='tasktemplate/'    
    records_response2 = call_get_method(BASEURL,endpoint1,user_token)
    print('records_response.status_code',records_response2.status_code)
    if records_response2.status_code not in [200,201]:
        messages.error(request, f"Failed to fetch records. {records_response2.json()}", extra_tags="warning")
    else:
        tasktemplate = records_response2.json()
    endpoint1='trioprofile/'    
    records_response2 = call_get_method(BASEURL,endpoint1,user_token)
    print('records_response.status_code',records_response2.status_code)
    if records_response2.status_code not in [200,201]:
        messages.error(request, f"Failed to fetch records. {records_response2.json()}", extra_tags="warning")
    else:
        trioprofile = records_response2.json()
    form=TaskForm(assignment_choices=clients,template_choices=tasktemplate,assigned_to_choices=trioprofile)
    endpoint = 'task/'
    if request.method=="POST":
        form=TaskForm(request.POST,assignment_choices=clients,template_choices=tasktemplate,assigned_to_choices=trioprofile)
        if form.is_valid():
            Output = form.cleaned_data
            Output['branch']=request.session['branch']
            Output['created_by']=request.session['user_data']['id']

            for field_name, field in form.fields.items():
                if isinstance(field.widget, forms.DateInput) or isinstance(field, forms.DateField) or isinstance(field, forms.DateTimeField):
                    if Output[field_name]:
                        del Output[field_name]
                        Output[field_name] = request.POST.get(field_name)
            json_data=json.dumps(Output)
            response = call_post_method_for_without_token(BASEURL,endpoint,json_data)
            if response.status_code not in [200,201]:
                print("error",response)
            else:
                messages.success(request,'Data Successfully Saved', extra_tags="success")
                return redirect('task_list')
    else:
        print('errorss',form.errors)
    try:
        # getting data from backend
        records_response = call_get_method_without_token(BASEURL,endpoint)
        if records_response.status_code not in [200,201]:
            messages.error(request, f"Failed to fetch records. {records_response.json()}", extra_tags="warning")
        else:
            records = records_response.json()
            # You can pass 'records' to your template for rendering
            context = {'form': form, 'records': records}
            return render(request, 'task.html', context)
    except Exception as e:
        print("An error occurred: Expecting value: line 1 column 1 (char 0)")
    context={
        'form':form,
    }
    return render(request,'task.html',context)

def task_list(request):
    user_token=request.session['user_token']
    endpoint = 'task/'
    try:
        # getting data from backend
        records_response = call_get_method(BASEURL,endpoint,user_token)
        if records_response.status_code not in [200,201]:
            messages.error(request, f"Failed to fetch records. {records_response.json()}", extra_tags="warning")
        else:
            records = records_response.json()
            # You can pass 'records' to your template for rendering
            context = {'records': records}
            return render(request, 'task_list.html', context)
    except Exception as e:
        print("An error occurred: Expecting value: line 1 column 1 (char 0)")
    return render(request,'task_list.html')


# edit function
def task_edit(request,pk):
    user_token=request.session['user_token']
    endpoint1='trioassignment/'    
    records_response2 = call_get_method(BASEURL,endpoint1,user_token)
    print('records_response.status_code',records_response2.status_code)
    if records_response2.status_code not in [200,201]:
        messages.error(request, f"Failed to fetch records. {records_response2.json()}", extra_tags="warning")
    else:
        clients = records_response2.json()
    endpoint1='tasktemplate/'    
    records_response2 = call_get_method(BASEURL,endpoint1,user_token)
    print('records_response.status_code',records_response2.status_code)
    if records_response2.status_code not in [200,201]:
        messages.error(request, f"Failed to fetch records. {records_response2.json()}", extra_tags="warning")
    else:
        tasktemplate = records_response2.json()
    endpoint1='trioprofile/'    
    records_response2 = call_get_method(BASEURL,endpoint1,user_token)
    print('records_response.status_code',records_response2.status_code)
    if records_response2.status_code not in [200,201]:
        messages.error(request, f"Failed to fetch records. {records_response2.json()}", extra_tags="warning")
    else:
        trioprofile = records_response2.json()
    task = call_get_method(BASEURL, f'task/{pk}/',user_token)
    
    if task.status_code in [200,201]:
        task_data = task.json()
    else:
        print('error------',task)
        messages.error(request, 'Failed to retrieve data for task. Please check your connection and try again.', extra_tags='warning')
        return redirect('task')

    if request.method=="POST":
        form=TaskForm(request.POST, initial=task_data,assignment_choices=clients,template_choices=tasktemplate,assigned_to_choices=trioprofile)
        if form.is_valid():
            updated_data = form.cleaned_data
            for field_name, field in form.fields.items():
                if isinstance(field.widget, forms.DateInput) or isinstance(field, forms.DateField) or isinstance(field, forms.DateTimeField):
                    if updated_data[field_name]:
                        del updated_data[field_name]
                        updated_data[field_name] = request.POST.get(field_name)
            # Serialize the updated data as JSON
            json_data = json.dumps(updated_data)
            response = call_put_method_without_token(BASEURL, f'task/{pk}/', json_data)

            if response.status_code in [200,201]: 
                messages.success(request, 'Your data has been successfully saved', extra_tags='success')
                return redirect('task') 
            else:
                error_message = response.json()
                messages.error(request, f"Oops..! {error_message}", extra_tags='warning')
        else:
            print("An error occurred: Expecting value: line 1 column 1 (char 0)")
    else:
        form = TaskForm(initial=task_data,assignment_choices=clients,template_choices=tasktemplate,assigned_to_choices=trioprofile)

    context={
        'form':form,
    }
    return render(request,'task_edit.html',context)

def task_delete(request,pk):
    end_point = f'task/{pk}/'
    task = call_delete_method_without_token(BASEURL, end_point)
    if task.status_code not in [200,201]:
        messages.error(request, 'Failed to delete data for task. Please try again.', extra_tags='warning')
        return redirect('task')
    else:
        messages.success(request, 'Successfully deleted data for task', extra_tags='success')
        return redirect('task')

# create and view table function
def taskauditlog(request):
    endpoint1='task/'    
    records_response2 = call_get_method_without_token(BASEURL,endpoint1)
    print('records_response.status_code',records_response2.status_code)
    if records_response2.status_code not in [200,201]:
        messages.error(request, f"Failed to fetch records. {records_response2.json()}", extra_tags="warning")
    else:
        clients = records_response2.json()
    form=TaskAuditLogForm(task_choices=clients)
    endpoint = 'taskauditlog/'
    if request.method=="POST":
        form=TaskAuditLogForm(request.POST,task_choices=clients)
        if form.is_valid():
            Output = form.cleaned_data
            Output['branch']=request.session['branch']
            Output['created_by']=request.session['user_data']['id']

            for field_name, field in form.fields.items():
                if isinstance(field.widget, forms.DateInput) or isinstance(field, forms.DateField) or isinstance(field, forms.DateTimeField):
                    if Output[field_name]:
                        del Output[field_name]
                        Output[field_name] = request.POST.get(field_name)
            json_data=json.dumps(Output)
            response = call_post_method_for_without_token(BASEURL,endpoint,json_data)
            if response.status_code not in [200,201]:
                print("error",response)
            else:
                messages.success(request,'Data Successfully Saved', extra_tags="success")
                return redirect('taskauditlog_list')
    else:
        print('errorss',form.errors)
    try:
        # getting data from backend
        records_response = call_get_method_without_token(BASEURL,endpoint)
        if records_response.status_code not in [200,201]:
            messages.error(request, f"Failed to fetch records. {records_response.json()}", extra_tags="warning")
        else:
            records = records_response.json()
            # You can pass 'records' to your template for rendering
            context = {'form': form, 'records': records}
            return render(request, 'taskauditlog.html', context)
    except Exception as e:
        print("An error occurred: Expecting value: line 1 column 1 (char 0)")
    context={
        'form':form,
    }
    return render(request,'taskauditlog.html',context)

def taskauditlog_list(request):
    endpoint = 'taskauditlog/'
    try:
        # getting data from backend
        records_response = call_get_method_without_token(BASEURL,endpoint)
        if records_response.status_code not in [200,201]:
            messages.error(request, f"Failed to fetch records. {records_response.json()}", extra_tags="warning")
        else:
            records = records_response.json()
            # You can pass 'records' to your template for rendering
            context = {'records': records}
            return render(request, 'taskauditlog_list.html', context)
    except Exception as e:
        print("An error occurred: Expecting value: line 1 column 1 (char 0)")
    return render(request,'taskauditlog_list.html')

# edit function
def taskauditlog_edit(request,pk):
    endpoint1='task/'    
    records_response2 = call_get_method_without_token(BASEURL,endpoint1)
    print('records_response.status_code',records_response2.status_code)
    if records_response2.status_code not in [200,201]:
        messages.error(request, f"Failed to fetch records. {records_response2.json()}", extra_tags="warning")
    else:
        clients = records_response2.json()
    taskauditlog = call_get_method_without_token(BASEURL, f'taskauditlog/{pk}/')
    
    if taskauditlog.status_code in [200,201]:
        taskauditlog_data = taskauditlog.json()
    else:
        print('error------',taskauditlog)
        messages.error(request, 'Failed to retrieve data for taskauditlog. Please check your connection and try again.', extra_tags='warning')
        return redirect('taskauditlog')

    if request.method=="POST":
        form=TaskAuditLogForm(request.POST, initial=taskauditlog_data,task_choices=clients)
        if form.is_valid():
            updated_data = form.cleaned_data
            for field_name, field in form.fields.items():
                if isinstance(field.widget, forms.DateInput) or isinstance(field, forms.DateField) or isinstance(field, forms.DateTimeField):
                    if updated_data[field_name]:
                        del updated_data[field_name]
                        updated_data[field_name] = request.POST.get(field_name)
            # Serialize the updated data as JSON
            json_data = json.dumps(updated_data)
            response = call_put_method_without_token(BASEURL, f'taskauditlog/{pk}/', json_data)

            if response.status_code in [200,201]: 
                messages.success(request, 'Your data has been successfully saved', extra_tags='success')
                return redirect('taskauditlog') 
            else:
                error_message = response.json()
                messages.error(request, f"Oops..! {error_message}", extra_tags='warning')
        else:
            print("An error occurred: Expecting value: line 1 column 1 (char 0)")
    else:
        form = TaskAuditLogForm(initial=taskauditlog_data,task_choices=clients)

    context={
        'form':form,
    }
    return render(request,'taskauditlog_edit.html',context)

def taskauditlog_delete(request,pk):
    end_point = f'taskauditlog/{pk}/'
    taskauditlog = call_delete_method_without_token(BASEURL, end_point)
    if taskauditlog.status_code not in [200,201]:
        messages.error(request, 'Failed to delete data for taskauditlog. Please try again.', extra_tags='warning')
        return redirect('taskauditlog')
    else:
        messages.success(request, 'Successfully deleted data for taskauditlog', extra_tags='success')
        return redirect('taskauditlog')

# create and view table function
def taskdeliverable(request):
    endpoint1='task/'    
    records_response2 = call_get_method_without_token(BASEURL,endpoint1)
    print('records_response.status_code',records_response2.status_code)
    if records_response2.status_code not in [200,201]:
        messages.error(request, f"Failed to fetch records. {records_response2.json()}", extra_tags="warning")
    else:
        clients = records_response2.json()
    form=TaskDeliverableForm(task_choices=clients)
    endpoint = 'taskdeliverable/'
    if request.method=="POST":
        form=TaskDeliverableForm(request.POST,task_choices=clients)
        if form.is_valid():
            Output = form.cleaned_data
            Output['branch']=request.session['branch']
            Output['created_by']=request.session['user_data']['id']

            for field_name, field in form.fields.items():
                if isinstance(field.widget, forms.DateInput) or isinstance(field, forms.DateField) or isinstance(field, forms.DateTimeField):
                    if Output[field_name]:
                        del Output[field_name]
                        Output[field_name] = request.POST.get(field_name)
            json_data=json.dumps(Output)
            response = call_post_method_for_without_token(BASEURL,endpoint,json_data)
            if response.status_code not in [200,201]:
                print("error",response)
            else:
                messages.success(request,'Data Successfully Saved', extra_tags="success")
                return redirect('taskdeliverable_list')
    else:
        print('errorss',form.errors)
    try:
        # getting data from backend
        records_response = call_get_method_without_token(BASEURL,endpoint)
        if records_response.status_code not in [200,201]:
            messages.error(request, f"Failed to fetch records. {records_response.json()}", extra_tags="warning")
        else:
            records = records_response.json()
            # You can pass 'records' to your template for rendering
            context = {'form': form, 'records': records}
            return render(request, 'taskdeliverable.html', context)
    except Exception as e:
        print("An error occurred: Expecting value: line 1 column 1 (char 0)")
    context={
        'form':form,
    }
    return render(request,'taskdeliverable.html',context)

def taskdeliverable_list(request):
    endpoint = 'taskdeliverable/'
    try:
        # getting data from backend
        records_response = call_get_method_without_token(BASEURL,endpoint)
        if records_response.status_code not in [200,201]:
            messages.error(request, f"Failed to fetch records. {records_response.json()}", extra_tags="warning")
        else:
            records = records_response.json()
            # You can pass 'records' to your template for rendering
            context = {'records': records}
            return render(request, 'taskdeliverable_list.html', context)
    except Exception as e:
        print("An error occurred: Expecting value: line 1 column 1 (char 0)")
    return render(request,'taskdeliverable_list.html')

# edit function
def taskdeliverable_edit(request,pk):
    endpoint1='task/'    
    records_response2 = call_get_method_without_token(BASEURL,endpoint1)
    print('records_response.status_code',records_response2.status_code)
    if records_response2.status_code not in [200,201]:
        messages.error(request, f"Failed to fetch records. {records_response2.json()}", extra_tags="warning")
    else:
        clients = records_response2.json()
    taskdeliverable = call_get_method_without_token(BASEURL, f'taskdeliverable/{pk}/')
    
    if taskdeliverable.status_code in [200,201]:
        taskdeliverable_data = taskdeliverable.json()
    else:
        print('error------',taskdeliverable)
        messages.error(request, 'Failed to retrieve data for taskdeliverable. Please check your connection and try again.', extra_tags='warning')
        return redirect('taskdeliverable')

    if request.method=="POST":
        form=TaskDeliverableForm(request.POST, initial=taskdeliverable_data,task_choices=clients)
        if form.is_valid():
            updated_data = form.cleaned_data
            for field_name, field in form.fields.items():
                if isinstance(field.widget, forms.DateInput) or isinstance(field, forms.DateField) or isinstance(field, forms.DateTimeField):
                    if updated_data[field_name]:
                        del updated_data[field_name]
                        updated_data[field_name] = request.POST.get(field_name)
            # Serialize the updated data as JSON
            json_data = json.dumps(updated_data)
            response = call_put_method_without_token(BASEURL, f'taskdeliverable/{pk}/', json_data)

            if response.status_code in [200,201]: 
                messages.success(request, 'Your data has been successfully saved', extra_tags='success')
                return redirect('taskdeliverable') 
            else:
                error_message = response.json()
                messages.error(request, f"Oops..! {error_message}", extra_tags='warning')
        else:
            print("An error occurred: Expecting value: line 1 column 1 (char 0)")
    else:
        form = TaskDeliverableForm(initial=taskdeliverable_data,task_choices=clients)

    context={
        'form':form,
    }
    return render(request,'taskdeliverable_edit.html',context)

def taskdeliverable_delete(request,pk):
    end_point = f'taskdeliverable/{pk}/'
    taskdeliverable = call_delete_method_without_token(BASEURL, end_point)
    if taskdeliverable.status_code not in [200,201]:
        messages.error(request, 'Failed to delete data for taskdeliverable. Please try again.', extra_tags='warning')
        return redirect('taskdeliverable')
    else:
        messages.success(request, 'Successfully deleted data for taskdeliverable', extra_tags='success')
        return redirect('taskdeliverable')

# create and view table function
def tasktimesheet(request):
    user_token=request.session['user_token']
    # endpoint1='task/'    
    # records_response2 = call_get_method(BASEURL,endpoint1,user_token)
    # print('records_response.status_code',records_response2.status_code)
    # if records_response2.status_code not in [200,201]:
    #     messages.error(request, f"Failed to fetch records. {records_response2.json()}", extra_tags="warning")
    # else:
    #     task = records_response2.json()
    endpoint2='trioprofile/'    
    records_response2 = call_get_method(BASEURL,endpoint2,user_token)
    print('records_response.status_code',records_response2.status_code)
    if records_response2.status_code not in [200,201]:
        messages.error(request, f"Failed to fetch records. {records_response2.json()}", extra_tags="warning")
    else:
        clients = records_response2.json()
    form=TaskTimesheetForm(user_choices=clients)
    endpoint = 'tasktimesheet/'
    if request.method=="POST":
        form=TaskTimesheetForm(request.POST,user_choices=clients,)
        if form.is_valid():
            Output = form.cleaned_data
            Output['branch']=request.session['branch']
            Output['created_by']=request.session['user_data']['id']

            for field_name, field in form.fields.items():
                if isinstance(field.widget, forms.DateInput) or isinstance(field, forms.DateField) or isinstance(field, forms.DateTimeField):
                    if Output[field_name]:
                        del Output[field_name]
                        Output[field_name] = request.POST.get(field_name)
            json_data=json.dumps(Output)
            response = call_post_method_for_without_token(BASEURL,endpoint,json_data)
            if response.status_code not in [200,201]:
                print("error",response)
            else:
                messages.success(request,'Data Successfully Saved', extra_tags="success")
                return redirect('tasktimesheet_list')
    else:
        print('errorss',form.errors)
    try:
        # getting data from backend
        records_response = call_get_method_without_token(BASEURL,endpoint)
        if records_response.status_code not in [200,201]:
            messages.error(request, f"Failed to fetch records. {records_response.json()}", extra_tags="warning")
        else:
            records = records_response.json()
            # You can pass 'records' to your template for rendering
            context = {'form': form, 'records': records}
            return render(request, 'tasktimesheet.html', context)
    except Exception as e:
        print("An error occurred: Expecting value: line 1 column 1 (char 0)")
    context={
        'form':form,
    }
    return render(request,'tasktimesheet.html',context)

def tasktimesheet_list(request):
    user_token=request.session['user_token']

    endpoint = 'tasktimesheet/'
    try:
        # getting data from backend
        records_response = call_get_method(BASEURL,endpoint,user_token)
        if records_response.status_code not in [200,201]:
            messages.error(request, f"Failed to fetch records. {records_response.json()}", extra_tags="warning")
        else:
            records = records_response.json()
            # You can pass 'records' to your template for rendering
            context = {'records': records}
            return render(request, 'tasktimesheet_list.html', context)
    except Exception as e:
        print("An error occurred: Expecting value: line 1 column 1 (char 0)")
    return render(request,'tasktimesheet_list.html')

# edit function
def tasktimesheet_edit(request,pk):
    # endpoint1='task/'    
    # records_response2 = call_get_method_without_token(BASEURL,endpoint1)
    # print('records_response.status_code',records_response2.status_code)
    # if records_response2.status_code not in [200,201]:
    #     messages.error(request, f"Failed to fetch records. {records_response2.json()}", extra_tags="warning")
    # else:
    #     task = records_response2.json()
    user_token=request.session['user_token']
    endpoint2='trioprofile/'    
    records_response2 = call_get_method(BASEURL,endpoint2,user_token)
    print('records_response.status_code',records_response2.status_code)
    if records_response2.status_code not in [200,201]:
        messages.error(request, f"Failed to fetch records. {records_response2.json()}", extra_tags="warning")
    else:
        clients = records_response2.json()
    tasktimesheet = call_get_method_without_token(BASEURL, f'tasktimesheet/{pk}/')
    
    if tasktimesheet.status_code in [200,201]:
        tasktimesheet_data = tasktimesheet.json()
    else:
        print('error------',tasktimesheet)
        messages.error(request, 'Failed to retrieve data for tasktimesheet. Please check your connection and try again.', extra_tags='warning')
        return redirect('tasktimesheet')

    if request.method=="POST":
        form=TaskTimesheetForm(request.POST, initial=tasktimesheet_data,user_choices=clients)
        if form.is_valid():
            updated_data = form.cleaned_data
            for field_name, field in form.fields.items():
                if isinstance(field.widget, forms.DateInput) or isinstance(field, forms.DateField) or isinstance(field, forms.DateTimeField):
                    if updated_data[field_name]:
                        del updated_data[field_name]
                        updated_data[field_name] = request.POST.get(field_name)
            # Serialize the updated data as JSON
            json_data = json.dumps(updated_data)
            response = call_put_method_without_token(BASEURL, f'tasktimesheet/{pk}/', json_data)

            if response.status_code in [200,201]: 
                messages.success(request, 'Your data has been successfully saved', extra_tags='success')
                return redirect('tasktimesheet') 
            else:
                error_message = response.json()
                messages.error(request, f"Oops..! {error_message}", extra_tags='warning')
        else:
            print("An error occurred: Expecting value: line 1 column 1 (char 0)")
    else:
        form = TaskTimesheetForm(initial=tasktimesheet_data,user_choices=clients,)

    context={
        'form':form,
    }
    return render(request,'tasktimesheet_edit.html',context)

def tasktimesheet_delete(request,pk):
    end_point = f'tasktimesheet/{pk}/'
    tasktimesheet = call_delete_method_without_token(BASEURL, end_point)
    if tasktimesheet.status_code not in [200,201]:
        messages.error(request, 'Failed to delete data for tasktimesheet. Please try again.', extra_tags='warning')
        return redirect('tasktimesheet')
    else:
        messages.success(request, 'Successfully deleted data for tasktimesheet', extra_tags='success')
        return redirect('tasktimesheet')


def taskhours(request, pk):
    user_token = request.session.get('user_token')
    print('-------',pk)

    endpoint = f'tasktimesheet_hours/{pk}/'
    try:
        # Get data from backend
        records_response = call_get_method(BASEURL, endpoint, user_token)
        if records_response.status_code not in [200, 201]:
            return JsonResponse({
                "error": "Failed to fetch records",
                "details": records_response.json()
            }, status=records_response.status_code)
        else:
            records = records_response.json()
            # Return only id and hours_spent
            data = {
                "id": records.get('id'),
                "hours_spent": records.get('total_working_hours')
            }
            return JsonResponse(data, status=200)
    except Exception as e:
        print(f"An error occurred: {e}")
        return JsonResponse({
            "error": "An unexpected error occurred",
            "message": str(e)
        }, status=500)

# create and view table function
def timesheetentry(request):
    user_token=request.session['user_token']
    endpoint1='task/'    
    records_response2 = call_get_method(BASEURL,endpoint1,user_token)
    print('records_response.status_code',records_response2.status_code)
    if records_response2.status_code not in [200,201]:
        messages.error(request, f"Failed to fetch records. {records_response2.json()}", extra_tags="warning")
    else:
        task = records_response2.json()
        print('task',task)

    endpoint2='tasktimesheet/'    
    records_response2 = call_get_method(BASEURL,endpoint2,user_token)
    print('records_response.status_code',records_response2.status_code)
    if records_response2.status_code not in [200,201]:
        messages.error(request, f"Failed to fetch records. {records_response2.json()}", extra_tags="warning")
    else:
        timesheet = records_response2.json()
        print('timesheet',timesheet)

        
    hours = timesheet[0]  # or any index or filter logic
    given_hours = hours.get('total_working_hours')
    print('Given Hours:', given_hours)

    initial={'given_hours':given_hours}
    form=TimesheetEntryForm(timesheet_choices=timesheet,task_choices=task,initial=initial)
    endpoint = 'timesheetentry/'
    if request.method=="POST":
        form=TimesheetEntryForm(request.POST,request.FILES,timesheet_choices=timesheet,task_choices=task,)
        if form.is_valid():
            Output = form.cleaned_data
            Output['branch']=request.session['branch']
            Output['created_by']=request.session['user_data']['id']
            print('Output',Output)
            for field_name, field in form.fields.items():
                if isinstance(field.widget, forms.DateInput) or isinstance(field, forms.DateField) or isinstance(field, forms.DateTimeField):
                    if Output[field_name]:
                        del Output[field_name]
                        Output[field_name] = request.POST.get(field_name)
            cleaned_data = form.cleaned_data
            print('cleaned_data',cleaned_data)
            files, cleaned_data = image_filescreate(cleaned_data)
            json_data = cleaned_data if files else json.dumps(cleaned_data)
            print('==json_data==,',json_data)
            response = call_post_method_with_token_v2(BASEURL,endpoint,json_data,files)

            print('==response==',response)
            if response['status_code'] == 1:
                print("error",response)
            else:
                messages.success(request,'Data Successfully Saved', extra_tags="success")
                return redirect('timesheetentry_list')
    else:
        print('errorss',form.errors)
    try:
        # getting data from backend
        records_response = call_get_method(BASEURL,endpoint,user_token)
        if records_response.status_code not in [200,201]:
            messages.error(request, f"Failed to fetch records. {records_response.json()}", extra_tags="warning")
        else:
            records = records_response.json()
            print('records',records)
            # You can pass 'records' to your template for rendering
            context = {'form': form, 'records': records}
            return render(request, 'timesheetentry.html', context)
    except Exception as e:
        print("An error occurred: Expecting value: line 1 column 1 (char 0)")
    
    context={
        'form':form,
    }
    return render(request,'timesheetentry.html',context)


def timesheetentry_view(request, pk):
    user_token = request.session.get('user_token')

    # Fetch timesheet entry details
    entry_endpoint = f'timesheetentry_view/{pk}/'
    entry_response = call_get_method(BASEURL, entry_endpoint, user_token)
    if entry_response.status_code not in [200, 201]:
        messages.error(request, f"Failed to fetch timesheet entry. {entry_response.json()}", extra_tags="warning")
        return render(request, 'timesheetentry.html', {'form': None, 'view': True})

    record_data = entry_response.json()
    print('record_data',record_data)
    # Create form instance with initial data and dynamic choices
    for record in record_data:
        if isinstance(record.get("timesheet"), dict):
            record["timesheet"] = record["timesheet"]["id"]

    print('record_data', record_data)

    context = {
        "record_data": record_data,
    }

    return render(request, 'timesheetentry_view.html', context)


def timesheetentry_view1(request, pk):
    user_token = request.session.get('user_token')
    if not user_token:
        messages.error(request, "Session expired or user token missing.", extra_tags="danger")
        return redirect('login')  # or your appropriate fallback

    # Fetch tasks
    task_response = call_get_method(BASEURL, 'task/', user_token)
    if task_response.status_code not in [200, 201]:
        messages.error(request, f"Failed to fetch tasks. {task_response.json()}", extra_tags="warning")
        task = []
    else:
        task = task_response.json()

    # Fetch timesheets
    timesheet_response = call_get_method(BASEURL, 'tasktimesheet/', user_token)
    if timesheet_response.status_code not in [200, 201]:
        messages.error(request, f"Failed to fetch timesheets. {timesheet_response.json()}", extra_tags="warning")
        timesheet = []
    else:
        timesheet = timesheet_response.json()
        print('timesheet',timesheet)
    # Handle total working hours extraction safely
    given_hours = None
    if timesheet:
        given_hours = timesheet[0].get('total_working_hours', None)
        print('Given Hours:', given_hours)

    # Fetch timesheet entry details
    entry_endpoint = f'timesheetentry_view1/{pk}/'
    entry_response = call_get_method(BASEURL, entry_endpoint, user_token)
    if entry_response.status_code not in [200, 201]:
        messages.error(request, f"Failed to fetch timesheet entry. {entry_response.json()}", extra_tags="warning")
        return render(request, 'timesheetentry.html', {'form': None, 'view': True})

    record_data = entry_response.json()
    print('record_data',record_data)
    if isinstance(record_data.get("timesheet"), dict):
        record_data["timesheet"] = record_data["timesheet"]["id"]

    # Create form instance with initial data and dynamic choices
    form = TimesheetEntryForm(
        initial=record_data,
        timesheet_choices=timesheet if timesheet else [],
        task_choices=task if task else []
    )

    context = {
        "form": form,
        "view": True,
        "given_hours": given_hours,  # Optionally pass it to template
    }

    return render(request, 'timesheetentry.html', context)

def timesheetentry_list(request):
    user_token=request.session['user_token']

    endpoint = 'timesheetentry/'
    try:
        # getting data from backend
        records_response = call_get_method(BASEURL,endpoint,user_token)
        if records_response.status_code not in [200,201]:
            messages.error(request, f"Failed to fetch records. {records_response.json()}", extra_tags="warning")
        else:
            records = records_response.json()
            # You can pass 'records' to your template for rendering
            context = {'records': records}
            return render(request, 'timesheetentry_list.html', context)
    except Exception as e:
        print("An error occurred: Expecting value: line 1 column 1 (char 0)")
    return render(request,'timesheetentry_list.html')

# def get_task(request, task_id):
#     user_token = request.session['user_token']
#     endpoint = f'get_task/{task_id}/'
#     try:
#         # Call the backend API to fetch task data
#         records_response = call_get_method(BASEURL, endpoint, user_token)
#         if records_response.status_code in [200, 201]:
#             records = records_response.json()
#             return JsonResponse({'records': records})
#         else:
#             return JsonResponse({'error': 'Failed to fetch task data'}, status=400)
#     except Exception as e:
#         return JsonResponse({'error': 'An error occurred'}, status=500)

def get_task(request, task_id):
    user_token = request.session['user_token']
    endpoint = f'get_task/{task_id}/'
    try:
        records_response = call_get_method(BASEURL, endpoint, user_token)
        if records_response.status_code in [200, 201]:
            all_tasks = records_response.json()  # still returning a list
            print('--task', all_tasks)

            # Filter the task with the given ID
            task = next((t for t in all_tasks if t['id'] == int(task_id)), None)

            if task:
                return JsonResponse({
                    'task': task['task'],
                    'total_working_hours': task['total_working_hours']
                })
            else:
                return JsonResponse({'error': 'Task not found'}, status=404)
        else:
            return JsonResponse({'error': 'Failed to fetch task data'}, status=400)
    except Exception as e:
        print('Error:', e)
        return JsonResponse({'error': 'An error occurred'}, status=500)


def tasktimesheet_approval_list(request):
    user_token=request.session['user_token']

    endpoint = 'tasktimesheet_approval/'
    try:
        # getting data from backend
        records_response = call_get_method(BASEURL,endpoint,user_token)
        if records_response.status_code not in [200,201]:
            messages.error(request, f"Failed to fetch records. {records_response.json()}", extra_tags="warning")
        else:
            records = records_response.json()
            print('Timesheetrecords',records)
            # You can pass 'records' to your template for rendering
            context = {'records': records, 'screen_name' :'Task Timesheet'}
            return render(request, 'tasktimesheet_approval_list.html', context)
    except Exception as e:
        print("An error occurred: Expecting value: line 1 column 1 (char 0)")
    return render(request,'tasktimesheet_approval_list.html')


def timesheetentry_approval_list(request):
    user_token=request.session['user_token']

    endpoint = 'timesheetentry_approval/'
    try:
        # getting data from backend
        records_response = call_get_method(BASEURL,endpoint,user_token)
        if records_response.status_code not in [200,201]:
            messages.error(request, f"Failed to fetch records. {records_response.json()}", extra_tags="warning")
        else:
            records = records_response.json()
            print('entryrecords',records)
            # You can pass 'records' to your template for rendering
            context = {'records': records ,'screen_name' :'Timesheet Entry'}
            return render(request, 'timesheetentry_approval_list.html', context)
    except Exception as e:
        print("An error occurred: Expecting value: line 1 column 1 (char 0)")
    return render(request,'timesheetentry_approval_list.html')

# edit function
def timesheetentry_edit(request,pk):
    user_token=request.session['user_token']
    endpoint1='task/'    
    records_response2 = call_get_method(BASEURL,endpoint1,user_token)
    print('records_response.status_code',records_response2.status_code)
    if records_response2.status_code not in [200,201]:
        messages.error(request, f"Failed to fetch records. {records_response2.json()}", extra_tags="warning")
    else:
        task = records_response2.json()
    endpoint2='tasktimesheet/'    
    records_response2 = call_get_method(BASEURL,endpoint2,user_token)
    print('records_response.status_code',records_response2.status_code)
    if records_response2.status_code not in [200,201]:
        messages.error(request, f"Failed to fetch records. {records_response2.json()}", extra_tags="warning")
    else:
        timesheet = records_response2.json()
    hours = timesheet[0]  # or any index or filter logic
    given_hours = hours.get('total_working_hours')
    print('Given Hours:', given_hours)

    initial={'given_hours':given_hours}
    timesheetentry = call_get_method(BASEURL, f'timesheetentry/{pk}/',user_token)
    
    if timesheetentry.status_code in [200,201]:
        timesheetentry_data = timesheetentry.json()
    else:
        print('error------',timesheetentry)
        messages.error(request, 'Failed to retrieve data for timesheetentry. Please check your connection and try again.', extra_tags='warning')
        return redirect('timesheetentry_list')

    if request.method=="POST":
        form=TimesheetEntryForm(request.POST,request.FILES, initial=timesheetentry_data,timesheet_choices=timesheet,task_choices=task)
        if form.is_valid():
            updated_data = form.cleaned_data
            for field_name, field in form.fields.items():
                if isinstance(field.widget, forms.DateInput) or isinstance(field, forms.DateField) or isinstance(field, forms.DateTimeField):
                    if updated_data[field_name]:
                        del updated_data[field_name]
                        updated_data[field_name] = request.POST.get(field_name)
            # Serialize the updated data as JSON
            json_data = json.dumps(updated_data)
            response = call_put_method_without_token(BASEURL, f'timesheetentry/{pk}/', json_data)

            if response.status_code in [200,201]: 
                messages.success(request, 'Your data has been successfully saved', extra_tags='success')
                return redirect('timesheetentry_list') 
            else:
                error_message = response.json()
                messages.error(request, f"Oops..! {error_message}", extra_tags='warning')
        else:
            print("An error occurred: Expecting value: line 1 column 1 (char 0)")
    else:
        form = TimesheetEntryForm(initial=timesheetentry_data,timesheet_choices=timesheet,task_choices=task)

    context={
        'form':form,
    }
    return render(request,'timesheetentry_edit.html',context)

def timesheetentry_delete(request,pk):
    end_point = f'timesheetentry/{pk}/'
    timesheetentry = call_delete_method_without_token(BASEURL, end_point)
    if timesheetentry.status_code not in [200,201]:
        messages.error(request, 'Failed to delete data for timesheetentry. Please try again.', extra_tags='warning')
        return redirect('timesheetentry_list')
    else:
        messages.success(request, 'Successfully deleted data for timesheetentry', extra_tags='success')
        return redirect('timesheetentry_list')

# create and view table function
def timesheetattachment(request):
    endpoint1='timesheetentry/'    
    records_response2 = call_get_method_without_token(BASEURL,endpoint1)
    print('records_response.status_code',records_response2.status_code)
    if records_response2.status_code not in [200,201]:
        messages.error(request, f"Failed to fetch records. {records_response2.json()}", extra_tags="warning")
    else:
        task = records_response2.json()
    form=TimesheetAttachmentForm(task_choices=task)
    endpoint = 'timesheetattachment/'
    if request.method=="POST":
        form=TimesheetAttachmentForm(request.POST,task_choices=task)
        if form.is_valid():
            Output = form.cleaned_data
            Output['branch']=request.session['branch']
            Output['created_by']=request.session['user_data']['id']

            for field_name, field in form.fields.items():
                if isinstance(field.widget, forms.DateInput) or isinstance(field, forms.DateField) or isinstance(field, forms.DateTimeField):
                    if Output[field_name]:
                        del Output[field_name]
                        Output[field_name] = request.POST.get(field_name)
            json_data=json.dumps(Output)
            response = call_post_method_for_without_token(BASEURL,endpoint,json_data)
            if response.status_code not in [200,201]:
                print("error",response)
            else:
                messages.success(request,'Data Successfully Saved', extra_tags="success")
                return redirect('timesheetattachment_list')
    else:
        print('errorss',form.errors)
    try:
        # getting data from backend
        records_response = call_get_method_without_token(BASEURL,endpoint)
        if records_response.status_code not in [200,201]:
            messages.error(request, f"Failed to fetch records. {records_response.json()}", extra_tags="warning")
        else:
            records = records_response.json()
            # You can pass 'records' to your template for rendering
            context = {'form': form, 'records': records}
            return render(request, 'timesheetattachment.html', context)
    except Exception as e:
        print("An error occurred: Expecting value: line 1 column 1 (char 0)")
    context={
        'form':form,
    }
    return render(request,'timesheetattachment.html',context)

def timesheetattachment_list(request):
    endpoint = 'timesheetattachment/'
    try:
        # getting data from backend
        records_response = call_get_method_without_token(BASEURL,endpoint)
        if records_response.status_code not in [200,201]:
            messages.error(request, f"Failed to fetch records. {records_response.json()}", extra_tags="warning")
        else:
            records = records_response.json()
            # You can pass 'records' to your template for rendering
            context = {'records': records}
            return render(request, 'timesheetattachment_list.html', context)
    except Exception as e:
        print("An error occurred: Expecting value: line 1 column 1 (char 0)")
    return render(request,'timesheetattachment_list.html')

# edit function
def timesheetattachment_edit(request,pk):
    endpoint1='timesheetentry/'    
    records_response2 = call_get_method_without_token(BASEURL,endpoint1)
    print('records_response.status_code',records_response2.status_code)
    if records_response2.status_code not in [200,201]:
        messages.error(request, f"Failed to fetch records. {records_response2.json()}", extra_tags="warning")
    else:
        task = records_response2.json()
    timesheetattachment = call_get_method_without_token(BASEURL, f'timesheetattachment/{pk}/')
    
    if timesheetattachment.status_code in [200,201]:
        timesheetattachment_data = timesheetattachment.json()
    else:
        print('error------',timesheetattachment)
        messages.error(request, 'Failed to retrieve data for timesheetattachment. Please check your connection and try again.', extra_tags='warning')
        return redirect('timesheetattachment')

    if request.method=="POST":
        form=TimesheetAttachmentForm(request.POST, initial=timesheetattachment_data,task_choices=task)
        if form.is_valid():
            updated_data = form.cleaned_data
            for field_name, field in form.fields.items():
                if isinstance(field.widget, forms.DateInput) or isinstance(field, forms.DateField) or isinstance(field, forms.DateTimeField):
                    if updated_data[field_name]:
                        del updated_data[field_name]
                        updated_data[field_name] = request.POST.get(field_name)
            # Serialize the updated data as JSON
            json_data = json.dumps(updated_data)
            response = call_put_method_without_token(BASEURL, f'timesheetattachment/{pk}/', json_data)

            if response.status_code in [200,201]: 
                messages.success(request, 'Your data has been successfully saved', extra_tags='success')
                return redirect('timesheetattachment') 
            else:
                error_message = response.json()
                messages.error(request, f"Oops..! {error_message}", extra_tags='warning')
        else:
            print("An error occurred: Expecting value: line 1 column 1 (char 0)")
    else:
        form = TimesheetAttachmentForm(initial=timesheetattachment_data,task_choices=task)

    context={
        'form':form,
    }
    return render(request,'timesheetattachment_edit.html',context)

def timesheetattachment_delete(request,pk):
    end_point = f'timesheetattachment/{pk}/'
    timesheetattachment = call_delete_method_without_token(BASEURL, end_point)
    if timesheetattachment.status_code not in [200,201]:
        messages.error(request, 'Failed to delete data for timesheetattachment. Please try again.', extra_tags='warning')
        return redirect('timesheetattachment')
    else:
        messages.success(request, 'Successfully deleted data for timesheetattachment', extra_tags='success')
        return redirect('timesheetattachment')

# create and view table function
def timesheetdocument(request):
    endpoint1='timesheetentry/'    
    records_response2 = call_get_method_without_token(BASEURL,endpoint1)
    print('records_response.status_code',records_response2.status_code)
    if records_response2.status_code not in [200,201]:
        messages.error(request, f"Failed to fetch records. {records_response2.json()}", extra_tags="warning")
    else:
        task = records_response2.json()
    form=TimesheetDocumentForm(task_choices=task)
    endpoint = 'timesheetdocument/'
    if request.method=="POST":
        form=TimesheetDocumentForm(request.POST,task_choices=task)
        if form.is_valid():
            Output = form.cleaned_data
            Output['branch']=request.session['branch']
            Output['created_by']=request.session['user_data']['id']

            for field_name, field in form.fields.items():
                if isinstance(field.widget, forms.DateInput) or isinstance(field, forms.DateField) or isinstance(field, forms.DateTimeField):
                    if Output[field_name]:
                        del Output[field_name]
                        Output[field_name] = request.POST.get(field_name)
            json_data=json.dumps(Output)
            response = call_post_method_for_without_token(BASEURL,endpoint,json_data)
            if response.status_code not in [200,201]:
                print("error",response)
            else:
                messages.success(request,'Data Successfully Saved', extra_tags="success")
                return redirect('timesheetdocument_list')
    else:
        print('errorss',form.errors)
    try:
        # getting data from backend
        records_response = call_get_method_without_token(BASEURL,endpoint)
        if records_response.status_code not in [200,201]:
            messages.error(request, f"Failed to fetch records. {records_response.json()}", extra_tags="warning")
        else:
            records = records_response.json()
            # You can pass 'records' to your template for rendering
            context = {'form': form, 'records': records}
            return render(request, 'timesheetdocument.html', context)
    except Exception as e:
        print("An error occurred: Expecting value: line 1 column 1 (char 0)")
    context={
        'form':form,
    }
    return render(request,'timesheetdocument.html',context)

def timesheetdocument_list(request):
    endpoint = 'timesheetdocument/'
    try:
        # getting data from backend
        records_response = call_get_method_without_token(BASEURL,endpoint)
        if records_response.status_code not in [200,201]:
            messages.error(request, f"Failed to fetch records. {records_response.json()}", extra_tags="warning")
        else:
            records = records_response.json()
            # You can pass 'records' to your template for rendering
            context = {'records': records}
            return render(request, 'timesheetdocument_list.html', context)
    except Exception as e:
        print("An error occurred: Expecting value: line 1 column 1 (char 0)")
    return render(request,'timesheetdocument_list.html')


# edit function
def timesheetdocument_edit(request,pk):
    endpoint1='timesheetentry/'    
    records_response2 = call_get_method_without_token(BASEURL,endpoint1)
    print('records_response.status_code',records_response2.status_code)
    if records_response2.status_code not in [200,201]:
        messages.error(request, f"Failed to fetch records. {records_response2.json()}", extra_tags="warning")
    else:
        task = records_response2.json()
    timesheetdocument = call_get_method_without_token(BASEURL, f'timesheetdocument/{pk}/')
    
    if timesheetdocument.status_code in [200,201]:
        timesheetdocument_data = timesheetdocument.json()
    else:
        print('error------',timesheetdocument)
        messages.error(request, 'Failed to retrieve data for timesheetdocument. Please check your connection and try again.', extra_tags='warning')
        return redirect('timesheetdocument')

    if request.method=="POST":
        form=TimesheetDocumentForm(request.POST, initial=timesheetdocument_data,task_choices=task)
        if form.is_valid():
            updated_data = form.cleaned_data
            for field_name, field in form.fields.items():
                if isinstance(field.widget, forms.DateInput) or isinstance(field, forms.DateField) or isinstance(field, forms.DateTimeField):
                    if updated_data[field_name]:
                        del updated_data[field_name]
                        updated_data[field_name] = request.POST.get(field_name)
            # Serialize the updated data as JSON
            json_data = json.dumps(updated_data)
            response = call_put_method_without_token(BASEURL, f'timesheetdocument/{pk}/', json_data)

            if response.status_code in [200,201]: 
                messages.success(request, 'Your data has been successfully saved', extra_tags='success')
                return redirect('timesheetdocument') 
            else:
                error_message = response.json()
                messages.error(request, f"Oops..! {error_message}", extra_tags='warning')
        else:
            print("An error occurred: Expecting value: line 1 column 1 (char 0)")
    else:
        form = TimesheetDocumentForm(initial=timesheetdocument_data,task_choices=task)

    context={
        'form':form,
    }
    return render(request,'timesheetdocument_edit.html',context)

def timesheetdocument_delete(request,pk):
    end_point = f'timesheetdocument/{pk}/'
    timesheetdocument = call_delete_method_without_token(BASEURL, end_point)
    if timesheetdocument.status_code not in [200,201]:
        messages.error(request, 'Failed to delete data for timesheetdocument. Please try again.', extra_tags='warning')
        return redirect('timesheetdocument')
    else:
        messages.success(request, 'Successfully deleted data for timesheetdocument', extra_tags='success')
        return redirect('timesheetdocument')

# create and view table function
def workschedule(request):
    form=WorkScheduleForm()
    endpoint = 'workschedule/'
    if request.method=="POST":
        form=WorkScheduleForm(request.POST)
        if form.is_valid():
            Output = form.cleaned_data
            Output['branch']=request.session['branch']
            Output['created_by']=request.session['user_data']['id']

            for field_name, field in form.fields.items():
                if isinstance(field.widget, forms.DateInput) or isinstance(field, forms.DateField) or isinstance(field, forms.DateTimeField):
                    if Output[field_name]:
                        del Output[field_name]
                        Output[field_name] = request.POST.get(field_name)
            json_data=json.dumps(Output)
            response = call_post_method_for_without_token(BASEURL,endpoint,json_data)
            if response.status_code not in [200,201]:
                print("error",response)
            else:
                messages.success(request,'Data Successfully Saved', extra_tags="success")
                return redirect('workschedule_list')
    else:
        print('errorss',form.errors)
    try:
        # getting data from backend
        records_response = call_get_method_without_token(BASEURL,endpoint)
        if records_response.status_code not in [200,201]:
            messages.error(request, f"Failed to fetch records. {records_response.json()}", extra_tags="warning")
        else:
            records = records_response.json()
            # You can pass 'records' to your template for rendering
            context = {'form': form, 'records': records}
            return render(request, 'workschedule.html', context)
    except Exception as e:
        print("An error occurred: Expecting value: line 1 column 1 (char 0)")
    context={
        'form':form,
    }
    return render(request,'workschedule.html',context)

def workschedule_list(request):
    endpoint = 'workschedule/'
    try:
        # getting data from backend
        records_response = call_get_method_without_token(BASEURL,endpoint)
        if records_response.status_code not in [200,201]:
            messages.error(request, f"Failed to fetch records. {records_response.json()}", extra_tags="warning")
        else:
            records = records_response.json()
            # You can pass 'records' to your template for rendering
            context = {'records': records}
            return render(request, 'workschedule_list.html', context)
    except Exception as e:
        print("An error occurred: Expecting value: line 1 column 1 (char 0)")
    return render(request,'workschedule_list.html')


# edit function
def workschedule_edit(request,pk):
    workschedule = call_get_method_without_token(BASEURL, f'workschedule/{pk}/')
    
    if workschedule.status_code in [200,201]:
        workschedule_data = workschedule.json()
    else:
        print('error------',workschedule)
        messages.error(request, 'Failed to retrieve data for workschedule. Please check your connection and try again.', extra_tags='warning')
        return redirect('workschedule')

    if request.method=="POST":
        form=WorkScheduleForm(request.POST, initial=workschedule_data)
        if form.is_valid():
            updated_data = form.cleaned_data
            for field_name, field in form.fields.items():
                if isinstance(field.widget, forms.DateInput) or isinstance(field, forms.DateField) or isinstance(field, forms.DateTimeField):
                    if updated_data[field_name]:
                        del updated_data[field_name]
                        updated_data[field_name] = request.POST.get(field_name)
            # Serialize the updated data as JSON
            json_data = json.dumps(updated_data)
            response = call_put_method_without_token(BASEURL, f'workschedule/{pk}/', json_data)

            if response.status_code in [200,201]: 
                messages.success(request, 'Your data has been successfully saved', extra_tags='success')
                return redirect('workschedule') 
            else:
                error_message = response.json()
                messages.error(request, f"Oops..! {error_message}", extra_tags='warning')
        else:
            print("An error occurred: Expecting value: line 1 column 1 (char 0)")
    else:
        form = WorkScheduleForm(initial=workschedule_data)

    context={
        'form':form,
    }
    return render(request,'workschedule_edit.html',context)

def workschedule_delete(request,pk):
    end_point = f'workschedule/{pk}/'
    workschedule = call_delete_method_without_token(BASEURL, end_point)
    if workschedule.status_code not in [200,201]:
        messages.error(request, 'Failed to delete data for workschedule. Please try again.', extra_tags='warning')
        return redirect('workschedule')
    else:
        messages.success(request, 'Successfully deleted data for workschedule', extra_tags='success')
        return redirect('workschedule')

# create and view table function
def taskextrahoursrequest(request):
    endpoint1='task/'    
    records_response2 = call_get_method_without_token(BASEURL,endpoint1)
    print('records_response.status_code',records_response2.status_code)
    if records_response2.status_code not in [200,201]:
        messages.error(request, f"Failed to fetch records. {records_response2.json()}", extra_tags="warning")
    else:
        task = records_response2.json()
    endpoint1='UserManagement/user/'    
    records_response2 = call_get_method_without_token(BASEURL,endpoint1)
    print('records_response.status_code',records_response2.status_code)
    if records_response2.status_code not in [200,201]:
        messages.error(request, f"Failed to fetch records. {records_response2.json()}", extra_tags="warning")
    else:
        employee = records_response2.json()
    form=TaskExtraHoursRequestForm(user_choices=employee,task_choices=task)
    endpoint = 'taskextrahoursrequest/'
    if request.method=="POST":
        form=TaskExtraHoursRequestForm(request.POST,user_choices=employee,task_choices=task)
        if form.is_valid():
            Output = form.cleaned_data
            Output['branch']=request.session['branch']
            Output['created_by']=request.session['user_data']['id']

            for field_name, field in form.fields.items():
                if isinstance(field.widget, forms.DateInput) or isinstance(field, forms.DateField) or isinstance(field, forms.DateTimeField):
                    if Output[field_name]:
                        del Output[field_name]
                        Output[field_name] = request.POST.get(field_name)
            json_data=json.dumps(Output)
            response = call_post_method_for_without_token(BASEURL,endpoint,json_data)
            if response.status_code not in [200,201]:
                print("error",response)
            else:
                messages.success(request,'Data Successfully Saved', extra_tags="success")
                return redirect('taskextrahoursrequest')
    else:
        print('errorss',form.errors)
    try:
        # getting data from backend
        records_response = call_get_method_without_token(BASEURL,endpoint)
        if records_response.status_code not in [200,201]:
            messages.error(request, f"Failed to fetch records. {records_response.json()}", extra_tags="warning")
        else:
            records = records_response.json()
            # You can pass 'records' to your template for rendering
            context = {'form': form, 'records': records}
            return render(request, 'taskextrahoursrequest.html', context)
    except Exception as e:
        print("An error occurred: Expecting value: line 1 column 1 (char 0)")
    context={
        'form':form,
    }
    return render(request,'taskextrahoursrequest.html',context)


# edit function
def taskextrahoursrequest_edit(request,pk):
    endpoint1='task/'    
    records_response2 = call_get_method_without_token(BASEURL,endpoint1)
    print('records_response.status_code',records_response2.status_code)
    if records_response2.status_code not in [200,201]:
        messages.error(request, f"Failed to fetch records. {records_response2.json()}", extra_tags="warning")
    else:
        task = records_response2.json()
    endpoint1='UserManagement/user/'    
    records_response2 = call_get_method_without_token(BASEURL,endpoint1)
    print('records_response.status_code',records_response2.status_code)
    if records_response2.status_code not in [200,201]:
        messages.error(request, f"Failed to fetch records. {records_response2.json()}", extra_tags="warning")
    else:
        employee = records_response2.json()
    taskextrahoursrequest = call_get_method_without_token(BASEURL, f'taskextrahoursrequest/{pk}/')
    
    if taskextrahoursrequest.status_code in [200,201]:
        taskextrahoursrequest_data = taskextrahoursrequest.json()
    else:
        print('error------',taskextrahoursrequest)
        messages.error(request, 'Failed to retrieve data for taskextrahoursrequest. Please check your connection and try again.', extra_tags='warning')
        return redirect('taskextrahoursrequest')

    if request.method=="POST":
        form=TaskExtraHoursRequestForm(request.POST, initial=taskextrahoursrequest_data,user_choices=employee,task_choices=task)
        if form.is_valid():
            updated_data = form.cleaned_data
            for field_name, field in form.fields.items():
                if isinstance(field.widget, forms.DateInput) or isinstance(field, forms.DateField) or isinstance(field, forms.DateTimeField):
                    if updated_data[field_name]:
                        del updated_data[field_name]
                        updated_data[field_name] = request.POST.get(field_name)
            # Serialize the updated data as JSON
            json_data = json.dumps(updated_data)
            response = call_put_method_without_token(BASEURL, f'taskextrahoursrequest/{pk}/', json_data)

            if response.status_code in [200,201]: 
                messages.success(request, 'Your data has been successfully saved', extra_tags='success')
                return redirect('taskextrahoursrequest') 
            else:
                error_message = response.json()
                messages.error(request, f"Oops..! {error_message}", extra_tags='warning')
        else:
            print("An error occurred: Expecting value: line 1 column 1 (char 0)")
    else:
        form = TaskExtraHoursRequestForm(initial=taskextrahoursrequest_data,user_choices=employee,task_choices=task)

    context={
        'form':form,
    }
    return render(request,'taskextrahoursrequest_edit.html',context)

def taskextrahoursrequest_delete(request,pk):
    end_point = f'taskextrahoursrequest/{pk}/'
    taskextrahoursrequest = call_delete_method_without_token(BASEURL, end_point)
    if taskextrahoursrequest.status_code not in [200,201]:
        messages.error(request, 'Failed to delete data for taskextrahoursrequest. Please try again.', extra_tags='warning')
        return redirect('taskextrahoursrequest')
    else:
        messages.success(request, 'Successfully deleted data for taskextrahoursrequest', extra_tags='success')
        return redirect('taskextrahoursrequest')

# create and view table function
def meetings(request):
    endpoint1='UserManagement/user/'    
    records_response2 = call_get_method_without_token(BASEURL,endpoint1)
    print('records_response.status_code',records_response2.status_code)
    if records_response2.status_code not in [200,201]:
        messages.error(request, f"Failed to fetch records. {records_response2.json()}", extra_tags="warning")
    else:
        employee = records_response2.json()
    form=MeetingsForm(attendees_choices=employee,user_choices=employee)
    endpoint = 'meetings/'
    if request.method=="POST":
        form=MeetingsForm(request.POST,attendees_choices=employee,user_choices=employee)
        if form.is_valid():
            Output = form.cleaned_data
            Output['branch']=request.session['branch']
            Output['created_by']=request.session['user_data']['id']

            for field_name, field in form.fields.items():
                if isinstance(field.widget, forms.DateInput) or isinstance(field, forms.DateField) or isinstance(field, forms.DateTimeField):
                    if Output[field_name]:
                        del Output[field_name]
                        Output[field_name] = request.POST.get(field_name)
            json_data=json.dumps(Output)
            response = call_post_method_for_without_token(BASEURL,endpoint,json_data)
            if response.status_code not in [200,201]:
                print("error",response)
            else:
                messages.success(request,'Data Successfully Saved', extra_tags="success")
                return redirect('meetings')
    else:
        print('errorss',form.errors)
    try:
        # getting data from backend
        records_response = call_get_method_without_token(BASEURL,endpoint)
        if records_response.status_code not in [200,201]:
            messages.error(request, f"Failed to fetch records. {records_response.json()}", extra_tags="warning")
        else:
            records = records_response.json()
            # You can pass 'records' to your template for rendering
            context = {'form': form, 'records': records}
            return render(request, 'meetings.html', context)
    except Exception as e:
        print("An error occurred: Expecting value: line 1 column 1 (char 0)")
    context={
        'form':form,
    }
    return render(request,'meetings.html',context)


# edit function
def meetings_edit(request,pk):
    endpoint1='UserManagement/user/'    
    records_response2 = call_get_method_without_token(BASEURL,endpoint1)
    print('records_response.status_code',records_response2.status_code)
    if records_response2.status_code not in [200,201]:
        messages.error(request, f"Failed to fetch records. {records_response2.json()}", extra_tags="warning")
    else:
        employee = records_response2.json()
    meetings = call_get_method_without_token(BASEURL, f'meetings/{pk}/')
    
    if meetings.status_code in [200,201]:
        meetings_data = meetings.json()
    else:
        print('error------',meetings)
        messages.error(request, 'Failed to retrieve data for meetings. Please check your connection and try again.', extra_tags='warning')
        return redirect('meetings')

    if request.method=="POST":
        form=MeetingsForm(request.POST, initial=meetings_data,attendees_choices=employee,user_choices=employee)
        if form.is_valid():
            updated_data = form.cleaned_data
            for field_name, field in form.fields.items():
                if isinstance(field.widget, forms.DateInput) or isinstance(field, forms.DateField) or isinstance(field, forms.DateTimeField):
                    if updated_data[field_name]:
                        del updated_data[field_name]
                        updated_data[field_name] = request.POST.get(field_name)
            # Serialize the updated data as JSON
            json_data = json.dumps(updated_data)
            response = call_put_method_without_token(BASEURL, f'meetings/{pk}/', json_data)

            if response.status_code in [200,201]: 
                messages.success(request, 'Your data has been successfully saved', extra_tags='success')
                return redirect('meetings') 
            else:
                error_message = response.json()
                messages.error(request, f"Oops..! {error_message}", extra_tags='warning')
        else:
            print("An error occurred: Expecting value: line 1 column 1 (char 0)")
    else:
        form = MeetingsForm(initial=meetings_data,attendees_choices=employee,user_choices=employee)

    context={
        'form':form,
    }
    return render(request,'meetings_edit.html',context)

def meetings_delete(request,pk):
    end_point = f'meetings/{pk}/'
    meetings = call_delete_method_without_token(BASEURL, end_point)
    if meetings.status_code not in [200,201]:
        messages.error(request, 'Failed to delete data for meetings. Please try again.', extra_tags='warning')
        return redirect('meetings')
    else:
        messages.success(request, 'Successfully deleted data for meetings', extra_tags='success')
        return redirect('meetings')

# create and view table function
def auditorprofile(request):
    user_token=request.session['user_token']
    endpoint2='audit_user/'    
    records_response2 = call_get_method(BASEURL,endpoint2,user_token)
    print('records_response.status_code',records_response2.status_code)
    if records_response2.status_code not in [200,201]:
        messages.error(request, f"Failed to fetch records. {records_response2.json()}", extra_tags="warning")
    else:
        employee = records_response2.json()
        print('---',employee)
    form=AuditorProfileForm(user_choices=employee)
    endpoint = 'auditorprofile/'
    if request.method=="POST":
        form=AuditorProfileForm(request.POST,user_choices=employee)
        if form.is_valid():
            Output = form.cleaned_data
            Output['branch']=request.session['branch']

            for field_name, field in form.fields.items():
                if isinstance(field.widget, forms.DateInput) or isinstance(field, forms.DateField) or isinstance(field, forms.DateTimeField):
                    if Output[field_name]:
                        del Output[field_name]
                        Output[field_name] = request.POST.get(field_name)
            json_data=json.dumps(Output)
            response = call_post_method_for_without_token(BASEURL,endpoint,json_data)
            if response.status_code not in [200,201]:
                print("error",response)
            else:
                messages.success(request,'Data Successfully Saved', extra_tags="success")
                return redirect('auditorprofile_list')
    else:
        print('errorss',form.errors)
    try:
        # getting data from backend
        records_response = call_get_method(BASEURL,endpoint,user_token)
        if records_response.status_code not in [200,201]:
            messages.error(request, f"Failed to fetch records. {records_response.json()}", extra_tags="warning")
        else:
            records = records_response.json()
            # You can pass 'records' to your template for rendering
            context = {'form': form, 'records': records}
            return render(request, 'auditorprofile.html', context)
    except Exception as e:
        print("An error occurred: Expecting value: line 1 column 1 (char 0)")
    context={
        'form':form,
    }
    return render(request,'auditorprofile.html',context)

def auditorprofile_list(request):
    user_token=request.session['user_token']
    endpoint = 'auditorprofile/'
    try:
        # getting data from backend
        records_response = call_get_method(BASEURL,endpoint,user_token)
        if records_response.status_code not in [200,201]:
            messages.error(request, f"Failed to fetch records. {records_response.json()}", extra_tags="warning")
        else:
            records = records_response.json()
            # You can pass 'records' to your template for rendering
            context = {'records': records}
            return render(request, 'auditorprofile_list.html', context)
    except Exception as e:
        print("An error occurred: Expecting value: line 1 column 1 (char 0)")
    return render(request,'auditorprofile_list.html')

# edit function
def auditorprofile_edit(request,pk):
    user_token=request.session['user_token']
    endpoint1='UserManagement/user/'    
    records_response2 = call_get_method(BASEURL,endpoint1,user_token)
    print('records_response.status_code',records_response2.status_code)
    if records_response2.status_code not in [200,201]:
        messages.error(request, f"Failed to fetch records. {records_response2.json()}", extra_tags="warning")
    else:
        employee = records_response2.json()
    auditorprofile = call_get_method_without_token(BASEURL, f'auditorprofile/{pk}/')
    
    if auditorprofile.status_code in [200,201]:
        auditorprofile_data = auditorprofile.json()
    else:
        print('error------',auditorprofile)
        messages.error(request, 'Failed to retrieve data for auditorprofile. Please check your connection and try again.', extra_tags='warning')
        return redirect('auditorprofile')

    if request.method=="POST":
        form=AuditorProfileForm(request.POST, initial=auditorprofile_data,user_choices=employee)
        if form.is_valid():
            updated_data = form.cleaned_data
            for field_name, field in form.fields.items():
                if isinstance(field.widget, forms.DateInput) or isinstance(field, forms.DateField) or isinstance(field, forms.DateTimeField):
                    if updated_data[field_name]:
                        del updated_data[field_name]
                        updated_data[field_name] = request.POST.get(field_name)
            # Serialize the updated data as JSON
            json_data = json.dumps(updated_data)
            response = call_put_method_without_token(BASEURL, f'auditorprofile/{pk}/', json_data)

            if response.status_code in [200,201]: 
                messages.success(request, 'Your data has been successfully saved', extra_tags='success')
                return redirect('auditorprofile') 
            else:
                error_message = response.json()
                messages.error(request, f"Oops..! {error_message}", extra_tags='warning')
        else:
            print("An error occurred: Expecting value: line 1 column 1 (char 0)")
    else:
        form = AuditorProfileForm(initial=auditorprofile_data,user_choices=employee)

    context={
        'form':form,
    }
    return render(request,'auditorprofile_edit.html',context)

def auditorprofile_delete(request,pk):
    end_point = f'auditorprofile/{pk}/'
    auditorprofile = call_delete_method_without_token(BASEURL, end_point)
    if auditorprofile.status_code not in [200,201]:
        messages.error(request, 'Failed to delete data for auditorprofile. Please try again.', extra_tags='warning')
        return redirect('auditorprofile')
    else:
        messages.success(request, 'Successfully deleted data for auditorprofile', extra_tags='success')
        return redirect('auditorprofile')

# create and view table function
def marketingagentprofile(request):
    user_token=request.session['user_token']
    endpoint2='agent_user/'    
    records_response2 = call_get_method(BASEURL,endpoint2,user_token)
    print('records_response.status_code',records_response2.status_code)
    if records_response2.status_code not in [200,201]:
        messages.error(request, f"Failed to fetch records. {records_response2.json()}", extra_tags="warning")
    else:
        employee = records_response2.json()
    form=MarketingAgentProfileForm(user_choices=employee)
    endpoint = 'marketingagentprofile/'
    if request.method=="POST":
        form=MarketingAgentProfileForm(request.POST,user_choices=employee)
        if form.is_valid():
            Output = form.cleaned_data
            Output['branch']=request.session['branch']
            Output['created_by']=request.session['user_data']['id']

            for field_name, field in form.fields.items():
                if isinstance(field.widget, forms.DateInput) or isinstance(field, forms.DateField) or isinstance(field, forms.DateTimeField):
                    if Output[field_name]:
                        del Output[field_name]
                        Output[field_name] = request.POST.get(field_name)
            json_data=json.dumps(Output)
            response = call_post_method_for_without_token(BASEURL,endpoint,json_data)
            if response.status_code not in [200,201]:
                print("error",response)
            else:
                messages.success(request,'Data Successfully Saved', extra_tags="success")
                return redirect('marketingagentprofile_list')
    else:
        print('errorss',form.errors)
    try:
        # getting data from backend
        records_response = call_get_method_without_token(BASEURL,endpoint)
        if records_response.status_code not in [200,201]:
            messages.error(request, f"Failed to fetch records. {records_response.json()}", extra_tags="warning")
        else:
            records = records_response.json()
            # You can pass 'records' to your template for rendering
            context = {'form': form, 'records': records}
            return render(request, 'marketingagentprofile.html', context)
    except Exception as e:
        print("An error occurred: Expecting value: line 1 column 1 (char 0)")
    context={
        'form':form,
    }
    return render(request,'marketingagentprofile.html',context)

def marketingagentprofile_list(request):
    user_token=request.session['user_token']

    endpoint = 'marketingagentprofile/'
    try:
        # getting data from backend
        records_response = call_get_method(BASEURL,endpoint,user_token)
        if records_response.status_code not in [200,201]:
            messages.error(request, f"Failed to fetch records. {records_response.json()}", extra_tags="warning")
        else:
            records = records_response.json()
            # You can pass 'records' to your template for rendering
            context = {'records': records}
            return render(request, 'marketingagentprofile_list.html', context)
    except Exception as e:
        print("An error occurred: Expecting value: line 1 column 1 (char 0)")
    return render(request,'marketingagentprofile_list.html')

# edit function
def marketingagentprofile_edit(request,pk):
    user_token=request.session['user_token']

    endpoint1='agent_user/'    
    records_response2 = call_get_method(BASEURL,endpoint1,user_token)
    print('records_response.status_code',records_response2.status_code)
    if records_response2.status_code not in [200,201]:
        messages.error(request, f"Failed to fetch records. {records_response2.json()}", extra_tags="warning")
    else:
        employee = records_response2.json()
    marketingagentprofile = call_get_method(BASEURL, f'marketingagentprofile/{pk}/',user_token)
    
    if marketingagentprofile.status_code in [200,201]:
        marketingagentprofile_data = marketingagentprofile.json()
    else:
        print('error------',marketingagentprofile)
        messages.error(request, 'Failed to retrieve data for marketingagentprofile. Please check your connection and try again.', extra_tags='warning')
        return redirect('marketingagentprofile')

    if request.method=="POST":
        form=MarketingAgentProfileForm(request.POST, initial=marketingagentprofile_data,user_choices=employee)
        if form.is_valid():
            updated_data = form.cleaned_data
            for field_name, field in form.fields.items():
                if isinstance(field.widget, forms.DateInput) or isinstance(field, forms.DateField) or isinstance(field, forms.DateTimeField):
                    if updated_data[field_name]:
                        del updated_data[field_name]
                        updated_data[field_name] = request.POST.get(field_name)
            # Serialize the updated data as JSON
            json_data = json.dumps(updated_data)
            response = call_put_method_without_token(BASEURL, f'marketingagentprofile/{pk}/', json_data)

            if response.status_code in [200,201]: 
                messages.success(request, 'Your data has been successfully saved', extra_tags='success')
                return redirect('marketingagentprofile_list') 
            else:
                error_message = response.json()
                messages.error(request, f"Oops..! {error_message}", extra_tags='warning')
        else:
            print("An error occurred: Expecting value: line 1 column 1 (char 0)")
    else:
        form = MarketingAgentProfileForm(initial=marketingagentprofile_data,user_choices=employee)

    context={
        'form':form,
    }
    return render(request,'marketingagentprofile_edit.html',context)

def marketingagentprofile_delete(request,pk):
    end_point = f'marketingagentprofile/{pk}/'
    marketingagentprofile = call_delete_method_without_token(BASEURL, end_point)
    if marketingagentprofile.status_code not in [200,201]:
        messages.error(request, 'Failed to delete data for marketingagentprofile. Please try again.', extra_tags='warning')
        return redirect('marketingagentprofile_list')
    else:
        messages.success(request, 'Successfully deleted data for marketingagentprofile', extra_tags='success')
        return redirect('marketingagentprofile_list')

# create and view table function
def issuereport(request):
    user_token=request.session['user_token']
    endpoint1='UserManagement/user/'    
    records_response2 = call_get_method(BASEURL,endpoint1,user_token)
    print('records_response.status_code',records_response2.status_code)
    if records_response2.status_code not in [200,201]:
        messages.error(request, f"Failed to fetch records. {records_response2.json()}", extra_tags="warning")
    else:
        employee = records_response2.json()
    form=IssueReportForm(user_choices=employee)
    endpoint = 'issuereport/'
    if request.method=="POST":
        form=IssueReportForm(request.POST,user_choices=employee)
        if form.is_valid():
            Output = form.cleaned_data
            Output['branch']=request.session['branch']

            for field_name, field in form.fields.items():
                if isinstance(field.widget, forms.DateInput) or isinstance(field, forms.DateField) or isinstance(field, forms.DateTimeField):
                    if Output[field_name]:
                        del Output[field_name]
                        Output[field_name] = request.POST.get(field_name)
            json_data=json.dumps(Output)
            response = call_post_method_for_without_token(BASEURL,endpoint,json_data)
            if response.status_code not in [200,201]:
                print("error",response)
            else:
                messages.success(request,'Data Successfully Saved', extra_tags="success")
                return redirect('issuereport_list')
    else:
        print('errorss',form.errors)
    try:
        # getting data from backend
        records_response = call_get_method_without_token(BASEURL,endpoint)
        if records_response.status_code not in [200,201]:
            messages.error(request, f"Failed to fetch records. {records_response.json()}", extra_tags="warning")
        else:
            records = records_response.json()
            # You can pass 'records' to your template for rendering
            context = {'form': form, 'records': records}
            return render(request, 'issuereport.html', context)
    except Exception as e:
        print("An error occurred: Expecting value: line 1 column 1 (char 0)")
    context={
        'form':form,
    }
    return render(request,'issuereport.html',context)

def issuereport_list(request):
    try:
        endpoint = 'issuereport/'
        # getting data from backend
        records_response = call_get_method_without_token(BASEURL,endpoint)
        if records_response.status_code not in [200,201]:
            messages.error(request, f"Failed to fetch records. {records_response.json()}", extra_tags="warning")
        else:
            records = records_response.json()
            print('--',records)
            # You can pass 'records' to your template for rendering
            context = { 'records': records}
            return render(request, 'issuereport_list.html', context)
    except Exception as e:
        print("An error occurred: Expecting value: line 1 column 1 (char 0)")

    return render(request,'issuereport_list.html',context)
# edit function
def issuereport_edit(request,pk):
    user_token=request.session['user_token']

    endpoint1='UserManagement/user/'    
    records_response2 = call_get_method(BASEURL,endpoint1,user_token)
    print('records_response.status_code',records_response2.status_code)
    if records_response2.status_code not in [200,201]:
        messages.error(request, f"Failed to fetch records. {records_response2.json()}", extra_tags="warning")
    else:
        employee = records_response2.json()
    issuereport = call_get_method_without_token(BASEURL, f'issuereport/{pk}/')
    
    if issuereport.status_code in [200,201]:
        issuereport_data = issuereport.json()
    else:
        print('error------',issuereport)
        messages.error(request, 'Failed to retrieve data for issuereport. Please check your connection and try again.', extra_tags='warning')
        return redirect('issuereport_list')

    if request.method=="POST":
        form=IssueReportForm(request.POST, initial=issuereport_data,user_choices=employee)
        if form.is_valid():
            updated_data = form.cleaned_data
            for field_name, field in form.fields.items():
                if isinstance(field.widget, forms.DateInput) or isinstance(field, forms.DateField) or isinstance(field, forms.DateTimeField):
                    if updated_data[field_name]:
                        del updated_data[field_name]
                        updated_data[field_name] = request.POST.get(field_name)
            # Serialize the updated data as JSON
            json_data = json.dumps(updated_data)
            response = call_put_method_without_token(BASEURL, f'issuereport/{pk}/', json_data)

            if response.status_code in [200,201]: 
                messages.success(request, 'Your data has been successfully saved', extra_tags='success')
                return redirect('issuereport_list') 
            else:
                error_message = response.json()
                messages.error(request, f"Oops..! {error_message}", extra_tags='warning')
        else:
            print("An error occurred: Expecting value: line 1 column 1 (char 0)")
    else:
        form = IssueReportForm(initial=issuereport_data,user_choices=employee)

    context={
        'form':form,
    }
    return render(request,'issuereport_edit.html',context)

def issuereport_delete(request,pk):
    end_point = f'issuereport/{pk}/'
    issuereport = call_delete_method_without_token(BASEURL, end_point)
    if issuereport.status_code not in [200,201]:
        messages.error(request, 'Failed to delete data for issuereport. Please try again.', extra_tags='warning')
        return redirect('issuereport_list')
    else:
        messages.success(request, 'Successfully deleted data for issuereport', extra_tags='success')
        return redirect('issuereport_list')

# create and view table function
def notification(request):
    form=NotificationForm()
    endpoint = 'notification/'
    if request.method=="POST":
        form=NotificationForm(request.POST)
        if form.is_valid():
            Output = form.cleaned_data
            Output['branch']=request.session['branch']
            Output['created_by']=request.session['user_data']['id']

            for field_name, field in form.fields.items():
                if isinstance(field.widget, forms.DateInput) or isinstance(field, forms.DateField) or isinstance(field, forms.DateTimeField):
                    if Output[field_name]:
                        del Output[field_name]
                        Output[field_name] = request.POST.get(field_name)
            json_data=json.dumps(Output)
            response = call_post_method_for_without_token(BASEURL,endpoint,json_data)
            if response.status_code not in [200,201]:
                print("error",response)
            else:
                messages.success(request,'Data Successfully Saved', extra_tags="success")
                return redirect('notification_list')
    else:
        print('errorss',form.errors)
    try:
        # getting data from backend
        records_response = call_get_method_without_token(BASEURL,endpoint)
        if records_response.status_code not in [200,201]:
            messages.error(request, f"Failed to fetch records. {records_response.json()}", extra_tags="warning")
        else:
            records = records_response.json()
            # You can pass 'records' to your template for rendering
            context = {'form': form, 'records': records}
            return render(request, 'notification.html', context)
    except Exception as e:
        print("An error occurred: Expecting value: line 1 column 1 (char 0)")
    context={
        'form':form,
    }
    return render(request,'notification.html',context)

def notification_list(request):
    endpoint = 'notification/'
    try:
        # getting data from backend
        records_response = call_get_method_without_token(BASEURL,endpoint)
        if records_response.status_code not in [200,201]:
            messages.error(request, f"Failed to fetch records. {records_response.json()}", extra_tags="warning")
        else:
            records = records_response.json()
            # You can pass 'records' to your template for rendering
            context = {'records': records}
            return render(request, 'notification_list.html', context)
    except Exception as e:
        print("An error occurred: Expecting value: line 1 column 1 (char 0)")
    return render(request,'notification_list.html')

# edit function
def notification_edit(request,pk):
    notification = call_get_method_without_token(BASEURL, f'notification/{pk}/')
    
    if notification.status_code in [200,201]:
        notification_data = notification.json()
    else:
        print('error------',notification)
        messages.error(request, 'Failed to retrieve data for notification. Please check your connection and try again.', extra_tags='warning')
        return redirect('notification')

    if request.method=="POST":
        form=NotificationForm(request.POST, initial=notification_data)
        if form.is_valid():
            updated_data = form.cleaned_data
            for field_name, field in form.fields.items():
                if isinstance(field.widget, forms.DateInput) or isinstance(field, forms.DateField) or isinstance(field, forms.DateTimeField):
                    if updated_data[field_name]:
                        del updated_data[field_name]
                        updated_data[field_name] = request.POST.get(field_name)
            # Serialize the updated data as JSON
            json_data = json.dumps(updated_data)
            response = call_put_method_without_token(BASEURL, f'notification/{pk}/', json_data)

            if response.status_code in [200,201]: 
                messages.success(request, 'Your data has been successfully saved', extra_tags='success')
                return redirect('notification') 
            else:
                error_message = response.json()
                messages.error(request, f"Oops..! {error_message}", extra_tags='warning')
        else:
            print("An error occurred: Expecting value: line 1 column 1 (char 0)")
    else:
        form = NotificationForm(initial=notification_data)

    context={
        'form':form,
    }
    return render(request,'notification_edit.html',context)

def notification_delete(request,pk):
    end_point = f'notification/{pk}/'
    notification = call_delete_method_without_token(BASEURL, end_point)
    if notification.status_code not in [200,201]:
        messages.error(request, 'Failed to delete data for notification. Please try again.', extra_tags='warning')
        return redirect('notification')
    else:
        messages.success(request, 'Successfully deleted data for notification', extra_tags='success')
        return redirect('notification')

# create and view table function
def lawyerprofile(request):
    user_token=request.session['user_token']
    endpoint2='lawyer_user/'    
    records_response2 = call_get_method(BASEURL,endpoint2,user_token)
    print('records_response.status_code',records_response2.status_code)
    print('lawyers',records_response2.json())
    if records_response2.status_code not in [200,201]:
        messages.error(request, f"Failed to fetch records. {records_response2.json()}", extra_tags="warning")
    else:
        employee = records_response2.json()
    form=LawyerProfileForm(user_choices=employee)
    endpoint = 'lawyerprofile/'
    if request.method=="POST":
        form=LawyerProfileForm(request.POST,user_choices=employee)
        if form.is_valid():
            Output = form.cleaned_data
            Output['branch']=request.session['branch']
            Output['created_by']=request.session['user_data']['id']

            for field_name, field in form.fields.items():
                if isinstance(field.widget, forms.DateInput) or isinstance(field, forms.DateField) or isinstance(field, forms.DateTimeField):
                    if Output[field_name]:
                        del Output[field_name]
                        Output[field_name] = request.POST.get(field_name)
            json_data=json.dumps(Output)
            response = call_post_method_for_without_token(BASEURL,endpoint,json_data)
            if response.status_code not in [200,201]:
                print("error",response)
            else:
                messages.success(request,'Data Successfully Saved', extra_tags="success")
                return redirect('lawyerprofile_list')
    else:
        print('errorss',form.errors)
    try:
        # getting data from backend
        records_response = call_get_method(BASEURL,endpoint,user_token)
        if records_response.status_code not in [200,201]:
            messages.error(request, f"Failed to fetch records. {records_response.json()}", extra_tags="warning")
        else:
            records = records_response.json()
            print('---',records)
            # You can pass 'records' to your template for rendering
            context = {'form': form, 'records': records}
            return render(request, 'lawyerprofile.html', context)
    except Exception as e:
        print("An error occurred: Expecting value: line 1 column 1 (char 0)")
    context={
        'form':form,
    }
    return render(request,'lawyerprofile.html',context)

def lawyerprofile_list(request):
    user_token=request.session['user_token']
    endpoint = 'lawyerprofile/'
    try:
        # getting data from backend
        records_response = call_get_method(BASEURL,endpoint,user_token)
        if records_response.status_code not in [200,201]:
            messages.error(request, f"Failed to fetch records. {records_response.json()}", extra_tags="warning")
        else:
            records = records_response.json()
            # You can pass 'records' to your template for rendering
            context = {'records': records}
            return render(request, 'lawyerprofile_list.html', context)
    except Exception as e:
        print("An error occurred: Expecting value: line 1 column 1 (char 0)")
    return render(request,'lawyerprofile_list.html')

# edit function
def lawyerprofile_edit(request,pk):
    user_token=request.session['user_token']
    endpoint1='lawyer_user/'    
    records_response2 = call_get_method(BASEURL,endpoint1,user_token)
    print('records_response.status_code',records_response2.status_code)
    if records_response2.status_code not in [200,201]:
        messages.error(request, f"Failed to fetch records. {records_response2.json()}", extra_tags="warning")
    else:
        employee = records_response2.json()
        print('----',employee)
    lawyerprofile = call_get_method(BASEURL, f'lawyerprofile/{pk}/',user_token)
    
    if lawyerprofile.status_code in [200,201]:
        lawyerprofile_data = lawyerprofile.json()
        print('data-----',lawyerprofile_data)

    else:
        print('error------',lawyerprofile.status_code)
        messages.error(request, 'Failed to retrieve data for lawyerprofile. Please check your connection and try again.', extra_tags='warning')
        return redirect('lawyerprofile_list')

    if request.method=="POST":
        form=LawyerProfileForm(request.POST, initial=lawyerprofile_data,user_choices=employee)
        if form.is_valid():
            updated_data = form.cleaned_data
            for field_name, field in form.fields.items():
                if isinstance(field.widget, forms.DateInput) or isinstance(field, forms.DateField) or isinstance(field, forms.DateTimeField):
                    if updated_data[field_name]:
                        del updated_data[field_name]
                        updated_data[field_name] = request.POST.get(field_name)
            # Serialize the updated data as JSON
            json_data = json.dumps(updated_data)
            response = call_put_method_without_token(BASEURL, f'lawyerprofile/{pk}/', json_data)

            if response.status_code in [200,201]: 
                messages.success(request, 'Your data has been successfully saved', extra_tags='success')
                return redirect('lawyerprofile_list') 
            else:
                error_message = response.json()
                messages.error(request, f"Oops..! {error_message}", extra_tags='warning')
        else:
            print("An error occurred: Expecting value: line 1 column 1 (char 0)")
    else:
        form = LawyerProfileForm(initial=lawyerprofile_data,user_choices=employee)

    context={
        'form':form,
    }
    return render(request,'lawyerprofile_edit.html',context)

def lawyerprofile_delete(request,pk):
    end_point = f'lawyerprofile/{pk}/'
    lawyerprofile = call_delete_method_without_token(BASEURL, end_point)
    if lawyerprofile.status_code not in [200,201]:
        messages.error(request, 'Failed to delete data for lawyerprofile. Please try again.', extra_tags='warning')
        return redirect('lawyerprofile_list')
    else:
        messages.success(request, 'Successfully deleted data for lawyerprofile', extra_tags='success')
        return redirect('lawyerprofile_list')

# create and view table function
def members(request):
    form=MembersForm()
    endpoint = 'members/'
    if request.method=="POST":
        form=MembersForm(request.POST)
        if form.is_valid():
            Output = form.cleaned_data
            Output['branch']=request.session['branch']
            Output['created_by']=request.session['user_data']['id']

            for field_name, field in form.fields.items():
                if isinstance(field.widget, forms.DateInput) or isinstance(field, forms.DateField) or isinstance(field, forms.DateTimeField):
                    if Output[field_name]:
                        del Output[field_name]
                        Output[field_name] = request.POST.get(field_name)
            json_data=json.dumps(Output)
            response = call_post_method_for_without_token(BASEURL,endpoint,json_data)
            if response.status_code not in [200,201]:
                print("error",response)
            else:
                messages.success(request,'Data Successfully Saved', extra_tags="success")
                return redirect('members_list')
    else:
        print('errorss',form.errors)
    try:
        # getting data from backend
        records_response = call_get_method_without_token(BASEURL,endpoint)
        if records_response.status_code not in [200,201]:
            messages.error(request, f"Failed to fetch records. {records_response.json()}", extra_tags="warning")
        else:
            records = records_response.json()
            # You can pass 'records' to your template for rendering
            context = {'form': form, 'records': records}
            return render(request, 'members.html', context)
    except Exception as e:
        print("An error occurred: Expecting value: line 1 column 1 (char 0)")
    context={
        'form':form,
    }
    return render(request,'members.html',context)

def members_list(request):
    endpoint = 'members/'
    try:
        # getting data from backend
        records_response = call_get_method_without_token(BASEURL,endpoint)
        if records_response.status_code not in [200,201]:
            messages.error(request, f"Failed to fetch records. {records_response.json()}", extra_tags="warning")
        else:
            records = records_response.json()
            # You can pass 'records' to your template for rendering
            context = {'records': records}
            return render(request, 'members_list.html', context)
    except Exception as e:
        print("An error occurred: Expecting value: line 1 column 1 (char 0)")
    return render(request,'members_list.html')

# edit function
def members_edit(request,pk):
    members = call_get_method_without_token(BASEURL, f'members/{pk}/')
    
    if members.status_code in [200,201]:
        members_data = members.json()
    else:
        print('error------',members)
        messages.error(request, 'Failed to retrieve data for members. Please check your connection and try again.', extra_tags='warning')
        return redirect('members')

    if request.method=="POST":
        form=MembersForm(request.POST, initial=members_data)
        if form.is_valid():
            updated_data = form.cleaned_data
            for field_name, field in form.fields.items():
                if isinstance(field.widget, forms.DateInput) or isinstance(field, forms.DateField) or isinstance(field, forms.DateTimeField):
                    if updated_data[field_name]:
                        del updated_data[field_name]
                        updated_data[field_name] = request.POST.get(field_name)
            # Serialize the updated data as JSON
            json_data = json.dumps(updated_data)
            response = call_put_method_without_token(BASEURL, f'members/{pk}/', json_data)

            if response.status_code in [200,201]: 
                messages.success(request, 'Your data has been successfully saved', extra_tags='success')
                return redirect('members') 
            else:
                error_message = response.json()
                messages.error(request, f"Oops..! {error_message}", extra_tags='warning')
        else:
            print("An error occurred: Expecting value: line 1 column 1 (char 0)")
    else:
        form = MembersForm(initial=members_data)

    context={
        'form':form,
    }
    return render(request,'members_edit.html',context)

def members_delete(request,pk):
    end_point = f'members/{pk}/'
    members = call_delete_method_without_token(BASEURL, end_point)
    if members.status_code not in [200,201]:
        messages.error(request, 'Failed to delete data for members. Please try again.', extra_tags='warning')
        return redirect('members')
    else:
        messages.success(request, 'Successfully deleted data for members', extra_tags='success')
        return redirect('members')

# create and view table function
def events(request):
    user_token=request.session['user_token']

    form=EventsForm()
    endpoint = 'events/'
    if request.method=="POST":
        form=EventsForm(request.POST)
        if form.is_valid():
            Output = form.cleaned_data
            Output['branch']=request.session['branch']
            Output['created_by']=request.session['user_data']['id']

            for field_name, field in form.fields.items():
                if isinstance(field.widget, forms.DateInput) or isinstance(field, forms.DateField) or isinstance(field, forms.DateTimeField)  or isinstance(field, forms.TimeField):
                    if Output[field_name]:
                        del Output[field_name]
                        Output[field_name] = request.POST.get(field_name)
            json_data=json.dumps(Output)
            response = call_post_method_for_without_token(BASEURL,endpoint,json_data)
            if response.status_code not in [200,201]:
                print("error",response)
            else:
                messages.success(request,'Data Successfully Saved', extra_tags="success")
                return redirect('events_list')
    else:
        print('errorss',form.errors)
    try:
        # getting data from backend
        records_response = call_get_method(BASEURL,endpoint,user_token)
        if records_response.status_code not in [200,201]:
            messages.error(request, f"Failed to fetch records. {records_response.json()}", extra_tags="warning")
        else:
            records = records_response.json()
            # You can pass 'records' to your template for rendering
            context = {'form': form, 'records': records}
            return render(request, 'events.html', context)
    except Exception as e:
        print("An error occurred: Expecting value: line 1 column 1 (char 0)")
    context={
        'form':form,
    }
    return render(request,'events.html',context)

def events_list(request):
    endpoint = 'events/'
    try:
        # getting data from backend
        records_response = call_get_method_without_token(BASEURL,endpoint)
        if records_response.status_code not in [200,201]:
            messages.error(request, f"Failed to fetch records. {records_response.json()}", extra_tags="warning")
        else:
            records = records_response.json()
            # You can pass 'records' to your template for rendering
            context = {'records': records}
            return render(request, 'events_list.html', context)
    except Exception as e:
        print("An error occurred: Expecting value: line 1 column 1 (char 0)")
    return render(request,'events_list.html')


# edit function
def events_edit(request,pk):
    events = call_get_method_without_token(BASEURL, f'events/{pk}/')
    
    if events.status_code in [200,201]:
        events_data = events.json()
    else:
        print('error------',events)
        messages.error(request, 'Failed to retrieve data for events. Please check your connection and try again.', extra_tags='warning')
        return redirect('events')

    if request.method=="POST":
        form=EventsForm(request.POST, initial=events_data)
        if form.is_valid():
            updated_data = form.cleaned_data
            for field_name, field in form.fields.items():
                if isinstance(field.widget, forms.DateInput) or isinstance(field, forms.DateField) or isinstance(field, forms.DateTimeField):
                    if updated_data[field_name]:
                        del updated_data[field_name]
                        updated_data[field_name] = request.POST.get(field_name)
            # Serialize the updated data as JSON
            json_data = json.dumps(updated_data)
            response = call_put_method_without_token(BASEURL, f'events/{pk}/', json_data)

            if response.status_code in [200,201]: 
                messages.success(request, 'Your data has been successfully saved', extra_tags='success')
                return redirect('events') 
            else:
                error_message = response.json()
                messages.error(request, f"Oops..! {error_message}", extra_tags='warning')
        else:
            print("An error occurred: Expecting value: line 1 column 1 (char 0)")
    else:
        form = EventsForm(initial=events_data)

    context={
        'form':form,
    }
    return render(request,'events_edit.html',context)

def events_delete(request,pk):
    end_point = f'events/{pk}/'
    events = call_delete_method_without_token(BASEURL, end_point)
    if events.status_code not in [200,201]:
        messages.error(request, 'Failed to delete data for events. Please try again.', extra_tags='warning')
        return redirect('events')
    else:
        messages.success(request, 'Successfully deleted data for events', extra_tags='success')
        return redirect('events')

# create and view table function
def stafffeedback(request):
    endpoint1='UserManagement/user/'    
    records_response2 = call_get_method_without_token(BASEURL,endpoint1)
    print('records_response.status_code',records_response2.status_code)
    if records_response2.status_code not in [200,201]:
        messages.error(request, f"Failed to fetch records. {records_response2.json()}", extra_tags="warning")
    else:
        employee = records_response2.json()
    form=StaffFeedbackForm(user_choices=employee)
    endpoint = 'stafffeedback/'
    if request.method=="POST":
        form=StaffFeedbackForm(request.POST,user_choices=employee)
        if form.is_valid():
            Output = form.cleaned_data
            Output['branch']=request.session['branch']
            Output['created_by']=request.session['user_data']['id']

            for field_name, field in form.fields.items():
                if isinstance(field.widget, forms.DateInput) or isinstance(field, forms.DateField) or isinstance(field, forms.DateTimeField):
                    if Output[field_name]:
                        del Output[field_name]
                        Output[field_name] = request.POST.get(field_name)
            json_data=json.dumps(Output)
            response = call_post_method_for_without_token(BASEURL,endpoint,json_data)
            if response.status_code not in [200,201]:
                print("error",response)
            else:
                messages.success(request,'Data Successfully Saved', extra_tags="success")
                return redirect('stafffeedback')
    else:
        print('errorss',form.errors)
    try:
        # getting data from backend
        records_response = call_get_method_without_token(BASEURL,endpoint)
        if records_response.status_code not in [200,201]:
            messages.error(request, f"Failed to fetch records. {records_response.json()}", extra_tags="warning")
        else:
            records = records_response.json()
            # You can pass 'records' to your template for rendering
            context = {'form': form, 'records': records}
            return render(request, 'stafffeedback.html', context)
    except Exception as e:
        print("An error occurred: Expecting value: line 1 column 1 (char 0)")
    context={
        'form':form,
    }
    return render(request,'stafffeedback.html',context)


# edit function
def stafffeedback_edit(request,pk):
    endpoint1='UserManagement/user/'    
    records_response2 = call_get_method_without_token(BASEURL,endpoint1)
    print('records_response.status_code',records_response2.status_code)
    if records_response2.status_code not in [200,201]:
        messages.error(request, f"Failed to fetch records. {records_response2.json()}", extra_tags="warning")
    else:
        employee = records_response2.json()
    stafffeedback = call_get_method_without_token(BASEURL, f'stafffeedback/{pk}/')
    
    if stafffeedback.status_code in [200,201]:
        stafffeedback_data = stafffeedback.json()
    else:
        print('error------',stafffeedback)
        messages.error(request, 'Failed to retrieve data for stafffeedback. Please check your connection and try again.', extra_tags='warning')
        return redirect('stafffeedback')

    if request.method=="POST":
        form=StaffFeedbackForm(request.POST, initial=stafffeedback_data,user_choices=employee)
        if form.is_valid():
            updated_data = form.cleaned_data
            for field_name, field in form.fields.items():
                if isinstance(field.widget, forms.DateInput) or isinstance(field, forms.DateField) or isinstance(field, forms.DateTimeField):
                    if updated_data[field_name]:
                        del updated_data[field_name]
                        updated_data[field_name] = request.POST.get(field_name)
            # Serialize the updated data as JSON
            json_data = json.dumps(updated_data)
            response = call_put_method_without_token(BASEURL, f'stafffeedback/{pk}/', json_data)

            if response.status_code in [200,201]: 
                messages.success(request, 'Your data has been successfully saved', extra_tags='success')
                return redirect('stafffeedback') 
            else:
                error_message = response.json()
                messages.error(request, f"Oops..! {error_message}", extra_tags='warning')
        else:
            print("An error occurred: Expecting value: line 1 column 1 (char 0)")
    else:
        form = StaffFeedbackForm(initial=stafffeedback_data,user_choices=employee)

    context={
        'form':form,
    }
    return render(request,'stafffeedback_edit.html',context)

def stafffeedback_delete(request,pk):
    end_point = f'stafffeedback/{pk}/'
    stafffeedback = call_delete_method_without_token(BASEURL, end_point)
    if stafffeedback.status_code not in [200,201]:
        messages.error(request, 'Failed to delete data for stafffeedback. Please try again.', extra_tags='warning')
        return redirect('stafffeedback')
    else:
        messages.success(request, 'Successfully deleted data for stafffeedback', extra_tags='success')
        return redirect('stafffeedback')

# create and view table function
def taskassignment(request):
    user_token=request.session['user_token']
    endpoint1='UserManagement/user/'    
    records_response2 = call_get_method(BASEURL,endpoint1,user_token)
    print('records_response.status_code',records_response2.status_code)
    if records_response2.status_code not in [200,201]:
        messages.error(request, f"Failed to fetch records. {records_response2.json()}", extra_tags="warning")
    else:
        assigned_to = records_response2.json()
    endpoint1='issuereport/'    
    records_response2 = call_get_method_without_token(BASEURL,endpoint1)
    print('records_response.status_code',records_response2.status_code)
    if records_response2.status_code not in [200,201]:
        messages.error(request, f"Failed to fetch records. {records_response2.json()}", extra_tags="warning")
    else:
        issuereport = records_response2.json()
    form=TaskAssignmentForm(issue_choices=issuereport,user_choices=assigned_to)
    endpoint = 'taskassignment/'
    if request.method=="POST":
        form=TaskAssignmentForm(request.POST,issue_choices=issuereport,user_choices=assigned_to)
        if form.is_valid():
            Output = form.cleaned_data
            Output['branch']=request.session['branch']
            Output['assigned_by']=request.session['user_data']['id']

            for field_name, field in form.fields.items():
                if isinstance(field.widget, forms.DateInput) or isinstance(field, forms.DateField) or isinstance(field, forms.DateTimeField):
                    if Output[field_name]:
                        del Output[field_name]
                        Output[field_name] = request.POST.get(field_name)
            json_data=json.dumps(Output)
            response = call_post_method_for_without_token(BASEURL,endpoint,json_data)
            if response.status_code not in [200,201]:
                print("error",response)
            else:
                messages.success(request,'Data Successfully Saved', extra_tags="success")
                return redirect('taskassignment')
    else:
        print('errorss',form.errors)
    try:
        # getting data from backend
        records_response = call_get_method_without_token(BASEURL,endpoint)
        if records_response.status_code not in [200,201]:
            messages.error(request, f"Failed to fetch records. {records_response.json()}", extra_tags="warning")
        else:
            records = records_response.json()
            # You can pass 'records' to your template for rendering
            context = {'form': form, 'records': records}
            return render(request, 'taskassignment.html', context)
    except Exception as e:
        print("An error occurred: Expecting value: line 1 column 1 (char 0)")
    context={
        'form':form,
    }
    return render(request,'taskassignment.html',context)

def taskassignment_list(request):
    try:
        user_token=request.session['user_token']
        # getting data from backend
        endpoint = 'taskassignment/'
        records_response = call_get_method(BASEURL,endpoint,user_token)
        if records_response.status_code not in [200,201]:
            messages.error(request, f"Failed to fetch records. {records_response.json()}", extra_tags="warning")
        else:
            records = records_response.json()
            # You can pass 'records' to your template for rendering
            context = {'records': records}
            return render(request, 'taskassignment_list.html', context)
    except Exception as e:
        print("An error occurred: Expecting value: line 1 column 1 (char 0)")
# edit function
def taskassignment_edit(request,pk):
    endpoint1='UserManagement/user/'    
    records_response2 = call_get_method_without_token(BASEURL,endpoint1)
    print('records_response.status_code',records_response2.status_code)
    if records_response2.status_code not in [200,201]:
        messages.error(request, f"Failed to fetch records. {records_response2.json()}", extra_tags="warning")
    else:
        assigned_to = records_response2.json()
    endpoint1='issuereport/'    
    records_response2 = call_get_method_without_token(BASEURL,endpoint1)
    print('records_response.status_code',records_response2.status_code)
    if records_response2.status_code not in [200,201]:
        messages.error(request, f"Failed to fetch records. {records_response2.json()}", extra_tags="warning")
    else:
        issuereport = records_response2.json()
    taskassignment = call_get_method_without_token(BASEURL, f'taskassignment/{pk}/')
    
    if taskassignment.status_code in [200,201]:
        taskassignment_data = taskassignment.json()
    else:
        print('error------',taskassignment)
        messages.error(request, 'Failed to retrieve data for taskassignment. Please check your connection and try again.', extra_tags='warning')
        return redirect('taskassignment')

    if request.method=="POST":
        form=TaskAssignmentForm(request.POST, initial=taskassignment_data,issue_choices=issuereport,user_choices=assigned_to)
        if form.is_valid():
            updated_data = form.cleaned_data
            for field_name, field in form.fields.items():
                if isinstance(field.widget, forms.DateInput) or isinstance(field, forms.DateField) or isinstance(field, forms.DateTimeField):
                    if updated_data[field_name]:
                        del updated_data[field_name]
                        updated_data[field_name] = request.POST.get(field_name)
            # Serialize the updated data as JSON
            json_data = json.dumps(updated_data)
            response = call_put_method_without_token(BASEURL, f'taskassignment/{pk}/', json_data)

            if response.status_code in [200,201]: 
                messages.success(request, 'Your data has been successfully saved', extra_tags='success')
                return redirect('taskassignment') 
            else:
                error_message = response.json()
                messages.error(request, f"Oops..! {error_message}", extra_tags='warning')
        else:
            print("An error occurred: Expecting value: line 1 column 1 (char 0)")
    else:
        form = TaskAssignmentForm(initial=taskassignment_data,issue_choices=issuereport,user_choices=assigned_to)

    context={
        'form':form,
    }
    return render(request,'taskassignment_edit.html',context)

def taskassignment_delete(request,pk):
    end_point = f'taskassignment/{pk}/'
    taskassignment = call_delete_method_without_token(BASEURL, end_point)
    if taskassignment.status_code not in [200,201]:
        messages.error(request, 'Failed to delete data for taskassignment. Please try again.', extra_tags='warning')
        return redirect('taskassignment')
    else:
        messages.success(request, 'Successfully deleted data for taskassignment', extra_tags='success')
        return redirect('taskassignment')


def image_filescreate(cleaned_data):
    files = {}
    fields_to_remove = []
    print('cleaned_data',cleaned_data)
    # Identify and separate file fields
    for field_name, value in cleaned_data.items():
        if hasattr(value, 'read'):  # Check if it's a file-like object
            files[field_name] = (value.name, value, value.content_type)
            fields_to_remove.append(field_name)

    # Remove file fields from cleaned_data
    for field_name in fields_to_remove:
        cleaned_data.pop(field_name)

    # Return files and the modified cleaned_data
    return files,cleaned_data



def select_company(request):
    try:
        endpoint2='UserManagement/company/'    
        records_response2 = call_get_method_without_token(BASEURL,endpoint2)
        print('records_response.status_code',records_response2.status_code)
        if records_response2.status_code not in [200,201]:
            messages.error(request, f"Failed to fetch records. {records_response2.json()}", extra_tags="warning")
        else:
            company_list = records_response2.json()
        if request.method =='POST':
            company_id = request.POST.get('company')
            request.session['company'] = company_id if company_id else None
            return redirect('select_branch', pk=company_id)


    except Exception as e:
        print("An error occurred: Expecting value: line 1 column 1 (char 0)")
    # endpoint2='UserManagement/county/'    
    # records_response2 = call_get_method_without_token(BASEURL,endpoint2)
    # print('records_response.status_code',records_response2.status_code)
    # if records_response2.status_code not in [200,201]:
    #     messages.error(request, f"Failed to fetch records. {records_response2.json()}", extra_tags="warning")
    # else:
    #     roles = records_response2.json()
    #     print('----',roles)
    # endpoint2='UserManagement/subcounty/'    
    # records_response2 = call_get_method_without_token(BASEURL,endpoint2)
    # print('records_response.status_code',records_response2.status_code)
    # if records_response2.status_code not in [200,201]:
    #     messages.error(request, f"Failed to fetch records. {records_response2.json()}", extra_tags="warning")
    # else:
    #     sub = records_response2.json()
    # form=CompanyForm(country_choices=roles,sub_country_choices=sub)
    form=CompanyForm()
    return render(request,'select_company.html',{'company_list':company_list,'form':form})



def select_branch(request,pk):
    try:
        user_token=request.session['user_token']
        print('---user_token',user_token)
        print('==',pk)
        endpoint2=f'UserManagement/select_branch/{pk}'    
        records_response2 = call_get_method_without_token(BASEURL,endpoint2)
        print('records_response.status_code',records_response2.status_code)
        branch_list1=[]
        if records_response2.status_code not in [200,201]:
            messages.error(request, f"Failed to fetch records. {records_response2.json()}", extra_tags="warning")
        else:
            branch_list = records_response2.json()
            print('----',branch_list )
            # branch_list1.append(branch_list)
        endpoint2=f'UserManagement/company/{pk}'    
        records_response2 = call_get_method_without_token(BASEURL,endpoint2)
        print('records_response.status_code',records_response2.status_code)
        if records_response2.status_code not in [200,201]:
            messages.error(request, f"Failed to fetch records. {records_response2.json()}", extra_tags="warning")
        else:
            company = records_response2.json()
            print('----',company )
        if request.method =='POST':
            branch_id = request.POST.get('branch')
            request.session['branch'] = branch_id if branch_id else None
            print('----branch---',branch_id)
        endpoint4=f'UserManagement/user_update/' 
        print(endpoint4)   
        records_response2 = call_put_method(BASEURL,endpoint4,branch_id,user_token)
        print('records_response.status_code',records_response2.json())
        if records_response2.status_code not in [200,201]:
            messages.error(request, f"Failed to fetch records. {records_response2.json()}", extra_tags="warning")
        else:
            company = records_response2.json()
            print('----',company )
            return redirect('dashboard')                
        print('----',branch_list1 )

    except Exception as e:
        print("An error occurred: Expecting value: line 1 column 1 (char 0)")
    # endpoint2='UserManagement/company/'    
    # records_response2 = call_get_method_without_token(BASEURL,endpoint2)
    # print('records_response.status_code',records_response2.status_code)
    # if records_response2.status_code not in [200,201]:
    #     messages.error(request, f"Failed to fetch records. {records_response2.json()}", extra_tags="warning")
    # else:
    #     roles = records_response2.json()
    #     # print('===',records)
    # endpoint1='UserManagement/county/'    
    # records_response2 = call_get_method_without_token(BASEURL,endpoint1)
    # print('records_response.status_code',records_response2.status_code)
    # if records_response2.status_code not in [200,201]:
    #     messages.error(request, f"Failed to fetch records. {records_response2.json()}", extra_tags="warning")
    # else:
    #     country = records_response2.json()
    # endpoint2='UserManagement/subcounty/'    
    # records_response2 = call_get_method_without_token(BASEURL,endpoint2)
    # print('records_response.status_code',records_response2.status_code)
    # if records_response2.status_code not in [200,201]:
    #     messages.error(request, f"Failed to fetch records. {records_response2.json()}", extra_tags="warning")
    # else:
    #     sub = records_response2.json()
    # form=BranchForm(request.POST,country_choices=country,sub_country_choices=sub)
    form=BranchForm()

    return render(request,'select_branch.html',{'branch_list':branch_list,'form':form,'company':company})

def document_entity(request):
    try:
        user_token=request.session['user_token']

        # Getting data from backend
        endpoint = 'entities/'
        records_response = call_get_method(BASEURL, endpoint,user_token)

        if records_response.status_code not in [200, 201]:
            try:
                error_msg = records_response.json()
            except json.JSONDecodeError:
                error_msg = records_response.text
            messages.error(request, f"Failed to fetch records. {error_msg}", extra_tags="warning")
            return render(request, 'entity_list.html', {'records': []})  # Return empty list if failed
        else:
            records = records_response.json()
            print('-----', records)
            context = {'records': records}
            return render(request, 'entity_list.html', context)

    except Exception as e:
        print(f"An error occurred: {e}")
        messages.error(request, f"An unexpected error occurred: {e}", extra_tags="danger")
        return render(request, 'entity_list.html', {'records': []})


# def get_documents(request, entityId):
#     # Getting data from backend
#     endpoint = f'folder/{entityId}'
#     records_response = call_get_method_without_token(BASEURL, endpoint)

#     if records_response.status_code not in [200, 201]:
#         error_msg = "Error fetching records"  # Simplified error message
#         return JsonResponse({'error': error_msg}, status=400)
#     else:
#         records = records_response.json()
#         # Only return the id and folder_name for each document
#         simplified_records = [{'id': record['id'], 'folder_name': record['folder_name']} for record in records]
#         print('---',simplified_records)
#         return JsonResponse({'records': simplified_records})

def get_documents(request, entityId):
    try:
        # Getting data from backend
        endpoint = f'folder/{entityId}'
        records_response = call_get_method_without_token(BASEURL, endpoint)

        if records_response.status_code not in [200, 201]:
            try:
                error_msg = records_response.json()
            except json.JSONDecodeError:
                error_msg = records_response.text
            messages.error(request, f"Failed to fetch records. {error_msg}", extra_tags="warning")
            return render(request, 'folder_list.html', {'records': []})  # Return empty list if failed
        else:
            records = records_response.json()
            print('-----', records)
            context = {'records': records}
            return render(request, 'folder_list.html', context)

    except Exception as e:
        print(f"An error occurred: {e}")
        messages.error(request, f"An unexpected error occurred: {e}", extra_tags="danger")
        return render(request, 'folder_list.html', {'records': []})

def timesheets_report(request):
    user_token = request.session.get('user_token')
    form = TimesheetRepotForm(request.POST or None)
    context = {'form': form, 'timesheets': []}

    if request.method == "POST" and form.is_valid():
        date = form.cleaned_data.get('date')
        status = form.cleaned_data.get('status')

        date_str = date.strftime('%Y-%m-%d') if date else ''
        status_param = f'status={status}' if status else ''
        
        # Build URL dynamically depending on available filters
        endpoint = 'timesheets_report/'
        if date_str:
            endpoint += f'{date_str}/'
        if status_param:
            endpoint += f'?{status_param}' if '?' not in endpoint else f'&{status_param}'

        try:
            response = call_get_method(BASEURL, endpoint, user_token)
            print('response', response.json())

            if response.status_code in [200, 201]:
                context['timesheets'] = response.json()
                messages.success(request, 'Timesheets retrieved successfully.', extra_tags='success')
            else:
                messages.error(request, 'Failed to retrieve timesheets.', extra_tags='danger')
        except Exception as e:
            messages.error(request, f'Error: {str(e)}', extra_tags='danger')

    return render(request, 'reports/timesheets_report.html', context)

def loancase_report(request):
    user_token = request.session.get('user_token')
    form = LoanCaseRepotForm(request.POST or None)
    context = {'form': form, 'loancases': []}

    if request.method == "POST" and form.is_valid():
        date = form.cleaned_data.get('date')
        date_str = date.strftime('%Y-%m-%d') if date else ''
        
        endpoint = f'loancase_report/{date_str}/' if date_str else 'loancase_report/'

        try:
            response = call_get_method(BASEURL, endpoint, user_token)
            if response.status_code in [200, 201]:
                context['loancases'] = response.json()
                messages.success(request, 'Loan cases retrieved successfully.', extra_tags='success')
            else:
                messages.error(request, 'Failed to retrieve loan cases.', extra_tags='danger')
        except Exception as e:
            messages.error(request, f'Error: {str(e)}', extra_tags='danger')

    return render(request, 'reports/loancase_report.html', context)
