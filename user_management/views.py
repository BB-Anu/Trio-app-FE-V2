import json
from pyexpat.errors import messages
from django.shortcuts import redirect, render
from .forms import *
from mainapp.api_call import call_get_method_without_token
from django.conf import settings
from mainapp.api_call import *
from django.contrib import messages

BASEURL = 'http://127.0.0.1:9000/'
APP_BUILDER = 'http://127.0.0.1:8000/'

def functions(request):
    endpoint = 'UserManagement/function_all/'
        # getting data from backend
    records_response = call_get_method_without_token(BASEURL,endpoint)
    print('records_response',records_response)
    if records_response.status_code not in [200,201]:
        messages.error(request, f"Failed to fetch records. {records_response.json()}", extra_tags="warning")
    else:
        records = records_response.json()
        print('records',records)
        return redirect('role')

def permission(request,role_id):
    endpoint = f'UserManagement/permission/{role_id}/' 
    records_response = call_get_method_without_token(BASEURL, endpoint)
    print('records_response',records_response)
    if records_response.status_code not in [200, 201]:
        messages.error(request, f"Failed to fetch records. {records_response.json()}", extra_tags="warning")

    records = records_response.json()
    print('records',records)
    return redirect('user')


def user_permission(request,user_id):
    endpoint = f'UserManagement/user_permission/{user_id}/' 
    records_response = call_get_method_without_token(BASEURL, endpoint)
    print('records_response',records_response)
    if records_response.status_code not in [200, 201]:
        messages.error(request, f"Failed to fetch records. {records_response.json()}", extra_tags="warning")

    records = records_response.json()
    print('records',records)
    return redirect('user')

def role(request):
    endpoint = 'UserManagement/role/'
    endpoint1 = 'UserManagement/api_functions_setup/'
    records_response1 = call_get_method_without_token(BASEURL, endpoint1)
    print('records_response.status_code', records_response1.status_code)
    permissions = []
    permissions = records_response1.json()
    print("Raw API Response:", permissions)
    permissions_data = permissions['functions']
 
    print("Formatted Permissions:", permissions_data)  # Debugging

    if request.method == "POST":
        form = RoleForm(request.POST, permissions_choices=permissions_data)
        if form.is_valid():
            Output = form.cleaned_data
            Output['branch']=request.session['branch']
            print('Output', Output)
            
            # Handle date fields if needed
            for field_name, field in form.fields.items():
                if isinstance(field.widget, forms.DateInput) or isinstance(field, forms.DateField) or isinstance(field, forms.DateTimeField):
                    if Output.get(field_name):
                        Output[field_name] = request.POST.get(field_name)
            
            json_data = json.dumps(Output)
            response = call_post_method_for_without_token(BASEURL, endpoint, json_data)
            
            if response.status_code not in [200, 201]:
                print("error", response)
            else:
                messages.success(request, 'Data Successfully Saved', extra_tags="success")
                return redirect('role_list')
    else:
        form = RoleForm(permissions_choices=permissions_data)

    # try:
    #     records_response = call_get_method_without_token(BASEURL, endpoint)
    #     if records_response.status_code not in [200, 201]:
    #         messages.error(request, f"Failed to fetch records. {records_response.json()}", extra_tags="warning")
    #         records = []
    #     else:
    #         records = records_response.json()
    # except Exception as e:
    #     print("An error occurred:", str(e))
    #     records = []

    context = {
        'form': form,
        # 'records': records,
    }
    return render(request, 'role.html', context)

def role_list(request):
    user_token=request.session['user_token']

    endpoint = 'UserManagement/role/'
    records_response = call_get_method(BASEURL, endpoint,user_token)
    if records_response.status_code not in [200, 201]:
        messages.error(request, f"Failed to fetch records. {records_response.json()}", extra_tags="warning")
        records = []
    else:
        records = records_response.json()
    context = {
        'records': records,
    }
    return render(request, 'role_list.html', context)

# edit function
def role_edit(request,pk):
    user_token=request.session['user_token']

    endpoint1 = 'UserManagement/api_functions_setup/'
    records_response1 = call_get_method_without_token(BASEURL, endpoint1)
    print('records_response.status_code', records_response1.status_code)
    permissions = []
    permissions = records_response1.json()
    print("Raw API Response:", permissions)
    permissions_data = permissions['functions']
 
    print("Formatted Permissions:", permissions_data)  # Debugging

    role = call_get_method(BASEURL, f'UserManagement/role/{pk}/',user_token)
    
    if role.status_code in [200,201]:
        role_data = role.json()
    else:
        print('error------',role)
        messages.error(request, 'Failed to retrieve data for role. Please check your connection and try again.', extra_tags='warning')
        return redirect('role')

    if request.method=="POST":
        form=RoleForm(request.POST, initial=role_data,permissions_choices=permissions_data)
        if form.is_valid():
            updated_data = form.cleaned_data
            for field_name, field in form.fields.items():
                if isinstance(field.widget, forms.DateInput) or isinstance(field, forms.DateField) or isinstance(field, forms.DateTimeField):
                    if updated_data[field_name]:
                        del updated_data[field_name]
                        updated_data[field_name] = request.POST.get(field_name)
            # Serialize the updated data as JSON
            json_data = json.dumps(updated_data)
            response = call_put_method_without_token(BASEURL, f'UserManagement/role/{pk}/', json_data)

            if response.status_code in [200,201]: 
                messages.success(request, 'Your data has been successfully saved', extra_tags='success')
                return redirect('role') 
            else:
                error_message = response.json()
                messages.error(request, f"Oops..! {error_message}", extra_tags='warning')
        else:
            print("An error occurred: Expecting value: line 1 column 1 (char 0)")
    else:
        form = RoleForm(initial=role_data,permissions_choices=permissions_data)

    context={
        'form':form,
    }
    return render(request,'role_edit.html',context)

