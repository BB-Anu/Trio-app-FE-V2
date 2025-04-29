import json
from pyexpat.errors import messages
from django.shortcuts import render

# Create your views here.

from django.shortcuts import render, redirect, get_object_or_404

from mainapp.api_call import *
from .forms import *
import re
from django.views.generic import DetailView
from django.utils.html import escape
from django.conf import settings

BASEURL = 'http://127.0.0.1:9000/'

def create_template_view(request):
    form=TemplateForm()
    endpoint = 'template/'
    if request.method=="POST":
        form=TemplateForm(request.POST)
        if form.is_valid():
            Output = form.cleaned_data
            for field_name, field in form.fields.items():
                if isinstance(field.widget, forms.DateInput) or isinstance(field, forms.DateField) or isinstance(field, forms.DateTimeField):
                    if Output[field_name]:
                        del Output[field_name]
                        Output[field_name] = request.POST.get(field_name)
            json_data=json.dumps(Output)
            response = call_post_method_for_without_token(BASEURL,endpoint,json_data)
            print('------------',response.json())
            if response.status_code not in [200,201]:
                print("error",response)
            else:
                return redirect('template_list')
    else:
        print('errorss',form.errors)
    
    context={
        'form':form,
    }
    return render(request,'tasktemplate/create_template.html',context)

def template_list_view(request):
    endpoint = 'template/'
    records_response = call_get_method_without_token(BASEURL,endpoint)
    if records_response.status_code not in [200,201]:
        messages.error(request, f"Failed to fetch records. {records_response.json()}", extra_tags="warning")
    else:
        records = records_response.json()
        print('----',records)
        context = { 'records': records}
        return render(request, 'tasktemplate/template_list.html', context)

def fill_and_save_template_view(request, pk):
    endpoint = f'templates/{pk}/'
    records_response = call_get_method_without_token(BASEURL, endpoint)

    if records_response.status_code not in [200, 201]:
        print('--template--', records_response.status_code)
        messages.error(request, "Failed to fetch the template data.")
        return render(request, 'tasktemplate/error.html', {'error': 'Template not found or server error.'})

    template = records_response.json()
    print('--template--', template)

    content = template.get('content', '')
    placeholders = re.findall(r'\{\{(\s*\w+\s*)\}\}', content)
    placeholders = [p.strip() for p in placeholders]

    def fill_placeholders(raw_content, placeholders, post_data):
        def replacer(match):
            key = match.group(1).strip()
            values = post_data.getlist(key)
            return escape(values[0]) if values else ''
        return re.sub(r'\{\{(\s*\w+\s*)\}\}', replacer, raw_content)

    if request.method == 'POST':
        missing_fields = [p for p in placeholders if not request.POST.get(p)]
        if missing_fields:
            messages.error(request, f"Missing values for: {', '.join(missing_fields)}.")
            return render(request, 'tasktemplate/fill_template.html', {
                'template': template,
                'placeholders': placeholders,
                'post_data': request.POST,
            })

    filled_content = fill_placeholders(content, placeholders, request.POST)
    # endpoint = f'template_document/{pk}/{filled_content}'
    # print(endpoint)
    form = TemplateDocumentForm({'Template':pk,'content': template})
    if form.is_valid():
        json_data = json.dumps(form.cleaned_data)

        post_endpoint = f'template_document/'
        records_response2 = call_post_method_for_without_token(BASEURL, post_endpoint, data=json_data)

        print('records_response.status_code', records_response2.status_code)
        print('response data:', records_response2.json())
        data=records_response2.json()
        id =data['id']
        if records_response2.status_code not in [200, 201]:
            # messages.error(request, f"Failed to save the filled template. Server responded with {records_response2.status_code}"
            print('error')
        else:
            # messages.success(request, "Template filled and saved successfully.")
            return redirect('document_detail', pk=id)

    # Optional: Save to DB (Uncomment and adjust based on your model)
        # from .models import FilledTemplate
        # FilledTemplate.objects.create(name=template['name'], content=filled_content)

        # messages.success(request, "Template filled and saved successfully.")
        # return redirect('template_list')

    return render(request, 'tasktemplate/fill_template.html', {
        'template': template,
        'placeholders': placeholders,
    })



