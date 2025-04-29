from os import access
import requests
# this is for post method without token
def call_post_method_for_without_token(BASE_URL,endpoint,data):
    api_url=BASE_URL+endpoint
    headers = {
        'Content-Type': 'application/json', 
    }
    response = requests.post(api_url,data=data,headers=headers)
    return response


# this is for post method with token
def call_post_with_method(BASE_URL,endpoint,data, access_token):
    api_url=BASE_URL+endpoint
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {access_token}'
    }
    response = requests.post(api_url,data=data,headers=headers)
    return response

def call_get_method_without_token(BASE_URL, endpoint):
    api_url = BASE_URL + endpoint
    headers = {
        'content-Type' : 'application/json'
    }
    response = requests.get(api_url,headers=headers)
    if response.status_code == 200:
        return response
    else:
        return response

def call_post_method_without_token_app_builder(BASE_URL, endpoint,project_id):
    api_url = BASE_URL + endpoint
    headers = {
        'content-Type' : 'application/json'
    }
    response = requests.get(api_url,data=project_id,headers=headers)
    if response.status_code == 200:
        return response
    else:
        return response

def call_get_method(BASE_URL, endpoint, access_token):
    api_url = BASE_URL + endpoint
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {access_token}'
    }

    response = requests.get(api_url, headers=headers)

    if response.status_code == 200:
        
        return response
    else:
        return response
    
def call_put_method_without_token(BASE_URL, endpoint, data):
    api_url = BASE_URL + endpoint
    headers = {
        'Content-Type': 'application/json',
    }
    response = requests.put(api_url, data=data, headers=headers)

    if response.status_code == 200:
        return response
    else:
        return response   
    
def call_put_method(BASE_URL, endpoint, data, access_token):
    api_url = BASE_URL + endpoint
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {access_token}'
    }
    response = requests.put(api_url, data=data, headers=headers)
    print('===response==',response.json())
    if response.status_code == 200:
        
        return response
    else:
        return response
    
def call_delete_method_without_token(BASE_URL, endpoint):
    api_url = BASE_URL + endpoint
    headers = {
        'Content-Type': 'application/json',
    }
    response = requests.delete(api_url, headers=headers)
    if response.status_code == 200:
        
        return response
    else:
        return response  
    
def call_delete_method(BASE_URL, endpoint,  access_token):
    api_url = BASE_URL + endpoint
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {access_token}'
    }
    response = requests.delete(api_url, headers=headers)

    if response.status_code == 200:
        
        return response
    else:
        return response
    



def call_post_method_with_token_v2(URL, endpoint, data, files=None):
    api_url = URL + endpoint
    # headers = {"Authorization": f'Bearer {access_token}'}
 
    if files:
        response = requests.post(api_url, data=data, files=files)
        print('response',response)
    else:
        headers = {
        'Content-Type': 'application/json', 
        }
        response = requests.post(api_url, data=data, headers=headers)
    if response.status_code in [200, 201]:
        try:
            return {'status_code': 0, 'data': response.json()}
        except json.JSONDecodeError:
            return {'status_code': 1, 'data': 'Invalid JSON response'}
    else:
        try:
            print('==response==',response)
            return {'status_code': 1, 'data': response.json()}
        except json.JSONDecodeError:
            return {'status_code': 1, 'data': 'Something went wrong'}
        

import requests
import json

def call_post_method_for_without_token_v2(base_url, endpoint, data):
    headers = {'Content-Type': 'application/json'}
    response = requests.post(
        f'{base_url}/{endpoint}',
        data=json.dumps({'content': data}),  # make sure it's dict, not raw string
        headers=headers
    )
    return response