def role_delete(request,pk):
    end_point = f'UserManagement/role/{pk}/'
    role = call_delete_method_without_token(BASEURL, end_point)
    print(role.status_code)
    if role.status_code not in [200,201]:
        messages.error(request, 'Failed to delete data for role. Please try again.', extra_tags='warning')
        return redirect('role')
    else:
        messages.success(request, 'Successfully deleted data for role', extra_tags='success')
        return redirect('role')

# create and view table function
def subcounty(request):
    user_token=request.session['user_token']

    endpoint2='UserManagement/county/'    
    records_response2 = call_get_method(BASEURL,endpoint2,user_token)
    print('records_response.status_code',records_response2.status_code)
    if records_response2.status_code not in [200,201]:
        messages.error(request, f"Failed to fetch records. {records_response2.json()}", extra_tags="warning")
    else:
        roles = records_response2.json()
    print('----',roles)
    form=SubCountyForm(roles_choices=roles)
    endpoint = 'UserManagement/subcounty/'
    if request.method=="POST":
        form=SubCountyForm(request.POST,roles_choices=roles)
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
                return redirect('subcounty_list')
    else:
        print('errorss',form.errors)
    # try:
    #     # getting data from backend
    #     records_response = call_get_method_without_token(BASEURL,endpoint)
    #     if records_response.status_code not in [200,201]:
    #         messages.error(request, f"Failed to fetch records. {records_response.json()}", extra_tags="warning")
    #     else:
    #         records = records_response.json()
    #         # You can pass 'records' to your template for rendering
    #         context = {'form': form, 'records': records}
    #         return render(request, 'subcounty.html', context)
    # except Exception as e:
    #     print("An error occurred: Expecting value: line 1 column 1 (char 0)")
    context={
        'form':form,
    }
    return render(request,'subcounty.html',context)

def subcounty_list(request):
    user_token=request.session['user_token']

    endpoint = 'UserManagement/subcounty/'
    records_response = call_get_method(BASEURL, endpoint,user_token)
    if records_response.status_code not in [200, 201]:
        messages.error(request, f"Failed to fetch records. {records_response.json()}", extra_tags="warning")
        records = []
    else:
        records = records_response.json()
    context = {
        'records': records,
    }
    return render(request, 'subcounty_list.html', context)
# edit function
def subcounty_edit(request,pk):
    user_token=request.session['user_token']

    endpoint2='UserManagement/county/'    
    records_response2 = call_get_method(BASEURL,endpoint2,user_token)
    print('records_response.status_code',records_response2.status_code)
    if records_response2.status_code not in [200,201]:
        messages.error(request, f"Failed to fetch records. {records_response2.json()}", extra_tags="warning")
    else:
        roles = records_response2.json()
    subcounty = call_get_method_without_token(BASEURL, f'UserManagement/subcounty/{pk}/')
    
    if subcounty.status_code in [200,201]:
        subcounty_data = subcounty.json()
    else:
        print('error------',subcounty)
        messages.error(request, 'Failed to retrieve data for subcounty. Please check your connection and try again.', extra_tags='warning')
        return redirect('subcounty')

    if request.method=="POST":
        form=SubCountyForm(request.POST, initial=subcounty_data,roles_choices=roles)
        if form.is_valid():
            updated_data = form.cleaned_data
            updated_data['updated_by']=request.session['user_data']['id']

            for field_name, field in form.fields.items():
                if isinstance(field.widget, forms.DateInput) or isinstance(field, forms.DateField) or isinstance(field, forms.DateTimeField):
                    if updated_data[field_name]:
                        del updated_data[field_name]
                        updated_data[field_name] = request.POST.get(field_name)
            # Serialize the updated data as JSON
            json_data = json.dumps(updated_data)
            response = call_put_method_without_token(BASEURL, f'UserManagement/subcounty/{pk}/', json_data)

            if response.status_code in [200,201]: 
                messages.success(request, 'Your data has been successfully saved', extra_tags='success')
                return redirect('subcounty') 
            else:
                error_message = response.json()
                messages.error(request, f"Oops..! {error_message}", extra_tags='warning')
        else:
            print("An error occurred: Expecting value: line 1 column 1 (char 0)")
    else:
        form = SubCountyForm(initial=subcounty_data,roles_choices=roles)

    context={
        'form':form,
    }
    return render(request,'subcounty_edit.html',context)

