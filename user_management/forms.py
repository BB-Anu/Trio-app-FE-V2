from django import forms
from django.core.validators import MinValueValidator
from django.core.validators import FileExtensionValidator, MaxValueValidator
from .models import *


class RoleForm(forms.Form):
	name = forms.CharField(max_length=250, required=True, widget=forms.TextInput(attrs={"class": "form-control"}))
	description = forms.CharField(max_length=250, required=True, widget=forms.Textarea(attrs={"class": "form-control"}))
	permissions = forms.MultipleChoiceField( required=False, widget=forms.SelectMultiple(attrs={"class": "form-control"}))
	
	def __init__(self, *args, **kwargs):
		permissions_choices_list = kwargs.pop('permissions_choices', [])
		initial_data = kwargs.get("initial", {})
		selected_permissions_choices = initial_data.get('permissions', '')
		super().__init__(*args, **kwargs)
		self.fields['permissions'].choices = [('', '---select---')] + [
			(record.get('id', ''), record.get('function_name', '')) 
			for record in permissions_choices_list if isinstance(record, dict)
		]
		if selected_permissions_choices:
			self.fields['permissions'].initial = selected_permissions_choices


class SubCountyForm(forms.Form):
	name = forms.CharField(max_length=250, required=True, widget=forms.TextInput(attrs={"class": "form-control"}))
	county = forms.ChoiceField( required=False, widget=forms.Select(attrs={"class": "form-control"}))
	def __init__(self, *args, **kwargs):
		roles_choices_list = kwargs.pop('roles_choices', [])
		initial_data = kwargs.get("initial", {})
		selected_roles_choices = initial_data.get('county', '')
		super().__init__(*args, **kwargs)
		self.fields['county'].choices = [('', '---select---')] + [(record.get('id', ''), record.get('name', '')) for record in roles_choices_list]
		if selected_roles_choices:
			self.fields['county'].initial = selected_roles_choices



class WardForm(forms.Form):
	name = forms.CharField(max_length=250, required=True, widget=forms.TextInput(attrs={"class": "form-control"}))
	subcounty = forms.ChoiceField( required=False, widget=forms.Select(attrs={"class": "form-control"}))
	def __init__(self, *args, **kwargs):
		roles_choices_list = kwargs.pop('roles_choices', [])
		initial_data = kwargs.get("initial", {})
		selected_roles_choices = initial_data.get('subcounty', '')
		super().__init__(*args, **kwargs)
		self.fields['subcounty'].choices = [('', '---select---')] + [(record.get('id', ''), record.get('name', '')) for record in roles_choices_list]
		if selected_roles_choices:
			self.fields['subcounty'].initial = selected_roles_choices



class FunctionForm(forms.Form):
	function_name = forms.CharField(max_length=250, required=True, widget=forms.TextInput(attrs={"class": "form-control"}))
	function_id = forms.CharField(max_length=250, required=False, widget=forms.TextInput(attrs={"class": "form-control"}))
	description = forms.CharField(required=False, widget=forms.Textarea(attrs={"class": "form-control"}))


class CountyForm(forms.Form):
	name = forms.CharField(max_length=250, required=True, widget=forms.TextInput(attrs={"class": "form-control"}))
	

class UserForm(forms.Form):
	first_name = forms.CharField(max_length=250, required=True, widget=forms.TextInput(attrs={"class": "form-control"}))
	last_name = forms.CharField(max_length=250, required=True, widget=forms.TextInput(attrs={"class": "form-control"}))
	address = forms.CharField(max_length=250, required=True, widget=forms.TextInput(attrs={"class": "form-control"}))
	email = forms.EmailField(required=True, widget=forms.TextInput(attrs={"type": "email","class": "form-control"}))
	contact_number = forms.IntegerField(required=True, widget=forms.TextInput(attrs={"class": "form-control"}))
	password=forms.CharField(max_length=20, required=True, widget=forms.TextInput(attrs={"class": "form-control"}))
	roles=forms.ChoiceField( required=False, widget=forms.Select(attrs={"class": "form-control"}))
	def __init__(self, *args, **kwargs):
		roles_choices_list = kwargs.pop('roles_choices', [])
		initial_data = kwargs.get("initial", {})
		selected_roles_choices = initial_data.get('roles', '')
		super().__init__(*args, **kwargs)
		self.fields['roles'].choices = [('', '---select---')] + [(record.get('id', ''), record.get('name', '')) for record in roles_choices_list]
		if selected_roles_choices:
			self.fields['roles'].initial = selected_roles_choices