# def document_detail_view(request, pk):
#     endpoint = f'template_documents/{pk}/'
#     records_response = call_get_method_without_token(BASEURL, endpoint)

#     if records_response.status_code not in [200, 201]:
#         print('--template--', records_response.status_code)
#         messages.error(request, "Failed to fetch the template data.")
#         return render(request, 'tasktemplate/error.html', {'error': 'Template not found or server error.'})

#     template = records_response.json()
#     print('--template--', template)
#     inner_content = json.loads(template['content'].replace("'", '"'))

#     # Extract the value of 'content' which contains '{{name}}'
#     extracted_content = inner_content.get('content')

#     print(extracted_content)  # Output: {{name}}
#     context = {
#         'document': extracted_content,
#     }
#     return render(request, 'tasktemplate/document_detail.html', context)

# import re

# def document_detail_view(request, pk):
#     endpoint = f'template_documents/{pk}/'
#     records_response = call_get_method_without_token(BASEURL, endpoint)

#     if records_response.status_code not in [200, 201]:
#         print('--template--', records_response.status_code)
#         messages.error(request, "Failed to fetch the template data.")
#         return render(request, 'tasktemplate/error.html', {'error': 'Template not found or server error.'})

#     template = records_response.json()
#     print('--template--', template)
#     inner_content = json.loads(template['content'].replace("'", '"'))

#     # Extract the value of 'content' and look for placeholders like {{name}}
#     extracted_content = inner_content.get('content', '')

#     # Use regex to extract placeholders in the form of {{placeholder}}
#     placeholders = re.findall(r'{{(.*?)}}', extracted_content)
#     print("Extracted placeholders:", placeholders)

#     context = {
#         'document': extracted_content,
#         'placeholders': placeholders,  # Pass the placeholders to the template
#     }
#     return render(request, 'tasktemplate/document_detail.html', context)

# import re
# def document_detail_view(request, pk):
#     endpoint = f'template_documents/{pk}/'
#     records_response = call_get_method_without_token(BASEURL, endpoint)

#     if records_response.status_code not in [200, 201]:
#         print('--template--', records_response.status_code)
#         messages.error(request, "Failed to fetch the template data.")
#         return render(request, 'tasktemplate/error.html', {'error': 'Template not found or server error.'})

#     template = records_response.json()
#     print('--template--', template)
#     inner_content = json.loads(template['content'].replace("'", '"'))

#     # Extract the value of 'content' and look for placeholders like {{name}}
#     extracted_content = inner_content.get('content', '')

#     # Use regex to extract placeholders in the form of {{placeholder}}
#     placeholders = re.findall(r'{{(.*?)}}', extracted_content)
#     print("Extracted placeholders:", placeholders)

#     context = {
#         'document': extracted_content,
#         'placeholders': placeholders,  # Pass the placeholders to the template
#     }
#     return render(request, 'tasktemplate/document_detail.html', context)



# import re, json
# from django.contrib import messages
# from django.shortcuts import render, redirect

# def document_detail_view(request, pk):
#     branch=request.session['branch']
#     endpoint = f'template_documents/{pk}/'
#     records_response = call_get_method_without_token(BASEURL, endpoint)

#     if records_response.status_code not in [200, 201]:
#         messages.error(request, "Failed to fetch the template data.")
#         return render(request, 'tasktemplate/error.html', {'error': 'Template not found or server error.'})

#     template = records_response.json()
#     inner_content = json.loads(template['content'].replace("'", '"'))
#     extracted_content = inner_content.get('content', '')
#     updated_content = re.sub(r'{{(.*?)}}', r'{{\1}}<br>', extracted_content)

#     # Extract placeholders like {{name}}
#     placeholders = re.findall(r'{{(.*?)}}', updated_content)

#     if request.method == 'POST':
#         title = request.POST.get('title')
#         hours_allocated = request.POST.get('hours_allocated')
#         description = request.POST.get('description')  # Final HTML content
#         checklist = request.POST.get('checklist', '')
#         deliverables = request.POST.get('deliverables', '')
#         branch=branch
#         template=pk
#         print('---------',title,hours_allocated,description,checklist,deliverables)
#         # Extract placeholders from the request
#         placeholder_values = {}
#         for key in request.POST:
#             if key.startswith('hidden_'):
#                 field_name = key.replace('hidden_', '')
#                 placeholder_values[field_name] = request.POST.get(key)