def subcounty_delete(request,pk):
    end_point = f'subcounty/{pk}/'
    subcounty = call_delete_method_without_token(BASEURL, end_point)
    if subcounty.status_code not in [200,201]:
        messages.error(request, 'Failed to delete data for subcounty. Please try again.', extra_tags='warning')
        return redirect('subcounty')
    else:
        messages.success(request, 'Successfully deleted data for subcounty', extra_tags='success')
        return redirect('subcounty')
    
def ward(request):
    user_token=request.session['user_token']

    endpoint2='UserManagement/subcounty/'    
    records_response2 = call_get_method(BASEURL,endpoint2,user_token)
    print('records_response.status_code',records_response2.status_code)
    if records_response2.status_code not in [200,201]:
        messages.error(request, f"Failed to fetch records. {records_response2.json()}", extra_tags="warning")
    else:
        roles = records_response2.json()
    form=WardForm(roles_choices=roles)
    endpoint = 'UserManagement/ward/'
    if request.method=="POST":
        form=WardForm(request.POST,roles_choices=roles)
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
                return redirect('ward_list')
    else:
        print('errorss',form.errors)
    # try:
    #     # getting data from backend
    #     records_response = call_get_method_without_token(BASEURL,endpoint)
    #     if records_response.status_code not in [200,201]:
    #         messages.error(request, f"Failed to fetch records. {records_response.json()}", extra_tags="warning")
    #     else:
    #         records = records_response.json()
    #         # You can pass 'records' to your template for rendering
    #         context = {'form': form, 'records': records}
    #         return render(request, 'ward.html', context)
    # except Exception as e:
    #     print("An error occurred: Expecting value: line 1 column 1 (char 0)")
    context={
        'form':form,
    }
    return render(request,'ward.html',context)

def ward_list(request):
    user_token=request.session['user_token']

    endpoint = 'UserManagement/ward/'
    records_response = call_get_method(BASEURL, endpoint,user_token)
    if records_response.status_code not in [200, 201]:
        messages.error(request, f"Failed to fetch records. {records_response.json()}", extra_tags="warning")
        records = []
    else:
        records = records_response.json()
    context = {
        'records': records,
    }
    return render(request, 'ward_list.html', context)
# edit function
def ward_edit(request,pk):
    user_token=request.session['user_token']

    endpoint2='UserManagement/subcounty/'    
    records_response2 = call_get_method(BASEURL,endpoint2,user_token)
    print('records_response.status_code',records_response2.status_code)
    if records_response2.status_code not in [200,201]:
        messages.error(request, f"Failed to fetch records. {records_response2.json()}", extra_tags="warning")
    else:
        roles = records_response2.json()

    ward = call_get_method(BASEURL, f'UserManagement/ward/{pk}/',user_token)
    
    if ward.status_code in [200,201]:
        ward_data = ward.json()
    else:
        print('error------',ward)
        messages.error(request, 'Failed to retrieve data for ward. Please check your connection and try again.', extra_tags='warning')
        return redirect('ward')

    if request.method=="POST":
        form=WardForm(request.POST, initial=ward_data,roles_choices=roles)
        if form.is_valid():
            updated_data = form.cleaned_data
            updated_data['created_by']=request.session['user_data']['id']

            for field_name, field in form.fields.items():
                if isinstance(field.widget, forms.DateInput) or isinstance(field, forms.DateField) or isinstance(field, forms.DateTimeField):
                    if updated_data[field_name]:
                        del updated_data[field_name]
                        updated_data[field_name] = request.POST.get(field_name)
            # Serialize the updated data as JSON
            json_data = json.dumps(updated_data)
            response = call_put_method_without_token(BASEURL, f'UserManagement/ward/{pk}/', json_data)

            if response.status_code in [200,201]: 
                messages.success(request, 'Your data has been successfully saved', extra_tags='success')
                return redirect('ward') 
            else:
                error_message = response.json()
                messages.error(request, f"Oops..! {error_message}", extra_tags='warning')
        else:
            print("An error occurred: Expecting value: line 1 column 1 (char 0)")
    else:
        form = WardForm(initial=ward_data,roles_choices=roles)

    context={
        'form':form,
    }
    return render(request,'ward_edit.html',context)

def ward_delete(request,pk):
    end_point = f'UserManagement/ward/{pk}/'
    ward = call_delete_method_without_token(BASEURL, end_point)
    if ward.status_code not in [200,201]:
        messages.error(request, 'Failed to delete data for ward. Please try again.', extra_tags='warning')
        return redirect('ward')
    else:
        messages.success(request, 'Successfully deleted data for ward', extra_tags='success')
        return redirect('ward')


# create and view table function
def function(request):
    form=FunctionForm()
    endpoint = 'UserManagement/function/'
    if request.method=="POST":
        form=FunctionForm(request.POST)
        if form.is_valid():
            Output = form.cleaned_data
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
                return redirect('function_list')
    else:
        print('errorss',form.errors)
    # try:
    #     # getting data from backend
    #     records_response = call_get_method_without_token(BASEURL,endpoint)
    #     if records_response.status_code not in [200,201]:
    #         messages.error(request, f"Failed to fetch records. {records_response.json()}", extra_tags="warning")
    #     else:
    #         records = records_response.json()
    #         # You can pass 'records' to your template for rendering
    #         context = {'form': form, 'records': records}
    #         return render(request, 'function.html', context)
    # except Exception as e:
    #     print("An error occurred: Expecting value: line 1 column 1 (char 0)")
    context={
        'form':form,
    }
    return render(request,'function.html',context)