class CompanyForm(forms.Form):
	name = forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
	address = forms.CharField(max_length=255, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
	contact_number = forms.IntegerField(required=True, widget=forms.NumberInput(attrs={'class': 'form-control'}))
	email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control'}))
	# country = forms.ChoiceField( required=False, widget=forms.Select(attrs={"class": "form-control"}))
	# subcountry = forms.ChoiceField( required=False, widget=forms.Select(attrs={"class": "form-control"}))
	website = forms.URLField(required=False, widget=forms.URLInput(attrs={'class': 'form-control'}))
	company_logo = forms.FileField(required=False, widget=forms.ClearableFileInput(attrs={'class': 'form-control'}))
	incorporation_number = forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
	number_of_branches = forms.IntegerField(required=True, widget=forms.NumberInput(attrs={'class': 'form-control'}))
	number_of_staffs = forms.IntegerField(required=True, widget=forms.NumberInput(attrs={'class': 'form-control'}))
	end_of_financial_year = forms.DateField(required=False, widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}))
	end_of_month_date = forms.DateField(required=False, widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}))
	amount_rounded_to = forms.IntegerField(required=True, widget=forms.NumberInput(attrs={'class': 'form-control'}))
	local_currency = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
	# def __init__(self, *args, **kwargs):
	# 	country_choices_list = kwargs.pop('country_choices', [])
	# 	subcountry_choices_list = kwargs.pop('sub_country_choices', [])
	# 	initial_data = kwargs.get("initial", {})
	# 	selected_roles_choices = initial_data.get('country', '')
	# 	selected_subcountry_choices = initial_data.get('subcountry', '')
	# 	super().__init__(*args, **kwargs)
	# 	self.fields['country'].choices = [('', '---select---')] + [(record.get('id', ''), record.get('name', '')) for record in country_choices_list]
	# 	if selected_roles_choices:
	# 		self.fields['country'].initial = selected_roles_choices
	# 	self.fields['subcountry'].choices = [('', '---select---')] + [(record.get('id', ''), record.get('name', '')) for record in subcountry_choices_list]
	# 	if selected_subcountry_choices:
	# 		self.fields['subcountry'].initial = selected_subcountry_choices

class BranchForm(forms.Form):
	name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
	address = forms.CharField(max_length=255, widget=forms.TextInput(attrs={'class': 'form-control'}))
	phone_number = forms.IntegerField(widget=forms.NumberInput(attrs={'class': 'form-control'}))
	manager_name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
	# country = forms.ChoiceField( required=False, widget=forms.Select(attrs={"class": "form-control"}))
	# subcountry = forms.ChoiceField( required=False, widget=forms.Select(attrs={"class": "form-control"}))
	local_currency = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
	description = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control'}))

	# def __init__(self, *args, **kwargs):
	# 	country_choices_list = kwargs.pop('country_choices', [])
	# 	subcountry_choices_list = kwargs.pop('sub_country_choices', [])
	# 	initial_data = kwargs.get("initial", {})
	# 	selected_country_choices = initial_data.get('country', '')
	# 	selected_subcountry_choices = initial_data.get('subcountry', '')
	# 	super().__init__(*args, **kwargs)
		
	# 	self.fields['country'].choices = [('', '---select---')] + [(record.get('id', ''), record.get('name', '')) for record in country_choices_list]
	# 	if selected_country_choices:
	# 		self.fields['country'].initial = selected_country_choices
	# 	self.fields['subcountry'].choices = [('', '---select---')] + [(record.get('id', ''), record.get('name', '')) for record in subcountry_choices_list]
	# 	if selected_subcountry_choices:
	# 		self.fields['subcountry'].initial = selected_subcountry_choices
