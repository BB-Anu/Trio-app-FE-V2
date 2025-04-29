from django.urls import path
from .views import *
urlpatterns = [
    path("role/", role, name="role"),
    path("role_list/", role_list, name="role_list"),
	path("role_edit/<pk>/", role_edit, name="role_edit"),
	path("role_delete/<pk>/", role_delete, name="role_delete"),
	path("subcounty/", subcounty, name="subcounty"),
    path("subcounty_list/", subcounty_list, name="subcounty_list"),
	path("subcounty_edit/<pk>/", subcounty_edit, name="subcounty_edit"),
	path("subcounty_delete/<pk>/", subcounty_delete, name="subcounty_delete"),
    path("function/", function, name="function"),
    path("function_list/", function_list, name="function_list"),
	path("function_edit/<pk>/", function_edit, name="function_edit"),
	path("function_delete/<pk>/", function_delete, name="function_delete"),
	path("county/", county, name="county"),
    path("county_list/", county_list, name="county_list"),
	path("county_edit/<pk>/", county_edit, name="county_edit"),
	path("county_delete/<pk>/", county_delete, name="county_delete"),
	path("ward/", ward, name="ward"),
    path("ward_list/", ward_list, name="ward_list"),
	path("ward_edit/<pk>/", ward_edit, name="ward_edit"),
	path("ward_delete/<pk>/", ward_delete, name="ward_delete"),

 	path("user/", user, name="user"),
	path("user_list/", user_list, name="user_list"),
	path("user_edit/<pk>/", user_edit, name="user_edit"),
	path("user_delete/<pk>/", user_delete, name="user_delete"),
    
	path("company/", company, name="company"),
	path("company_create/", company_create, name="company_create"),
	path("company_edit/<pk>/", company_edit, name="company_edit"),
	path("company_delete/<pk>/", company_delete, name="company_delete"),
    
	path("branch/", branch, name="branch"),
	path("branch_create/", branch_create, name="branch_create"),
	path("branch_edit/<pk>/", branch_edit, name="branch_edit"),
	path("branch_delete/<pk>/", branch_delete, name="branch_delete"),
]