def function_list(request):
    endpoint = 'UserManagement/function/'
    records_response = call_get_method_without_token(BASEURL, endpoint)
    if records_response.status_code not in [200, 201]:
        messages.error(request, f"Failed to fetch records. {records_response.json()}", extra_tags="warning")
        records = []
    else:
        records = records_response.json()
    context = {
        'records': records,
    }
    return render(request, 'function_list.html', context)

# edit function
def function_edit(request,pk):
    function = call_get_method_without_token(BASEURL, f'UserManagement/function/{pk}/')
    
    if function.status_code in [200,201]:
        function_data = function.json()
    else:
        print('error------',function)
        messages.error(request, 'Failed to retrieve data for function. Please check your connection and try again.', extra_tags='warning')
        return redirect('function')

    if request.method=="POST":
        form=FunctionForm(request.POST, initial=function_data)
        if form.is_valid():
            updated_data = form.cleaned_data
            for field_name, field in form.fields.items():
                if isinstance(field.widget, forms.DateInput) or isinstance(field, forms.DateField) or isinstance(field, forms.DateTimeField):
                    if updated_data[field_name]:
                        del updated_data[field_name]
                        updated_data[field_name] = request.POST.get(field_name)
            # Serialize the updated data as JSON
            json_data = json.dumps(updated_data)
            response = call_put_method_without_token(BASEURL, f'function/{pk}/', json_data)

            if response.status_code in [200,201]: 
                messages.success(request, 'Your data has been successfully saved', extra_tags='success')
                return redirect('function') 
            else:
                error_message = response.json()
                messages.error(request, f"Oops..! {error_message}", extra_tags='warning')
        else:
            print("An error occurred: Expecting value: line 1 column 1 (char 0)")
    else:
        form = FunctionForm(initial=function_data)

    context={
        'form':form,
    }
    return render(request,'function_edit.html',context)

def function_delete(request,pk):
    end_point = f'UserManagement/function/{pk}/'
    function = call_delete_method_without_token(BASEURL, end_point)
    if function.status_code not in [200,201]:
        messages.error(request, 'Failed to delete data for function. Please try again.', extra_tags='warning')
        return redirect('function')
    else:
        messages.success(request, 'Successfully deleted data for function', extra_tags='success')
        return redirect('function')

# create and view table function
def county(request):
    form=CountyForm()
    endpoint = 'UserManagement/county/'
    if request.method=="POST":
        form=CountyForm(request.POST)
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
                return redirect('county_list')
    else:
        print('errorss',form.errors)
    # try:
    #     # getting data from backend
    #     records_response = call_get_method_without_token(BASEURL,endpoint)
    #     if records_response.status_code not in [200,201]:
    #         messages.error(request, f"Failed to fetch records. {records_response.json()}", extra_tags="warning")
    #     else:
    #         records = records_response.json()
    #         # You can pass 'records' to your template for rendering
    #         context = {'form': form, 'records': records}
    #         return render(request, 'county.html', context)
    # except Exception as e:
    #     print("An error occurred: Expecting value: line 1 column 1 (char 0)")
    context={
        'form':form,
    }
    return render(request,'county.html',context)

def county_list(request):
    user_token=request.session['user_token']
    endpoint = 'UserManagement/county/'
    records_response = call_get_method(BASEURL, endpoint,user_token)
    if records_response.status_code not in [200, 201]:
        messages.error(request, f"Failed to fetch records. {records_response.json()}", extra_tags="warning")
        records = []
    else:
        records = records_response.json()
    context = {
        'records': records,
    }
    return render(request, 'county_list.html', context)

# edit function
def county_edit(request,pk):
    user_token=request.session['user_token']

    county = call_get_method(BASEURL, f'UserManagement/county/{pk}/',user_token)
    
    if county.status_code in [200,201]:
        county_data = county.json()
    else:
        print('error------',county)
        messages.error(request, 'Failed to retrieve data for county. Please check your connection and try again.', extra_tags='warning')
        return redirect('county')

    if request.method=="POST":
        form=CountyForm(request.POST, initial=county_data)
        if form.is_valid():
            updated_data = form.cleaned_data
            updated_data['created_by']=request.session['user_data']['id']

            for field_name, field in form.fields.items():
                if isinstance(field.widget, forms.DateInput) or isinstance(field, forms.DateField) or isinstance(field, forms.DateTimeField):
                    if updated_data[field_name]:
                        del updated_data[field_name]
                        updated_data[field_name] = request.POST.get(field_name)
            # Serialize the updated data as JSON
            json_data = json.dumps(updated_data)
            response = call_put_method_without_token(BASEURL, f'UserManagement/county/{pk}/', json_data)

            if response.status_code in [200,201]: 
                messages.success(request, 'Your data has been successfully saved', extra_tags='success')
                return redirect('county') 
            else:
                error_message = response.json()
                messages.error(request, f"Oops..! {error_message}", extra_tags='warning')
        else:
            print("An error occurred: Expecting value: line 1 column 1 (char 0)")
    else:
        form = CountyForm(initial=county_data)

    context={
        'form':form,
    }
    return render(request,'county_edit.html',context)