#         # Optional: also handle JSON if 'placeholders' is passed as raw JSON string
#         raw_placeholders = request.POST.get('placeholders')
#         if raw_placeholders:
#             try:
#                 placeholder_values = json.loads(raw_placeholders)
#             except json.JSONDecodeError:
#                 pass  # fallback to previous hidden_ values

#         payload = {
#               'branch':branch,
#             'template':pk,
#             'placeholders': placeholder_values  # Only send placeholders
#         }
#         post_endpoint = 'tasktemplate/'
#         records_response2 = call_post_method_for_without_token(BASEURL, post_endpoint, data=json.dumps(payload))

#         print('records_response.status_code', records_response2.status_code)

#         if records_response2.status_code not in [200, 201]:
#             messages.error(request, f"Failed to save the filled template. Server responded with {records_response2.status_code}")
#             # return render(request, 'tasktemplate/error.html', {'error': 'Template save failed.'})
#             print('---- error  -----')

#         data = records_response2.json()
#         # template_id = data.get('id')
#         messages.success(request, "Template saved successfully.")
#         # return redirect('template_detail', pk=template_id)


#         messages.success(request, "Task template saved successfully.")
#         return redirect('template_list')  # or wherever you want to go

#     context = {
#         'document': extracted_content,
#         'placeholders': placeholders,
#     }
#     return render(request, 'tasktemplate/document_detail.html', context)

import re, json
from django.contrib import messages
from django.shortcuts import render, redirect

def document_detail_view(request, pk):
    branch = request.session['branch']
    endpoint = f'template_documents/{pk}/'
    records_response = call_get_method_without_token(BASEURL, endpoint)

    if records_response.status_code not in [200, 201]:
        messages.error(request, "Failed to fetch the template data.")
        return render(request, 'tasktemplate/error.html', {'error': 'Template not found or server error.'})

    # Fetch the template and content
    template = records_response.json()
    inner_content = json.loads(template['content'].replace("'", '"'))
    extracted_content = inner_content.get('content', '')

    # Add <br> tags after each placeholder
    updated_content = re.sub(r'{{(.*?)}}', r'{{\1}}<br>', extracted_content)

    # Extract placeholders like {{name}}
    placeholders = re.findall(r'{{(.*?)}}', updated_content)

    if request.method == 'POST':
        # Handle POST request
        title = request.POST.get('title')
        hours_allocated = request.POST.get('hours_allocated')
        description = request.POST.get('description')
        checklist = request.POST.get('checklist', '')
        deliverables = request.POST.get('deliverables', '')
        template = pk

        # Extract placeholder values from the form submission
        placeholder_values = {}
        for key in request.POST:
            if key.startswith('hidden_'):
                field_name = key.replace('hidden_', '')
                placeholder_values[field_name] = request.POST.get(key)

        # Handle the raw placeholder values if available
        raw_placeholders = request.POST.get('placeholders')
        if raw_placeholders:
            try:
                placeholder_values = json.loads(raw_placeholders)
            except json.JSONDecodeError:
                pass  # Fallback if the JSON decoding fails

        # Prepare the payload to save the filled template
        payload = {
            'branch': branch,
            'template': pk,
            'placeholders': placeholder_values  # Send only the placeholder values
        }

        post_endpoint = 'tasktemplate/'
        records_response2 = call_post_method_for_without_token(BASEURL, post_endpoint, data=json.dumps(payload))

        if records_response2.status_code not in [200, 201]:
            messages.error(request, f"Failed to save the filled template. Server responded with {records_response2.status_code}")
            print('---- error  -----')

        data = records_response2.json()
        messages.success(request, "Template saved successfully.")
        return redirect('template_list')  # Redirect after success

    context = {
        'document': updated_content,  # Pass updated content with <br> for line breaks
        'placeholders': placeholders,
    }

    return render(request, 'tasktemplate/document_detail.html', context)