def county_delete(request,pk):
    end_point = f'UserManagement/county/{pk}/'
    county = call_delete_method_without_token(BASEURL, end_point)
    if county.status_code not in [200,201]:
        messages.error(request, 'Failed to delete data for county. Please try again.', extra_tags='warning')
        return redirect('county')
    else:
        messages.success(request, 'Successfully deleted data for county', extra_tags='success')
        return redirect('county')


def user(request):
    user_token=request.session['user_token']

    form=UserForm()
    endpoint = 'UserManagement/user/'
    endpoint2='UserManagement/role/'    
    records_response2 = call_get_method(BASEURL,endpoint2,user_token)
    print('records_response.status_code',records_response2.status_code)
    if records_response2.status_code not in [200,201]:
        messages.error(request, f"Failed to fetch records. {records_response2.json()}", extra_tags="warning")
    else:
        roles = records_response2.json()
        # print('===',records)
    if request.method=="POST":
        form=UserForm(request.POST,roles_choices=roles)
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
                return redirect('user_list')
    else:
        form=UserForm(roles_choices=roles)

        print('errorss',form.errors)
    # try:
    #     # getting data from backend
    #     records_response = call_get_method(BASEURL,endpoint,user_token)
    #     if records_response.status_code not in [200,201]:
    #         messages.error(request, f"Failed to fetch records. {records_response.json()}", extra_tags="warning")
    #     else:
    #         records = records_response.json()
    #         # You can pass 'records' to your template for rendering
    #         context = {'form': form, 'records': records}
    #         return render(request, 'user.html', context)
    # except Exception as e:
    #     print("An error occurred: Expecting value: line 1 column 1 (char 0)")
    context={
        'form':form,
    }
    return render(request,'user.html',context)

def user_list(request):
    user_token=request.session['user_token']
    endpoint = 'UserManagement/user/'
    records_response = call_get_method(BASEURL, endpoint, user_token)
    if records_response.status_code not in [200, 201]:
        messages.error(request, f"Failed to fetch records. {records_response.json()}", extra_tags="warning")
        records = []
    else:
        records = records_response.json()
    context = {
        'records': records,
    }
    return render(request, 'user_list.html', context)

# edit function
def user_edit(request, pk):
    user_token = request.session['user_token']

    # Get user data
    user = call_get_method(BASEURL, f'UserManagement/user/{pk}/', user_token)
    if user.status_code in [200, 201]:
        user_data = user.json()
        print('data', user_data)

        # Extract role ID from nested dictionary
        if 'roles' in user_data and isinstance(user_data['roles'], dict):
            user_data['roles'] = user_data['roles'].get('id')  # Set to role ID (e.g. '2')
    else:
        print('error------', user)
        messages.error(request, 'Failed to retrieve data for user. Please check your connection and try again.', extra_tags='warning')
        return redirect('user_list')

    # Get roles list for dropdown
    endpoint2 = 'UserManagement/role/'
    records_response2 = call_get_method(BASEURL, endpoint2, user_token)
    print('records_response.status_code', records_response2.status_code)
    if records_response2.status_code not in [200, 201]:
        messages.error(request, f"Failed to fetch records. {records_response2.json()}", extra_tags="warning")
        roles = []
    else:
        roles = records_response2.json()

    if request.method == "POST":
        form = UserForm(request.POST, initial=user_data, roles_choices=roles)
        if form.is_valid():
            updated_data = form.cleaned_data

            # Handle DateField or DateTimeField manually
            for field_name, field in form.fields.items():
                if isinstance(field.widget, forms.DateInput) or isinstance(field, forms.DateField) or isinstance(field, forms.DateTimeField):
                    if updated_data.get(field_name):
                        updated_data[field_name] = request.POST.get(field_name)

            # Serialize and send the data to API
            json_data = json.dumps(updated_data)
            response = call_put_method_without_token(BASEURL, f'UserManagement/user/{pk}/', json_data)

            if response.status_code in [200, 201]:
                messages.success(request, 'Your data has been successfully saved', extra_tags='success')
                return redirect('user_list')
            else:
                try:
                    error_message = response.json()
                except Exception as e:
                    error_message = str(e)
                messages.error(request, f"Oops..! {error_message}", extra_tags='warning')
        else:
            print("An error occurred: Expecting value: line 1 column 1 (char 0)")
    else:
        form = UserForm(initial=user_data, roles_choices=roles)

    context = {
        'form': form,
    }
    return render(request, 'user_edit.html', context)

def user_delete(request,pk):
    end_point = f'UserManagement/user/{pk}/'
    user = call_delete_method_without_token(BASEURL, end_point)
    print(user.status_code)
    if user.status_code not in [200,201]:
        messages.error(request, 'Failed to delete data for user. Please try again.', extra_tags='warning')
        return redirect('user_list')
    else:
        messages.success(request, 'Successfully deleted data for user', extra_tags='success')
        return redirect('user_list')




def company(request):
    endpoint = 'UserManagement/company/'
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
    form=CompanyForm()
    if request.method=="POST":
        form=CompanyForm(request.POST)
        if form.is_valid():
            Output = form.cleaned_data
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
                return redirect('company')
    else:
        form=CompanyForm()

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
            return render(request, 'company.html', context)
    except Exception as e:
        print("An error occurred: Expecting value: line 1 column 1 (char 0)")
    context={
        'form':form,
    }
    return render(request,'company.html',context)


def company_create(request):
    endpoint = 'UserManagement/company/'
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
    form=CompanyForm()
    if request.method=="POST":
        form=CompanyForm(request.POST)
        if form.is_valid():
            Output = form.cleaned_data
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
                return redirect('select_company')
    else:
        form=CompanyForm()

        print('errorss',form.errors)
   
    context={
        'form':form,
    }
    return render(request,'create_company.html',context)

# edit function
def company_edit(request,pk):
    endpoint = 'UserManagement/company/'
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
    user = call_get_method_without_token(BASEURL, f'UserManagement/company/{pk}/')
    
    if user.status_code in [200,201]:
        user_data = user.json()
    else:
        print('error------',user)
        messages.error(request, 'Failed to retrieve data for user. Please check your connection and try again.', extra_tags='warning')
        return redirect('company')
   
    # endpoint2='UserManagement/role/'    
    # records_response2 = call_get_method_without_token(BASEURL,endpoint2)
    # print('records_response.status_code',records_response2.status_code)
    # if records_response2.status_code not in [200,201]:
    #     messages.error(request, f"Failed to fetch records. {records_response2.json()}", extra_tags="warning")
    # else:
    #     roles = records_response2.json()

    if request.method=="POST":
        form=CompanyForm(request.POST, initial=user_data)
        if form.is_valid():
            updated_data = form.cleaned_data
            for field_name, field in form.fields.items():
                if isinstance(field.widget, forms.DateInput) or isinstance(field, forms.DateField) or isinstance(field, forms.DateTimeField):
                    if updated_data[field_name]:
                        del updated_data[field_name]
                        updated_data[field_name] = request.POST.get(field_name)
            # Serialize the updated data as JSON
            json_data = json.dumps(updated_data)
            response = call_put_method_without_token(BASEURL, f'UserManagement/company/{pk}/', json_data)

            if response.status_code in [200,201]: 
                messages.success(request, 'Your data has been successfully saved', extra_tags='success')
                return redirect('company') 
            else:
                error_message = response.json()
                messages.error(request, f"Oops..! {error_message}", extra_tags='warning')
        else:
            print("An error occurred: Expecting value: line 1 column 1 (char 0)")
    else:
        form = CompanyForm(initial=user_data)

    context={
        'form':form,
    }
    return render(request,'company_edit.html',context)

def company_delete(request,pk):
    end_point = f'UserManagement/company/{pk}/'
    user = call_delete_method_without_token(BASEURL, end_point)
    print(user.status_code)
    if user.status_code not in [200,201]:
        messages.error(request, 'Failed to delete data for company. Please try again.', extra_tags='warning')
        return redirect('company')
    else:
        messages.success(request, 'Successfully deleted data for company', extra_tags='success')
        return redirect('company')


def branch(request):
    endpoint = 'UserManagement/branch/'
    endpoint2='UserManagement/company/'    
    records_response2 = call_get_method_without_token(BASEURL,endpoint2)
    print('records_response.status_code',records_response2.status_code)
    if records_response2.status_code not in [200,201]:
        messages.error(request, f"Failed to fetch records. {records_response2.json()}", extra_tags="warning")
    else:
        roles = records_response2.json()
        # print('===',records)
    # endpoint1='UserManagement/county/'    
    # records_response2 = call_get_method_without_token(BASEURL,endpoint1)
    # print('records_response.status_code',records_response2.status_code)
    # if records_response2.status_code not in [200,201]:
    #     messages.error(request, f"Failed to fetch records. {records_response2.json()}", extra_tags="warning")
    # else:
    #     country = records_response2.json()
    #     print('----',roles)
    # endpoint2='UserManagement/subcounty/'    
    # records_response2 = call_get_method_without_token(BASEURL,endpoint2)
    # print('records_response.status_code',records_response2.status_code)
    # if records_response2.status_code not in [200,201]:
    #     messages.error(request, f"Failed to fetch records. {records_response2.json()}", extra_tags="warning")
    # else:
    #     sub = records_response2.json()
    if request.method=="POST":
        form=BranchForm(request.POST)
        if form.is_valid():
            Output = form.cleaned_data
            Output['company']=request.session['company']
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
                return redirect('select_branch')
    else:
        form=BranchForm()

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
            return render(request, 'branch.html', context)
    except Exception as e:
        print("An error occurred: Expecting value: line 1 column 1 (char 0)")
    context={
        'form':form,
    }
    return render(request,'branch.html',context)


def branch_create(request):
    endpoint = 'UserManagement/branch/'
    # pk=request.session['branch']
    # endpoint3=f'UserManagement/get_company/{pk}'    
    # records_response2 = call_get_method_without_token(BASEURL,endpoint3)
    # print('records_response.status_code',records_response2.status_code)
    # if records_response2.status_code not in [200,201]:
    #     messages.error(request, f"Failed to fetch records. {records_response2.json()}", extra_tags="warning")
    # else:
    #     branch = records_response2.json()
    #     print('===',branch)
    pk=request.session['company']
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
    if request.method=="POST":
        form=BranchForm(request.POST)
        if form.is_valid():
            Output = form.cleaned_data
            Output['company']=request.session['company']
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
                return redirect('select_branch' , pk=pk)
    else:
        company=request.session['company']
        form=BranchForm()
    endpoint2=f'UserManagement/branch/{pk}'    
    records_response2 = call_get_method_without_token(BASEURL,endpoint2)
    print('records_response.status_code',records_response2.status_code)
    if records_response2.status_code not in [200,201]:
        messages.error(request, f"Failed to fetch records. {records_response2.json()}", extra_tags="warning")
    else:
        roles = records_response2.json()
        print('===',roles)

        print('errorss',form.errors)
    
    context={
        'form':form,
    }
    return render(request,'branch_create.html',context)

# edit function
def branch_edit(request,pk):
    endpoint = 'UserManagement/branch/'
    endpoint2='UserManagement/company/'    
    records_response2 = call_get_method_without_token(BASEURL,endpoint2)
    print('records_response.status_code',records_response2.status_code)
    if records_response2.status_code not in [200,201]:
        messages.error(request, f"Failed to fetch records. {records_response2.json()}", extra_tags="warning")
    else:
        company_choices = records_response2.json()
        # print('===',records)
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
    user = call_get_method_without_token(BASEURL, f'UserManagement/branch/{pk}/')
    
    if user.status_code in [200,201]:
        user_data = user.json()
    else:
        print('error------',user)
        messages.error(request, 'Failed to retrieve data for user. Please check your connection and try again.', extra_tags='warning')
        return redirect('branch')
   
    # endpoint2='UserManagement/role/'    
    # records_response2 = call_get_method_without_token(BASEURL,endpoint2)
    # print('records_response.status_code',records_response2.status_code)
    # if records_response2.status_code not in [200,201]:
    #     messages.error(request, f"Failed to fetch records. {records_response2.json()}", extra_tags="warning")
    # else:
    #     roles = records_response2.json()

    if request.method=="POST":
        form=BranchForm(request.POST, initial=user_data)
        if form.is_valid():
            updated_data = form.cleaned_data
            for field_name, field in form.fields.items():
                if isinstance(field.widget, forms.DateInput) or isinstance(field, forms.DateField) or isinstance(field, forms.DateTimeField):
                    if updated_data[field_name]:
                        del updated_data[field_name]
                        updated_data[field_name] = request.POST.get(field_name)
            # Serialize the updated data as JSON
            json_data = json.dumps(updated_data)
            response = call_put_method_without_token(BASEURL, f'UserManagement/branch/{pk}/', json_data)

            if response.status_code in [200,201]: 
                messages.success(request, 'Your data has been successfully saved', extra_tags='success')
                return redirect('branch') 
            else:
                error_message = response.json()
                messages.error(request, f"Oops..! {error_message}", extra_tags='warning')
        else:
            print("An error occurred: Expecting value: line 1 column 1 (char 0)")
    else:
        form = BranchForm(initial=user_data)

    context={
        'form':form,
    }
    return render(request,'branch_edit.html',context)

def branch_delete(request,pk):
    end_point = f'UserManagement/branch/{pk}/'
    user = call_delete_method_without_token(BASEURL, end_point)
    print(user.status_code)
    if user.status_code not in [200,201]:
        messages.error(request, 'Failed to delete data for branch. Please try again.', extra_tags='warning')
        return redirect('branch')
    else:
        messages.success(request, 'Successfully deleted data for branch', extra_tags='success')
        return redirect('branch')



def permissions(request):
    token = request.session['user_token']
    endpoint1 = 'UserManagement/api_functions_setup/'
    records_response1 = call_get_method(BASEURL, endpoint1,token)
    
    print('records_response.status_code', records_response1.status_code)
    permissions = records_response1.json()
    print("Raw API Response:", permissions)

    permissions_data = permissions.get('functions', [])
    print("Formatted Permissions:", permissions_data)

    context = {
        "permissions": "active",
        "permissions_data": permissions_data
    }
    return render(request, 'permissions.html', context)


def permissions_add(request, pk):
    token = request.session['user_token']
    endpoint1 = 'UserManagement/api_functions_setup/'
    functions_response = call_get_method(BASEURL, endpoint1,token)

    print('functions_response.status_code', functions_response.status_code)
    functions_data = functions_response.json()
    print("Raw API Response:", functions_data)

    permissions_data = functions_data.get('functions', [])
    print("Formatted Permissions:", permissions_data)

    role_endpoint = f'UserManagement/role_permission/{pk}/'
    role_response = call_get_method(BASEURL, role_endpoint,token)

    print('role_response.status_code', role_response.status_code)
    role_permissions = role_response.json()
    print("Role Response:", role_permissions)

    assigned_permission_ids = [
        str(permission['id']) for permission in role_permissions.get('data', [])
    ]

    if request.method == 'POST':
        selected_permission_ids = request.POST.getlist('permission_ids')
        print(f"Selected Permissions for Role {pk}: ", selected_permission_ids)

        json_data = json.dumps({"functions": selected_permission_ids})
        update_response = call_put_method(BASEURL, f'UserManagement/role/{pk}/', json_data,token)

        if update_response.status_code in [200, 201]:
            messages.success(request, 'Your data has been successfully saved', extra_tags='success')
            return redirect('roles_page')
        else:
            try:
                error_message = update_response.json()
            except Exception as e:
                error_message = str(e)
            messages.error(request, f"Oops..! {error_message}", extra_tags='warning')

    context = {
        "permissions": "active",
        "permissions_data": permissions_data,
        "assigned_permission_ids": assigned_permission_ids
    }
    return render(request, 'permissions_list.html', context)





def roles_page(request):
    try:
        token = request.session['user_token']
        endpoint = 'UserManagement/role/'
    
        records_response = call_get_method(BASEURL, endpoint,token)

        if records_response.status_code not in [200, 201]:
            messages.error(request, f"Failed to fetch records. {records_response.json()}", extra_tags="warning")
        else:
            records = records_response.json()
            print("records++++",records)
        context={
            "roles_page":"active",
            'roles':records
             }
        return render(request, 'roles_page.html', context)
    except Exception as error:
        return render(request, "error.html", {"error": error})

def roles_add(request):
    token = request.session['user_token']
    endpoint = 'UserManagement/role/'
    endpoint1 = 'UserManagement/api_functions_setup/'
    records_response1 = call_get_method(BASEURL, endpoint1,token)
    print('records_response.status_code', records_response1.status_code)
    permissions = []
    permissions = records_response1.json()
    print("Raw API Response:", permissions)
    permissions_data = permissions['functions']
 
    print("Formatted Permissions:", permissions_data)  # Debugging

    if request.method == "POST":
        form = RolesForm(request.POST)
        if form.is_valid():
            Output = form.cleaned_data
            print('Output', Output)
            # Handle date fields if needed
            for field_name, field in form.fields.items():
                if isinstance(field.widget, forms.DateInput) or isinstance(field, forms.DateField) or isinstance(field, forms.DateTimeField):
                    if Output.get(field_name):
                        Output[field_name] = request.POST.get(field_name)
            
            json_data = json.dumps(Output)
            response = call_post_with_method(BASEURL, endpoint, json_data,token)
            
            if response.status_code not in [200, 201]:
                print("error", response)
            else:
                messages.success(request, 'Data Successfully Saved', extra_tags="success")
                return redirect('roles_page')
    else:
        form = RolesForm()

    try:
        records_response = call_get_method(BASEURL, endpoint,token)
        if records_response.status_code not in [200, 201]:
            messages.error(request, f"Failed to fetch records. {records_response.json()}", extra_tags="warning")
            records = []
        else:
            records = records_response.json()
    except Exception as e:
        print("An error occurred:", str(e))
        records = []

    context = {
        'form': form,
        'records': records,
    }
    return render(request, 'roles.html', context)


def roles_edit(request,pk):
    token = request.session['user_token']
    endpoint1 = 'UserManagement/api_functions_setup/'
    records_response1 = call_get_method(BASEURL, endpoint1,token)
    print('records_response.status_code', records_response1.status_code)
    permissions = []
    permissions = records_response1.json()
    print("Raw API Response:", permissions)
    permissions_data = permissions['functions']
 
    print("Formatted Permissions:", permissions_data)  # Debugging

    role = call_get_method(BASEURL, f'UserManagement/role/{pk}/',token)
    
    if role.status_code in [200,201]:
        role_data = role.json()
    else:
        print('error------',role)
        messages.error(request, 'Failed to retrieve data for role. Please check your connection and try again.', extra_tags='warning')
        return redirect('roles_page')

    if request.method=="POST":
        form=RolesForm(request.POST, initial=role_data)
        if form.is_valid():
            updated_data = form.cleaned_data
            for field_name, field in form.fields.items():
                if isinstance(field.widget, forms.DateInput) or isinstance(field, forms.DateField) or isinstance(field, forms.DateTimeField):
                    if updated_data[field_name]:
                        del updated_data[field_name]
                        updated_data[field_name] = request.POST.get(field_name)
            # Serialize the updated data as JSON
            json_data = json.dumps(updated_data)
            response = call_put_method(BASEURL, f'UserManagement/role/{pk}/', json_data,token)

            if response.status_code in [200,201]: 
                messages.success(request, 'Your data has been successfully saved', extra_tags='success')
                return redirect('roles_page') 
            else:
                error_message = response.json()
                messages.error(request, f"Oops..! {error_message}", extra_tags='warning')
        else:
            print("An error occurred: Expecting value: line 1 column 1 (char 0)")
    else:
        form = RolesForm(initial=role_data)

    context={
        'form':form,
    }
    return render(request, 'roles.html', context)


def roles_delete(request,pk):
    token = request.session['user_token']
    end_point = f'UserManagement/role/{pk}/'
    jobpost = call_delete_method(BASEURL, end_point,token)
    if jobpost.status_code not in [200,201]:
        messages.error(request, 'Failed to delete data for jobpost. Please try again.', extra_tags='warning')
        return redirect('roles_page')
    else:
        messages.success(request, 'Successfully deleted data for jobpost', extra_tags='success')
        return redirect('roles_page')
    