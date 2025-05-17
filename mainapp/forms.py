from django import forms
from django.core.validators import MinValueValidator
from django.core.validators import FileExtensionValidator, MaxValueValidator
from .models import *

class ClientProfileForm(forms.Form):
	user = forms.ChoiceField( required=True, widget=forms.Select(attrs={"class": "form-control"}))
	business_name = forms.CharField(max_length=250, required=True, widget=forms.TextInput(attrs={"class": "form-control"}))
	business_type = forms.CharField(max_length=250, required=True, widget=forms.TextInput(attrs={"class": "form-control"}))
	registration_number = forms.CharField(max_length=250, required=True, widget=forms.TextInput(attrs={"class": "form-control"}))
	kra_pin = forms.CharField(max_length=250, required=True, widget=forms.TextInput(attrs={"class": "form-control"}))
	contact_email = forms.EmailField(required=True, widget=forms.TextInput(attrs={"type": "email","class": "form-control"}))
	contact_phone = forms.CharField(max_length=250, required=True, widget=forms.TextInput(attrs={"class": "form-control"}))
	address = forms.CharField( required=True, widget=forms.Textarea(attrs={"class": "form-control"}))
	tax_compliance_cert = forms.FileField(validators=[FileExtensionValidator(allowed_extensions=["pdf", "doc", "docx"])],required=False,widget=forms.ClearableFileInput(attrs={"class": "form-control-file"}))
	number_of_employees=forms.IntegerField(required=True,widget=forms.NumberInput(attrs={"class": "form-control"}))
	annual_turnover=forms.DecimalField(max_digits=None, decimal_places=None,required=True, widget=forms.NumberInput(attrs={"class": "form-control"}))
	def __init__(self, *args, **kwargs):
		user_choices_list = kwargs.pop('user_choices', [])
		initial_data = kwargs.get("initial", {})
		selected_user_choices = initial_data.get('user', '')
		super().__init__(*args, **kwargs)
		self.fields['user'].choices = [('', '---select---')] + [
			(
				record.get('id', ''),  
				f"{record['user'].get('name', '')} ({record['user'].get('roles', '')})"
			)
			for record in user_choices_list
		]		
		if selected_user_choices:
			self.fields['user'].initial = selected_user_choices


class DocumentGroupForm(forms.Form):
	group_name = forms.CharField(max_length=250, required=True, widget=forms.TextInput(attrs={"class": "form-control"}))
	description = forms.CharField(max_length=250, required=True, widget=forms.TextInput(attrs={"class": "form-control"}))


class CustomDocumentEntityForm(forms.Form):
	entity_id = forms.CharField(max_length=250, required=True, widget=forms.TextInput(attrs={"class": "form-control"}))
	entity_name = forms.CharField(max_length=250, required=True, widget=forms.TextInput(attrs={"class": "form-control"}))
	entity_type = forms.CharField(max_length=250, required=True, widget=forms.TextInput(attrs={"class": "form-control"}))
	description = forms.CharField(required=False, widget=forms.Textarea(attrs={"class": "form-control"}))



class TaskTemplateForm(forms.Form):
	title = forms.CharField(max_length=250, required=True, widget=forms.TextInput(attrs={"class": "form-control"}))
	description = forms.CharField( required=True, widget=forms.Textarea(attrs={"class": "form-control"}))
	hours_allocated = forms.FloatField(required=True, widget=forms.NumberInput(attrs={"class": "form-control"}))
	checklist = forms.CharField( required=True, widget=forms.Textarea(attrs={"class": "form-control"}))
	deliverables = forms.CharField( required=True, widget=forms.Textarea(attrs={"class": "form-control"}))


class TRIOGroupForm(forms.Form):
	name = forms.CharField(max_length=250, required=True, widget=forms.TextInput(attrs={"class": "form-control"}))
	description = forms.CharField( required=True, widget=forms.Textarea(attrs={"class": "form-control"}))
	enterprise_size = forms.ChoiceField( choices=[
		('NANO', 'Nano Enterprise'),
		('MICRO', 'Micro Enterprise'),
		('SMALL', 'Small Enterprise'),
		('MEDIUM', 'Medium Enterprise'),
	], widget=forms.Select(attrs={"class": "form-control"}))
	is_available = forms.BooleanField(required=False,widget=forms.CheckboxInput(attrs={"class": "form-check-input"}))
	

class LoanCaseForm(forms.Form):
	client = forms.ChoiceField( required=True, widget=forms.Select(attrs={"class": "form-control"}))
	case = forms.CharField(max_length=250, required=True, widget=forms.TextInput(attrs={"class": "form-control"}))
	start_date = forms.DateField(input_formats=['%Y-%m-%d'],required=True, widget=forms.DateInput(attrs={"type": "date","class": "form-control"}))
	# case_id = forms.CharField(max_length=250, required=True, widget=forms.TextInput(attrs={"class": "form-control"}))
	# case_reference = forms.CharField(max_length=250, required=True, widget=forms.TextInput(attrs={"class": "form-control"}))
	loan_amount = forms.DecimalField(max_digits=None, decimal_places=None,required=True, widget=forms.NumberInput(attrs={"class": "form-control"}))
	loan_purpose = forms.CharField( required=True, widget=forms.Textarea(attrs={"class": "form-control"}))
	def __init__(self, *args, **kwargs):
		user_choices_list = kwargs.pop('client_choices', [])
		initial_data = kwargs.get("initial", {})
		selected_user_choices = initial_data.get('client', '')
		super().__init__(*args, **kwargs)
		self.fields['client'].choices = [('', '---select---')] + [(record.get('id', ''), record.get('business_name', '')) for record in user_choices_list]
		if selected_user_choices:
			self.fields['client'].initial = selected_user_choices

class ProjectsForm(forms.Form):
	project_name = forms.CharField(max_length=250, required=True, widget=forms.TextInput(attrs={"class": "form-control"}))
	client = forms.MultipleChoiceField( required=True, widget=forms.SelectMultiple(attrs={"class": "form-control"}))
	start_date = forms.DateField(input_formats=['%Y-%m-%d'],required=True, widget=forms.DateInput(attrs={"type": "date","class": "form-control"}))
	end_date = forms.DateField(input_formats=['%Y-%m-%d'],required=False, widget=forms.DateInput(attrs={"type": "date","class": "form-control"}))
	status = forms.CharField(max_length=250, required=True, widget=forms.TextInput(attrs={"class": "form-control"}))
	def __init__(self, *args, **kwargs):
		user_choices_list = kwargs.pop('client_choices', [])
		initial_data = kwargs.get("initial", {})
		selected_user_choices = initial_data.get('client', '')
		super().__init__(*args, **kwargs)
		self.fields['client'].choices = [('', '---select---')] + [(record.get('id', ''), record.get('user', '')) for record in user_choices_list]
		if selected_user_choices:
			self.fields['client'].initial = selected_user_choices

class DocumentTypeForm(forms.Form):
	type = forms.CharField(max_length=250, required=True, widget=forms.TextInput(attrs={"class": "form-control"}))
	description = forms.CharField(max_length=250, required=True, widget=forms.TextInput(attrs={"class": "form-control"}))
	# group = forms.ChoiceField( required=True, widget=forms.Select(attrs={"class": "form-control"}))
	# def __init__(self, *args, **kwargs):
	# 	user_choices_list = kwargs.pop('group_choices', [])
	# 	initial_data = kwargs.get("initial", {})
	# 	selected_user_choices = initial_data.get('group', '')
	# 	super().__init__(*args, **kwargs)
	# 	self.fields['group'].choices = [('', '---select---')] + [(record.get('id', ''), record.get('group_name', '')) for record in user_choices_list]
	# 	if selected_user_choices:
	# 		self.fields['group'].initial = selected_user_choices

class FolderMasterForm(forms.Form):
	folder_id = forms.CharField(max_length=250, required=True, widget=forms.TextInput(attrs={"class": "form-control"}))
	folder_name = forms.CharField(max_length=250, required=True, widget=forms.TextInput(attrs={"class": "form-control"}))
	description = forms.CharField(required=False, widget=forms.Textarea(attrs={"class": "form-control"}))
	entity = forms.ChoiceField( required=True, widget=forms.Select(attrs={"class": "form-control"}))
	client = forms.ChoiceField( required=True, widget=forms.Select(attrs={"class": "form-control"}))
	master_checkbox_file = forms.BooleanField(required=False,widget=forms.CheckboxInput(attrs={"class": "form-check-input"}))
	parent_folder =forms.ChoiceField( required=False, widget=forms.Select(attrs={"class": "form-control"}))
	default_folder = forms.BooleanField(required=True,widget=forms.CheckboxInput(attrs={"class": "form-check-input"}))
	def __init__(self, *args, **kwargs):
		user_choices_list = kwargs.pop('client_choices', [])
		entity_choices_list = kwargs.pop('entity_choices', [])
		parent_folder_choices_list = kwargs.pop('parent_folder_choices', [])
		initial_data = kwargs.get("initial", {})
		selected_user_choices = initial_data.get('client', '')
		selected_entity_choices = initial_data.get('entity', '')
		selected_parent_folder_choices = initial_data.get('parent_folder', '')
		super().__init__(*args, **kwargs)
		self.fields['client'].choices = [('', '---select---')] + [
			(record.get('id', ''), record.get('user', {}).get('name', '')) for record in user_choices_list
		]
		self.fields['entity'].choices = [('', '---select---')] + [(record.get('id', ''), record.get('id', '')) for record in entity_choices_list]
		self.fields['parent_folder'].choices = [('', '---select---')] + [(record.get('id', ''), record.get('folder_name', '')) for record in parent_folder_choices_list]
		if selected_user_choices:
			self.fields['client'].initial = selected_user_choices
		if selected_entity_choices:
			self.fields['entity'].initial = selected_entity_choices
		if selected_parent_folder_choices:
			self.fields['parent_folder'].initial = selected_parent_folder_choices

class TRIOAssignmentForm(forms.Form):
	case = forms.ChoiceField( required=True, widget=forms.Select(attrs={"class": "form-control"}))
	group = forms.ChoiceField( required=True, widget=forms.Select(attrs={"class": "form-control"}))
	def __init__(self, *args, **kwargs):
		user_choices_list = kwargs.pop('client_choices', [])
		entity_choices_list = kwargs.pop('group_choices', [])
		initial_data = kwargs.get("initial", {})
		selected_user_choices = initial_data.get('case', '')
		selected_entity_choices = initial_data.get('group', '')
		super().__init__(*args, **kwargs)
		self.fields['case'].choices = [('', '---select---')] + [(record.get('id', ''), record.get('first_name', '')) for record in user_choices_list]
		self.fields['group'].choices = [('', '---select---')] + [(record.get('id', ''), record.get('name', '')) for record in entity_choices_list]
		if selected_user_choices:
			self.fields['case'].initial = selected_user_choices
		if selected_entity_choices:
			self.fields['group'].initial = selected_entity_choices

class AuditLogForm(forms.Form):
	user = forms.ChoiceField( required=True, widget=forms.Select(attrs={"class": "form-control"}))
	action = forms.CharField(max_length=250, required=True, widget=forms.TextInput(attrs={"class": "form-control"}))
	case = forms.ChoiceField( required=True, widget=forms.Select(attrs={"class": "form-control"}))
	def __init__(self, *args, **kwargs):
		user_choices_list = kwargs.pop('user_choices', [])
		entity_choices_list = kwargs.pop('case_choices', [])
		initial_data = kwargs.get("initial", {})
		selected_user_choices = initial_data.get('user', '')
		selected_entity_choices = initial_data.get('case', '')
		super().__init__(*args, **kwargs)
		self.fields['user'].choices = [('', '---select---')] + [(record.get('id', ''), record.get('first_name', '')) for record in user_choices_list]
		self.fields['case'].choices = [('', '---select---')] + [(record.get('id', ''), record.get('id', '')) for record in entity_choices_list]
		if selected_user_choices:
			self.fields['user'].initial = selected_user_choices
		if selected_entity_choices:
			self.fields['case'].initial = selected_entity_choices

class ComplianceChecklistForm(forms.Form):
	case = forms.ChoiceField( required=True, widget=forms.Select(attrs={"class": "form-control"}))
	item_name = forms.CharField(max_length=250, required=True, widget=forms.TextInput(attrs={"class": "form-control"}))
	is_verified = forms.BooleanField(required=True,widget=forms.CheckboxInput(attrs={"class": "form-check-input"}))
	def __init__(self, *args, **kwargs):
		entity_choices_list = kwargs.pop('case_choices', [])
		initial_data = kwargs.get("initial", {})
		selected_entity_choices = initial_data.get('case', '')
		super().__init__(*args, **kwargs)
		self.fields['case'].choices = [('', '---select---')] + [(record.get('id', ''), record.get('id', '')) for record in entity_choices_list]
		if selected_entity_choices:
			self.fields['case'].initial = selected_entity_choices

class DocumentForm(forms.Form):
	case = forms.ChoiceField( required=True, widget=forms.Select(attrs={"class": "form-control"}))
	document_type = forms.CharField(max_length=250, required=True, widget=forms.TextInput(attrs={"class": "form-control"}))
	file = forms.FileField(validators=[FileExtensionValidator(allowed_extensions=["pdf", "doc", "docx"])],required=False,widget=forms.ClearableFileInput(attrs={"class": "form-control-file"}))
	version = forms.IntegerField(required=True,widget=forms.NumberInput(attrs={"class": "form-control"}))
	def __init__(self, *args, **kwargs):
		entity_choices_list = kwargs.pop('case_choices', [])
		initial_data = kwargs.get("initial", {})
		selected_entity_choices = initial_data.get('case', '')
		super().__init__(*args, **kwargs)
		self.fields['case'].choices = [('', '---select---')] + [(record.get('id', ''), record.get('id', '')) for record in entity_choices_list]
		if selected_entity_choices:
			self.fields['case'].initial = selected_entity_choices

class ClientDocumentForm(forms.Form):
	# case = forms.ChoiceField( required=True, widget=forms.Select(attrs={"class": "form-control"}))
	document_type = forms.CharField(max_length=250, required=True, widget=forms.TextInput(attrs={"class": "form-control"}))
	file = forms.FileField(validators=[FileExtensionValidator(allowed_extensions=["pdf", "doc", "docx"])],required=True,widget=forms.ClearableFileInput(attrs={"class": "form-control-file"}))
	version = forms.IntegerField(required=True,widget=forms.NumberInput(attrs={"class": "form-control"}))

class RiskAssessmentForm(forms.Form):
	case = forms.ChoiceField( required=True, widget=forms.Select(attrs={"class": "form-control"}))
	analyst = forms.ChoiceField( required=True, widget=forms.Select(attrs={"class": "form-control"}))
	score = forms.IntegerField(required=True,widget=forms.NumberInput(attrs={"class": "form-control"}))
	grade = forms.CharField(max_length=250, required=True, widget=forms.TextInput(attrs={"class": "form-control"}))
	summary = forms.CharField( required=True, widget=forms.Textarea(attrs={"class": "form-control"}))
	recommendation = forms.CharField(max_length=250, required=True, widget=forms.TextInput(attrs={"class": "form-control"}))
	def __init__(self, *args, **kwargs):
		user_choices_list = kwargs.pop('user_choices', [])
		entity_choices_list = kwargs.pop('case_choices', [])
		initial_data = kwargs.get("initial", {})
		selected_user_choices = initial_data.get('analyst', '')
		selected_entity_choices = initial_data.get('case', '')
		super().__init__(*args, **kwargs)
		self.fields['analyst'].choices = [('', '---select---')] + [(record.get('id', ''), record.get('first_name', '')) for record in user_choices_list]
		self.fields['case'].choices = [('', '---select---')] + [(record.get('id', ''), record.get('id', '')) for record in entity_choices_list]
		if selected_user_choices:
			self.fields['analyst'].initial = selected_user_choices
		if selected_entity_choices:
			self.fields['case'].initial = selected_entity_choices

class ClientQueryForm(forms.Form):
	project = forms.ChoiceField( required=True, widget=forms.Select(attrs={"class": "form-control"}))
	client = forms.ChoiceField( required=True, widget=forms.Select(attrs={"class": "form-control"}))
	notes = forms.CharField(required=False, widget=forms.Textarea(attrs={"class": "form-control"}))
	filename = forms.CharField(max_length=250, required=False, widget=forms.TextInput(attrs={"class": "form-control"}))
	file_type = forms.CharField(max_length=250, required=False, widget=forms.TextInput(attrs={"class": "form-control"}))
	def __init__(self, *args, **kwargs):
		user_choices_list = kwargs.pop('client_choices', [])
		entity_choices_list = kwargs.pop('project_choices', [])
		initial_data = kwargs.get("initial", {})
		selected_user_choices = initial_data.get('client', '')
		selected_entity_choices = initial_data.get('project', '')
		super().__init__(*args, **kwargs)
		self.fields['client'].choices = [('', '---select---')] + [(record.get('id', ''), record.get('id', '')) for record in user_choices_list]
		self.fields['project'].choices = [('', '---select---')] + [(record.get('id', ''), record.get('id', '')) for record in entity_choices_list]
		if selected_user_choices:
			self.fields['client'].initial = selected_user_choices
		if selected_entity_choices:
			self.fields['project'].initial = selected_entity_choices


class TimeSheetForm(forms.Form):
	employee = forms.ChoiceField( required=True, widget=forms.Select(attrs={"class": "form-control"}))
	project = forms.ChoiceField( required=True, widget=forms.Select(attrs={"class": "form-control"}))
	date = forms.DateField(input_formats=['%Y-%m-%d'],required=True, widget=forms.DateInput(attrs={"type": "date","class": "form-control"}))
	total_working_hours = forms.FloatField(required=False, widget=forms.NumberInput(attrs={"class": "form-control"}))
	working_hours = forms.FloatField(required=False, widget=forms.NumberInput(attrs={"class": "form-control"}))
	status = forms.ChoiceField(choices=[('Pending', 'Pending'),('Completed', 'Completed'),('Approved', 'Approved'),('Rejected', 'Rejected')], required=False, widget=forms.Select(attrs={"class": "form-control"}))
	location = forms.CharField(required=False, widget=forms.Textarea(attrs={"class": "form-control"}))
	def __init__(self, *args, **kwargs):
		user_choices_list = kwargs.pop('employee_choices', [])
		entity_choices_list = kwargs.pop('project_choices', [])
		initial_data = kwargs.get("initial", {})
		selected_user_choices = initial_data.get('employee', '')
		selected_entity_choices = initial_data.get('project', '')
		super().__init__(*args, **kwargs)
		self.fields['employee'].choices = [('', '---select---')] + [(record.get('id', ''), record.get('id', '')) for record in user_choices_list]
		self.fields['project'].choices = [('', '---select---')] + [(record.get('id', ''), record.get('id', '')) for record in entity_choices_list]
		if selected_user_choices:
			self.fields['employee'].initial = selected_user_choices
		if selected_entity_choices:
			self.fields['project'].initial = selected_entity_choices

class DocumentUploadForm(forms.Form):
	document_id = forms.CharField(max_length=250, required=True, widget=forms.TextInput(attrs={"class": "form-control"}))
	document_title = forms.CharField(max_length=250, required=True, widget=forms.TextInput(attrs={"class": "form-control"}))
	document_type = forms.ChoiceField( required=True, widget=forms.Select(attrs={"class": "form-control"}))
	entity_type = forms.MultipleChoiceField( required=True, widget=forms.SelectMultiple(attrs={"class": "form-control"}))
	folder = forms.ChoiceField( required=True, widget=forms.Select(attrs={"class": "form-control"}))
	description = forms.CharField(required=False, widget=forms.Textarea(attrs={"class": "form-control"}))
	document_upload = forms.FileField(validators=[FileExtensionValidator(allowed_extensions=["pdf", "doc", "docx"])],required=False,widget=forms.ClearableFileInput(attrs={"class": "form-control-file"}))
	upload_date = forms.DateField(input_formats=['%Y-%m-%d'],required=False, widget=forms.DateInput(attrs={"type": "date","class": "form-control"}))
	expiry_date = forms.DateField(input_formats=['%Y-%m-%d'],required=False, widget=forms.DateInput(attrs={"type": "date","class": "form-control"}))
	start_date = forms.DateField(input_formats=['%Y-%m-%d'],required=False, widget=forms.DateInput(attrs={"type": "date","class": "form-control"}))
	end_date = forms.DateField(input_formats=['%Y-%m-%d'],required=False, widget=forms.DateInput(attrs={"type": "date","class": "form-control"}))
	def __init__(self, *args, **kwargs):
		user_choices_list = kwargs.pop('document_choices', [])
		entity_choices_list = kwargs.pop('entity_choices', [])
		folder_choices_list = kwargs.pop('folder_choices', [])
		initial_data = kwargs.get("initial", {})
		selected_user_choices = initial_data.get('document_type', '')
		selected_entity_choices = initial_data.get('entity_type', '')
		selected_folder_choices = initial_data.get('folder', '')
		super().__init__(*args, **kwargs)
		self.fields['document_type'].choices = [('', '---select---')] + [(record.get('id', ''), record.get('type', '')) for record in user_choices_list]
		self.fields['entity_type'].choices = [('', '---select---')] + [(record.get('id', ''), record.get('entity_name', '')) for record in entity_choices_list]
		self.fields['folder'].choices = [('', '---select---')] + [(record.get('id', ''), record.get('folder_name', '')) for record in folder_choices_list]
		if selected_user_choices:
			self.fields['document_type'].initial = selected_user_choices
		if selected_entity_choices:
			self.fields['entity_type'].initial = selected_entity_choices
		if selected_folder_choices:
			self.fields['folder'].initial = selected_folder_choices


class DocumentUploadAudit1Form(forms.Form):
	document_id = forms.CharField(max_length=250, required=True, widget=forms.TextInput(attrs={"class": "form-control"}))
	document_title = forms.CharField(max_length=250, required=True, widget=forms.TextInput(attrs={"class": "form-control"}))
	document_type = forms.ChoiceField( required=True, widget=forms.Select(attrs={"class": "form-control"}))
	folder = forms.ChoiceField( required=True, widget=forms.Select(attrs={"class": "form-control"}))
	description = forms.CharField(required=False, widget=forms.Textarea(attrs={"class": "form-control"}))
	document_upload = forms.FileField(validators=[FileExtensionValidator(allowed_extensions=["pdf", "doc", "docx"])],required=False,widget=forms.ClearableFileInput(attrs={"class": "form-control-file"}))
	upload_date = forms.DateField(input_formats=['%Y-%m-%d'],required=False, widget=forms.DateInput(attrs={"type": "date","class": "form-control"}))
	expiry_date = forms.DateField(input_formats=['%Y-%m-%d'],required=False, widget=forms.DateInput(attrs={"type": "date","class": "form-control"}))
	start_date = forms.DateField(input_formats=['%Y-%m-%d'],required=False, widget=forms.DateInput(attrs={"type": "date","class": "form-control"}))
	end_date = forms.DateField(input_formats=['%Y-%m-%d'],required=False, widget=forms.DateInput(attrs={"type": "date","class": "form-control"}))
	status = forms.ChoiceField(choices=[ ('created', 'Created'), ('updated', 'Updated'),('deleted', 'Deleted'),], required=True, widget=forms.Select(attrs={"class": "form-control"}))
	def __init__(self, *args, **kwargs):
		user_choices_list = kwargs.pop('document_choices', [])
		folder_choices_list = kwargs.pop('folder_choices', [])
		initial_data = kwargs.get("initial", {})
		selected_user_choices = initial_data.get('document_type', '')
		selected_folder_choices = initial_data.get('folder', '')
		super().__init__(*args, **kwargs)
		self.fields['document_type'].choices = [('', '---select---')] + [(record.get('id', ''), record.get('id', '')) for record in user_choices_list]
		self.fields['folder'].choices = [('', '---select---')] + [(record.get('id', ''), record.get('id', '')) for record in folder_choices_list]
		if selected_user_choices:
			self.fields['document_type'].initial = selected_user_choices
		if selected_folder_choices:
			self.fields['folder'].initial = selected_folder_choices


class DocumentUploadHistory1Form(forms.Form):
	document_id = forms.CharField(max_length=250, required=True, widget=forms.TextInput(attrs={"class": "form-control"}))
	document_title = forms.CharField(max_length=250, required=True, widget=forms.TextInput(attrs={"class": "form-control"}))
	document_type = forms.ChoiceField( required=True, widget=forms.Select(attrs={"class": "form-control"}))
	folder = forms.ChoiceField( required=True, widget=forms.Select(attrs={"class": "form-control"}))
	description = forms.CharField(required=False, widget=forms.Textarea(attrs={"class": "form-control"}))
	document_upload = forms.FileField(validators=[FileExtensionValidator(allowed_extensions=["pdf", "doc", "docx"])],required=False,widget=forms.ClearableFileInput(attrs={"class": "form-control-file"}))
	upload_date = forms.DateField(input_formats=['%Y-%m-%d'],required=False, widget=forms.DateInput(attrs={"type": "date","class": "form-control"}))
	expiry_date = forms.DateField(input_formats=['%Y-%m-%d'],required=False, widget=forms.DateInput(attrs={"type": "date","class": "form-control"}))
	start_date = forms.DateField(input_formats=['%Y-%m-%d'],required=False, widget=forms.DateInput(attrs={"type": "date","class": "form-control"}))
	end_date = forms.DateField(input_formats=['%Y-%m-%d'],required=False, widget=forms.DateInput(attrs={"type": "date","class": "form-control"}))
	is_deactivate = forms.BooleanField(required=True,widget=forms.CheckboxInput(attrs={"class": "form-check-input"}))
	version = forms.IntegerField(required=True,widget=forms.NumberInput(attrs={"class": "form-control"}))
	def __init__(self, *args, **kwargs):
		user_choices_list = kwargs.pop('document_choices', [])
		folder_choices_list = kwargs.pop('folder_choices', [])
		initial_data = kwargs.get("initial", {})
		selected_user_choices = initial_data.get('document_type', '')
		selected_folder_choices = initial_data.get('folder', '')
		super().__init__(*args, **kwargs)
		self.fields['document_type'].choices = [('', '---select---')] + [(record.get('id', ''), record.get('id', '')) for record in user_choices_list]
		self.fields['folder'].choices = [('', '---select---')] + [(record.get('id', ''), record.get('id', '')) for record in folder_choices_list]
		if selected_user_choices:
			self.fields['document_type'].initial = selected_user_choices
		if selected_folder_choices:
			self.fields['folder'].initial = selected_folder_choices

class UserProfileForm(forms.Form):
	user =  forms.ChoiceField( required=True, widget=forms.Select(attrs={"class": "form-control"}))
	# role =  forms.ChoiceField( required=True, widget=forms.Select(attrs={"class": "form-control"}))
	phone = forms.CharField(max_length=250, required=False, widget=forms.TextInput(attrs={"class": "form-control"}))
	email = forms.EmailField(required=True, widget=forms.TextInput(attrs={"type": "email","class": "form-control"}))
	profile_completed = forms.BooleanField(required=False,widget=forms.CheckboxInput(attrs={"class": "form-check-input"}))
	# status = forms.CharField(max_length=250, required=True, widget=forms.TextInput(attrs={"class": "form-control"}))
	def __init__(self, *args, **kwargs):
		user_choices_list = kwargs.pop('user_choices', [])
		# entity_choices_list = kwargs.pop('role_choices', [])
		initial_data = kwargs.get("initial", {})
		selected_user_choices = initial_data.get('user', '')
		# selected_entity_choices = initial_data.get('role', '')
		super().__init__(*args, **kwargs)
		self.fields['user'].choices = [('', '---select---')] + [
		(
			record.get('id', ''),
			f"{record.get('first_name', '')} ({record.get('roles', {}).get('name', '')})"
		)
		for record in user_choices_list
		]		# self.fields['role'].choices = [('', '---select---')] + [(record.get('id', ''), record.get('id', '')) for record in entity_choices_list]
		if selected_user_choices:
			self.fields['user'].initial = selected_user_choices
		# if selected_entity_choices:
		# 	self.fields['role'].initial = selected_entity_choices


class DocumentAccessForm(forms.Form):
	document =  forms.ChoiceField( required=True, widget=forms.Select(attrs={"class": "form-control"}))
	access_to =  forms.ChoiceField( required=True, widget=forms.Select(attrs={"class": "form-control"}))
	permission = forms.CharField(required=False, widget=forms.Textarea(attrs={"class": "form-control"}))
	expiry_from_at = forms.DateTimeField(required=False, widget=forms.DateTimeInput(attrs={"type": "date","class": "form-control"}))
	expiry_to_at = forms.DateTimeField(required=False, widget=forms.DateTimeInput(attrs={"type": "date","class": "form-control"}))	
	def __init__(self, *args, **kwargs):
		user_choices_list = kwargs.pop('user_choices', [])
		entity_choices_list = kwargs.pop('document_choices', [])
		initial_data = kwargs.get("initial", {})
		selected_user_choices = initial_data.get('access_to', '')
		selected_entity_choices = initial_data.get('document', '')
		super().__init__(*args, **kwargs)
		self.fields['access_to'].choices = [('', '---select---')] + [(record.get('id', ''), record.get('first_name', '')) for record in user_choices_list]
		self.fields['document'].choices = [('', '---select---')] + [(record.get('id', ''), record.get('document_title', '')) for record in entity_choices_list]
		if selected_user_choices:
			self.fields['access_to'].initial = selected_user_choices
		if selected_entity_choices:
			self.fields['document'].initial = selected_entity_choices

class FileDownloadReasonForm(forms.Form):
	document = forms.ChoiceField( required=True, widget=forms.Select(attrs={"class": "form-control"}))
	reason = forms.CharField( required=True, widget=forms.Textarea(attrs={"class": "form-control"}))
	def __init__(self, *args, **kwargs):
		entity_choices_list = kwargs.pop('document_choices', [])
		initial_data = kwargs.get("initial", {})
		selected_entity_choices = initial_data.get('document', '')
		super().__init__(*args, **kwargs)
		self.fields['document'].choices = [('', '---select---')] + [(record.get('id', ''), record.get('document_title', '')) for record in entity_choices_list]
		if selected_entity_choices:
			self.fields['document'].initial = selected_entity_choices

class CaseAssignmentForm(forms.Form):
	case = forms.ChoiceField( required=True, widget=forms.Select(attrs={"class": "form-control"}))
	user = forms.ChoiceField( required=True, widget=forms.Select(attrs={"class": "form-control"}))
	assigned_to = forms.MultipleChoiceField( required=True, widget=forms.SelectMultiple(attrs={"class": "form-control"}))
	# role = forms.CharField(max_length=250, required=True, widget=forms.TextInput(attrs={"class": "form-control"}))
	# assigned_at = forms.DateTimeField(required=True, widget=forms.DateTimeInput(attrs={"type": "date","class": "form-control"}))
	due_date = forms.DateField(input_formats=['%Y-%m-%d'],required=True, widget=forms.DateInput(attrs={"type": "date","class": "form-control"}))
	def __init__(self, *args, **kwargs):
		user_choices_list = kwargs.pop('user_choices', [])
		entity_choices_list = kwargs.pop('case_choices', [])
		assigned_to_choices_list = kwargs.pop('assigned_to_choices', [])
		initial_data = kwargs.get("initial", {})
		selected_user_choices = initial_data.get('user', '')
		selected_entity_choices = initial_data.get('case', '')
		selected_assigned_to_choices = initial_data.get('assigned_to', '')
		super().__init__(*args, **kwargs)
		self.fields['user'].choices = [('', '---select---')] + [(record.get('id', ''), record.get('first_name', '')) for record in user_choices_list]
		self.fields['assigned_to'].choices = [
			('', '---select---')
		] + [
			(record['user']['id'], f"{record['user']['name']} ({record['user']['roles']})")
			for record in assigned_to_choices_list if 'user' in record and record['user']
		]		
		self.fields['case'].choices = [('', '---select---')] + [(record.get('id', ''), record.get('id', '')) for record in entity_choices_list]
		if selected_user_choices:
			self.fields['user'].initial = selected_user_choices
		if selected_assigned_to_choices:
			self.fields['assigned_to'].initial = selected_assigned_to_choices
		if selected_entity_choices:
			self.fields['case'].initial = selected_entity_choices

class TRIOGroupMemberForm(forms.Form):
	group = forms.ChoiceField( required=True, widget=forms.Select(attrs={"class": "form-control"}))
	profile = forms.MultipleChoiceField( required=True, widget=forms.SelectMultiple(attrs={"class": "form-control",'rows':4}))
	def __init__(self, *args, **kwargs):
		user_choices_list = kwargs.pop('user_choices', [])
		entity_choices_list = kwargs.pop('case_choices', [])
		initial_data = kwargs.get("initial", {})
		selected_user_choices = initial_data.get('profile', '')
		selected_entity_choices = initial_data.get('group', '')
		super().__init__(*args, **kwargs)
		self.fields['profile'].choices = [('', '---select---')] + [
		(
			record.get('id', ''),
			f"{record.get('user', {}).get('name', '')} ({record.get('user', {}).get('roles', '')})"
		)
		for record in user_choices_list
		if record.get('user', {}).get('roles', '').lower() != 'customer'
	]
		self.fields['group'].choices = [('', '---select---')] + [(record.get('id', ''), record.get('name', '')) for record in entity_choices_list]
		if selected_user_choices:
			self.fields['profile'].initial = selected_user_choices
		if selected_entity_choices:
			self.fields['group'].initial = selected_entity_choices

# class TRIOProfileForm(forms.Form):
# 	user = forms.ChoiceField( required=True, widget=forms.Select(attrs={"class": "form-control"}))
# 	task_template = forms.ChoiceField( required=True, widget=forms.Select(attrs={"class": "form-control"}))
# 	qualification = forms.CharField( required=True, widget=forms.Textarea(attrs={"class": "form-control"}))
# 	experience_years = forms.IntegerField(required=True,widget=forms.NumberInput(attrs={"class": "form-control"}))
# 	phone = forms.CharField(max_length=250, required=True, widget=forms.TextInput(attrs={"class": "form-control"}))
# 	is_active = forms.BooleanField(required=True,widget=forms.CheckboxInput(attrs={"class": "form-check-input"}))
# 	def __init__(self, *args, **kwargs):
# 		user_choices_list = kwargs.pop('user_choices', [])
# 		entity_choices_list = kwargs.pop('task_template_choices', [])
# 		initial_data = kwargs.get("initial", {})
# 		selected_user_choices = initial_data.get('user', '')
# 		selected_entity_choices = initial_data.get('task_template', '')
# 		super().__init__(*args, **kwargs)
	
# 		self.fields['user'].choices = [('', '---select---')] + [
#     (
#         record.get('id', ''),
#         f"{record.get('group', {}).get('name', '')} ({record.get('group', {}).get('roles', '')})"
#     )
#     for record in user_choices_list
#     if isinstance(record.get('group'), dict) and record.get('group', {}).get('roles', '').lower() != 'customer'
# ]


# 		self.fields['task_template'].choices = [('', '---select---')] + [
# 			(record.get('id', ''), record.get('template', {}).get('name', '')) for record in entity_choices_list
# 		]
# 		if selected_user_choices:
# 			self.fields['user'].initial = selected_user_choices
# 		if selected_entity_choices:
# 			self.fields['task_template'].initial = selected_entity_choices
class TRIOProfileForm(forms.Form):
		user = forms.ChoiceField( required=True, widget=forms.Select(attrs={"class": "form-control"}))
		task_template = forms.ChoiceField( required=True, widget=forms.Select(attrs={"class": "form-control"}))
		qualification = forms.CharField( required=True, widget=forms.Textarea(attrs={"class": "form-control"}))
		experience_years = forms.IntegerField(required=True,widget=forms.NumberInput(attrs={"class": "form-control"}))
		phone = forms.CharField(max_length=250, required=True, widget=forms.TextInput(attrs={"class": "form-control"}))
		is_active = forms.BooleanField(required=False,widget=forms.CheckboxInput(attrs={"class": "form-check-input"}))
		def __init__(self, *args, **kwargs):
			user_choices_list = kwargs.pop('user_choices', [])
			entity_choices_list = kwargs.pop('task_template_choices', [])
			initial_data = kwargs.get("initial", {})
			selected_user_choices = initial_data.get('user', '')
			selected_entity_choices = initial_data.get('task_template', '')
			super().__init__(*args, **kwargs)

			self.fields['user'].choices = [('', '---select---')] + [
			(
				record['id'],  # Use client ID here
				f"{record['user']['name']} ({record['user']['roles']})"
			)
			for record in user_choices_list
			if record.get('user') and record['user'].get('roles', '').lower() != 'customer'
		]

			self.fields['task_template'].choices = [('', '---select---')] + [
				(record.get('id', ''), record.get('template', {}).get('name', '')) for record in entity_choices_list
			]

			if selected_user_choices:
				self.fields['user'].initial = selected_user_choices
			if selected_entity_choices:
				self.fields['task_template'].initial = selected_entity_choices

class FinalReportForm(forms.Form):
	assignment = forms.ChoiceField( required=True, widget=forms.Select(attrs={"class": "form-control"}))
	report_title = forms.CharField(max_length=250, required=True, widget=forms.TextInput(attrs={"class": "form-control"}))
	content = forms.CharField( required=True, widget=forms.Textarea(attrs={"class": "form-control"}))
	def __init__(self, *args, **kwargs):
		entity_choices_list = kwargs.pop('role_choices', [])
		initial_data = kwargs.get("initial", {})
		selected_entity_choices = initial_data.get('assignment', '')
		super().__init__(*args, **kwargs)
		self.fields['assignment'].choices = [('', '---select---')] + [(record.get('id', ''), record.get('id', '')) for record in entity_choices_list]
		if selected_entity_choices:
			self.fields['assignment'].initial = selected_entity_choices

class TaskForm(forms.Form):
	assignment = forms.ChoiceField( required=True, widget=forms.Select(attrs={"class": "form-control"}))
	template = forms.ChoiceField( required=True, widget=forms.Select(attrs={"class": "form-control"}))
	assigned_to = forms.ChoiceField( required=True, widget=forms.Select(attrs={"class": "form-control"}))
	due_date = forms.DateField(input_formats=['%Y-%m-%d'],required=True, widget=forms.DateInput(attrs={"type": "date","class": "form-control"}))
	def __init__(self, *args, **kwargs):
		assignment_choices_list = kwargs.pop('assignment_choices', [])
		template_choices_list = kwargs.pop('template_choices', [])
		assigned_to_choices_list = kwargs.pop('assigned_to_choices', [])
		initial_data = kwargs.get("initial", {})
		selected_entity_choices = initial_data.get('assignment', '')
		selected_template_choices = initial_data.get('template', '')
		selected_assigned_to_choices = initial_data.get('assigned_to', '')
		super().__init__(*args, **kwargs)
		self.fields['assignment'].choices = [('', '---select---')] + [(record.get('id', ''), record.get('id', '')) for record in assignment_choices_list]
		self.fields['template'].choices = [('', '---select---')] + [(record.get('id', ''), record.get('id', '')) for record in template_choices_list]
		self.fields['assigned_to'].choices = [('', '---select---')] + [(record.get('id', ''), record.get('id', '')) for record in assigned_to_choices_list]
		if selected_entity_choices:
			self.fields['assignment'].initial = selected_entity_choices
		if selected_template_choices:
			self.fields['template'].initial = selected_template_choices		
		if selected_assigned_to_choices:
			self.fields['assigned_to'].initial = selected_assigned_to_choices


class TaskAuditLogForm(forms.Form):
	task = forms.ChoiceField( required=True, widget=forms.Select(attrs={"class": "form-control"}))
	message = forms.CharField( required=True, widget=forms.Textarea(attrs={"class": "form-control"}))
	def __init__(self, *args, **kwargs):
		entity_choices_list = kwargs.pop('task_choices', [])
		initial_data = kwargs.get("initial", {})
		selected_entity_choices = initial_data.get('task', '')
		super().__init__(*args, **kwargs)
		self.fields['task'].choices = [('', '---select---')] + [(record.get('id', ''), record.get('id', '')) for record in entity_choices_list]
		if selected_entity_choices:
			self.fields['task'].initial = selected_entity_choices


class TaskDeliverableForm(forms.Form):
	task = forms.ChoiceField( required=True, widget=forms.Select(attrs={"class": "form-control"}))
	file = forms.FileField(validators=[FileExtensionValidator(allowed_extensions=["pdf", "doc", "docx"])],required=True,widget=forms.ClearableFileInput(attrs={"class": "form-control-file"}))
	description = forms.CharField( required=True, widget=forms.Textarea(attrs={"class": "form-control"}))
	uploaded_on = forms.DateTimeField(required=True, widget=forms.DateTimeInput(attrs={"type": "date","class": "form-control"}))
	def __init__(self, *args, **kwargs):
		entity_choices_list = kwargs.pop('task_choices', [])
		initial_data = kwargs.get("initial", {})
		selected_entity_choices = initial_data.get('task', '')
		super().__init__(*args, **kwargs)
		self.fields['task'].choices = [('', '---select---')] + [(record.get('id', ''), record.get('id', '')) for record in entity_choices_list]
		if selected_entity_choices:
			self.fields['task'].initial = selected_entity_choices

class TaskTimesheetForm(forms.Form):
	employee = forms.ChoiceField( required=True, widget=forms.Select(attrs={"class": "form-control"}))
	# task = forms.ChoiceField( required=True, widget=forms.Select(attrs={"class": "form-control"}))
	task = forms.CharField( max_length=250,required=True, widget=forms.TextInput(attrs={"class": "form-control"}))
	date = forms.DateField(input_formats=['%Y-%m-%d'],required=True, widget=forms.DateInput(attrs={"type": "date","class": "form-control"}))
	total_working_hours = forms.FloatField(required=False, widget=forms.NumberInput(attrs={"class": "form-control"}))
	hours_spent = forms.FloatField(required=True, widget=forms.NumberInput(attrs={"class": "form-control"}))
	remarks = forms.CharField( required=True, widget=forms.Textarea(attrs={"class": "form-control"}))
	def __init__(self, *args, **kwargs):
		user_choices_list = kwargs.pop('user_choices', [])
		# entity_choices_list = kwargs.pop('task_choices', [])
		initial_data = kwargs.get("initial", {})
		selected_user_choices = initial_data.get('employee', '')
		# selected_entity_choices = initial_data.get('task', '')
		super().__init__(*args, **kwargs)
		self.fields['employee'].choices = [('', '---select---')] + [(record.get('id', ''), record.get('user', '')) for record in user_choices_list]
		# self.fields['task'].choices = [('', '---select---')] + [(record.get('id', ''), record.get('id', '')) for record in entity_choices_list]
		# if selected_entity_choices:
			# self.fields['task'].initial = selected_entity_choices
		if selected_user_choices:
			self.fields['employee'].initial = selected_user_choices
	
# class TimesheetEntryForm(forms.Form):
# 	timesheet = forms.ChoiceField( required=True, widget=forms.Select(attrs={"class": "form-control"}))
# 	task = forms.ChoiceField( required=True, widget=forms.Select(attrs={"class": "form-control"}))
# 	given_hours = forms.FloatField(required=True, widget=forms.NumberInput(attrs={"class": "form-control", "readonly": "readonly"}))
# 	hours = forms.FloatField(required=True, widget=forms.NumberInput(attrs={"class": "form-control"}))
# 	work_done = forms.CharField( required=True, widget=forms.Textarea(attrs={"class": "form-control"}))
# 	uploaded_at = forms.DateTimeField(required=True, widget=forms.DateTimeInput(attrs={"type": "date","class": "form-control"}))
# 	filename = forms.CharField(max_length=250, required=False, widget=forms.TextInput(attrs={"class": "form-control"}))
# 	file_type = forms.CharField(max_length=250, required=False, widget=forms.TextInput(attrs={"class": "form-control"}))
# 	attachment_name = forms.CharField(max_length=250, required=False, widget=forms.TextInput(attrs={"class": "form-control"}))
# 	attachment_type = forms.CharField(max_length=250, required=False, widget=forms.TextInput(attrs={"class": "form-control"}))
# 	def __init__(self, *args, **kwargs):
# 		user_choices_list = kwargs.pop('timesheet_choices', [])
# 		entity_choices_list = kwargs.pop('task_choices', [])
# 		initial_data = kwargs.get("initial", {})
# 		selected_user_choices = initial_data.get('timesheet', '')
# 		selected_entity_choices = initial_data.get('task', '')
# 		super().__init__(*args, **kwargs)
# 		self.fields['timesheet'].choices = [('', '---select---')] + [
# 			(record.get('id', ''), f"{record.get('id', '')} - {record.get('task', '')[:70]}")
# 			for record in user_choices_list
# 		]
# 		self.fields['task'].choices = [('', '---select---')] + [
# 			(record.get('id', ''), f"{record.get('id', '')} - {record.get('template', {}).get('name', '')}")
# 			for record in entity_choices_list
# 		]
# 		if selected_entity_choices:
# 			self.fields['task'].initial = selected_entity_choices
# 		if selected_user_choices:
# 			self.fields['timesheet'].initial = selected_user_choices

class TimesheetEntryForm(forms.Form):
	task = forms.ChoiceField(required=True, widget=forms.Select(attrs={"class": "form-control"}))
	timesheet = forms.ChoiceField(required=True, widget=forms.Select(attrs={"class": "form-control"}))
	given_hours = forms.FloatField(required=True, widget=forms.NumberInput(attrs={"class": "form-control", "readonly": "readonly"}))
	hours = forms.FloatField(required=True, widget=forms.NumberInput(attrs={"class": "form-control"}))
	work_done = forms.CharField(required=True, widget=forms.Textarea(attrs={"class": "form-control"}))
	document=forms.FileField(validators=[FileExtensionValidator(allowed_extensions=["pdf", "doc", "docx"])],required=False,widget=forms.ClearableFileInput(attrs={"class": "form-control-file"}))
	filename = forms.CharField(max_length=250, required=False, widget=forms.TextInput(attrs={"class": "form-control"}))
	file_type = forms.CharField(max_length=250, required=False, widget=forms.TextInput(attrs={"class": "form-control"}))
	attachment=forms.FileField(validators=[FileExtensionValidator(allowed_extensions=["pdf", "doc", "docx"])],required=False,widget=forms.ClearableFileInput(attrs={"class": "form-control-file"}))
	attachment_name = forms.CharField(max_length=250, required=False, widget=forms.TextInput(attrs={"class": "form-control"}))
	attachment_type = forms.CharField(max_length=250, required=False, widget=forms.TextInput(attrs={"class": "form-control"}))

	def __init__(self, *args, **kwargs):
		user_choices_list = kwargs.pop('timesheet_choices', [])
		entity_choices_list = kwargs.pop('task_choices', [])
		initial_data = kwargs.get("initial", {})
		selected_user_choices = initial_data.get('timesheet', '')
		selected_entity_choices = initial_data.get('task', '')
		super().__init__(*args, **kwargs)
		self.fields['timesheet'].choices = [('', '---select---')] + [
			(record.get('id', ''), f"{record.get('id', '')} - {record.get('task', '')[:70]}")
			for record in user_choices_list
		]
		self.fields['task'].choices = [('', '---select---')] + [
			(record.get('id', ''), f"{record.get('id', '')} - {record.get('template', {}).get('name', '')}")
			for record in entity_choices_list
		]
		if selected_entity_choices:
			self.fields['task'].initial = selected_entity_choices
		if selected_user_choices:
			self.fields['timesheet'].initial = selected_user_choices

	def clean(self):
		cleaned_data = super().clean()
		given_hours = cleaned_data.get('given_hours')
		entered_hours = cleaned_data.get('hours')

		if given_hours is not None and entered_hours is not None:
			if entered_hours > given_hours:
				raise forms.ValidationError(f"Entered hours ({entered_hours}) exceed the available given hours ({given_hours}).")


class TimesheetAttachmentForm(forms.Form):
	entry = forms.ChoiceField( required=True, widget=forms.Select(attrs={"class": "form-control"}))
	filename = forms.CharField(max_length=250, required=True, widget=forms.TextInput(attrs={"class": "form-control"}))
	file_type = forms.CharField(max_length=250, required=True, widget=forms.TextInput(attrs={"class": "form-control"}))
	created_at = forms.DateTimeField(required=True, widget=forms.DateTimeInput(attrs={"type": "date","class": "form-control"}))
	def __init__(self, *args, **kwargs):
		entity_choices_list = kwargs.pop('task_choices', [])
		initial_data = kwargs.get("initial", {})
		selected_entity_choices = initial_data.get('entry', '')
		super().__init__(*args, **kwargs)
		self.fields['entry'].choices = [('', '---select---')] + [(record.get('id', ''), record.get('id', '')) for record in entity_choices_list]
		if selected_entity_choices:
			self.fields['entry'].initial = selected_entity_choices


class TimesheetDocumentForm(forms.Form):
	entry = forms.ChoiceField( required=True, widget=forms.Select(attrs={"class": "form-control"}))
	filename = forms.CharField(max_length=250, required=True, widget=forms.TextInput(attrs={"class": "form-control"}))
	file_type = forms.CharField(max_length=250, required=True, widget=forms.TextInput(attrs={"class": "form-control"}))
	created_at = forms.DateTimeField(required=True, widget=forms.DateTimeInput(attrs={"type": "date","class": "form-control"}))
	def __init__(self, *args, **kwargs):
		entity_choices_list = kwargs.pop('task_choices', [])
		initial_data = kwargs.get("initial", {})
		selected_entity_choices = initial_data.get('entry', '')
		super().__init__(*args, **kwargs)
		self.fields['entry'].choices = [('', '---select---')] + [(record.get('id', ''), record.get('id', '')) for record in entity_choices_list]
		if selected_entity_choices:
			self.fields['entry'].initial = selected_entity_choices

class WorkScheduleForm(forms.Form):
	monday = forms.CharField(max_length=250, required=False, widget=forms.TextInput(attrs={"class": "form-control"}))
	tuesday = forms.CharField(max_length=250, required=False, widget=forms.TextInput(attrs={"class": "form-control"}))
	wednesday = forms.CharField(max_length=250, required=False, widget=forms.TextInput(attrs={"class": "form-control"}))
	thursday = forms.CharField(max_length=250, required=False, widget=forms.TextInput(attrs={"class": "form-control"}))
	friday = forms.CharField(max_length=250, required=False, widget=forms.TextInput(attrs={"class": "form-control"}))
	saturday = forms.CharField(max_length=250, required=False, widget=forms.TextInput(attrs={"class": "form-control"}))
	sunday = forms.CharField(max_length=250, required=False, widget=forms.TextInput(attrs={"class": "form-control"}))
	created_by = forms.CharField(max_length=250, required=False, widget=forms.TextInput(attrs={"class": "form-control"}))
	created_at = forms.DateTimeField(required=False, widget=forms.DateTimeInput(attrs={"type": "date","class": "form-control"}))


class TaskExtraHoursRequestForm(forms.Form):
	task = forms.ChoiceField( required=True, widget=forms.Select(attrs={"class": "form-control"}))
	employee = forms.ChoiceField( required=True, widget=forms.Select(attrs={"class": "form-control"}))
	approved = forms.BooleanField(required=False,widget=forms.CheckboxInput(attrs={"class": "form-check-input"}))
	approved = forms.BooleanField(required=False,widget=forms.CheckboxInput(attrs={"class": "form-check-input"}))
	reason = forms.CharField(required=False, widget=forms.Textarea(attrs={"class": "form-control"}))
	def __init__(self, *args, **kwargs):
		entity_choices_list = kwargs.pop('task_choices', [])
		user_choices_list = kwargs.pop('user_choices', [])
		initial_data = kwargs.get("initial", {})
		selected_entity_choices = initial_data.get('task', '')
		selected_user_choices = initial_data.get('employee', '')
		super().__init__(*args, **kwargs)
		self.fields['task'].choices = [('', '---select---')] + [(record.get('id', ''), record.get('id', '')) for record in entity_choices_list]
		self.fields['employee'].choices = [('', '---select---')] + [(record.get('id', ''), record.get('first_name', '')) for record in user_choices_list]
		if selected_user_choices:
			self.fields['employee'].initial = selected_user_choices
		if selected_entity_choices:
			self.fields['task'].initial = selected_entity_choices



class MeetingsForm(forms.Form):
	title = forms.CharField(max_length=250, required=False, widget=forms.TextInput(attrs={"class": "form-control"}))
	location = forms.CharField(max_length=250, required=False, widget=forms.TextInput(attrs={"class": "form-control"}))
	attendees = forms.MultipleChoiceField( required=True, widget=forms.SelectMultiple(attrs={"class": "form-control"}))
	purpose = forms.CharField(required=False, widget=forms.Textarea(attrs={"class": "form-control"}))
	meeting_agenda = forms.CharField(required=False, widget=forms.Textarea(attrs={"class": "form-control"}))
	meeting_notes = forms.CharField(required=False, widget=forms.Textarea(attrs={"class": "form-control"}))
	meeting_date = forms.DateField(input_formats=['%Y-%m-%d'],required=True, widget=forms.DateInput(attrs={"type": "date","class": "form-control"}))
	meeting_time =  forms.TimeField(input_formats=["%H:%M:%S"],required=False, widget=forms.TimeInput(attrs={"class": "your-time-input-class form-control"}))
	delivery_date = forms.DateField(input_formats=['%Y-%m-%d'],required=False, widget=forms.DateInput(attrs={"type": "date","class": "form-control"}))
	filename = forms.CharField(max_length=250, required=False, widget=forms.TextInput(attrs={"class": "form-control"}))
	file_type = forms.CharField(max_length=250, required=False, widget=forms.TextInput(attrs={"class": "form-control"}))
	secretary = forms.ChoiceField( required=True, widget=forms.Select(attrs={"class": "form-control"}))
	status = forms.CharField(max_length=250, required=True, widget=forms.TextInput(attrs={"class": "form-control"}))
	reschedule_reason = forms.CharField(max_length=250, required=False, widget=forms.TextInput(attrs={"class": "form-control"}))
	closed = forms.BooleanField(required=True,widget=forms.CheckboxInput(attrs={"class": "form-check-input"}))
	def __init__(self, *args, **kwargs):
		entity_choices_list = kwargs.pop('attendees_choices', [])
		user_choices_list = kwargs.pop('user_choices', [])
		initial_data = kwargs.get("initial", {})
		selected_entity_choices = initial_data.get('attendees', '')
		selected_user_choices = initial_data.get('secretary', '')
		super().__init__(*args, **kwargs)
		self.fields['attendees'].choices = [('', '---select---')] + [(record.get('id', ''), record.get('id', '')) for record in entity_choices_list]
		self.fields['secretary'].choices = [('', '---select---')] + [(record.get('id', ''), record.get('first_name', '')) for record in user_choices_list]
		if selected_user_choices:
			self.fields['secretary'].initial = selected_user_choices
		if selected_entity_choices:
			self.fields['attendees'].initial = selected_entity_choices

class AuditorProfileForm(forms.Form):
	user = forms.ChoiceField( required=True, widget=forms.Select(attrs={"class": "form-control"}))
	firm_name = forms.CharField(max_length=250, required=True, widget=forms.TextInput(attrs={"class": "form-control"}))
	license_number = forms.CharField(max_length=250, required=True, widget=forms.TextInput(attrs={"class": "form-control"}))
	qualifications = forms.CharField(required=False, widget=forms.Textarea(attrs={"class": "form-control"}))
	years_of_experience=forms.IntegerField( required=True, widget=forms.NumberInput(attrs={"class": "form-control"}))

	accreditation_body = forms.CharField(max_length=250, required=False, widget=forms.TextInput(attrs={"class": "form-control"}))
	contact_phone = forms.CharField(max_length=250, required=True, widget=forms.TextInput(attrs={"class": "form-control"}))
	contact_email = forms.EmailField(required=True, widget=forms.TextInput(attrs={"type": "email","class": "form-control"}))
	address = forms.CharField( required=True, widget=forms.Textarea(attrs={"class": "form-control"}))
	is_internal = forms.BooleanField(required=False,widget=forms.CheckboxInput(attrs={"class": "form-check-input"}))
	nda_signed = forms.BooleanField(required=False,widget=forms.CheckboxInput(attrs={"class": "form-check-input"}))
	active = forms.BooleanField(required=False,widget=forms.CheckboxInput(attrs={"class": "form-check-input"}))

	def __init__(self, *args, **kwargs):
		user_choices_list = kwargs.pop('user_choices', [])
		initial_data = kwargs.get("initial", {})
		selected_user_choices = initial_data.get('user', '')
		super().__init__(*args, **kwargs)
		self.fields['user'].choices = [('', '---select---')] + [
		(
			record.get('id', ''), 
			f"{record['user'].get('name', '')} ({record['user'].get('roles', '')})"
		)
		for record in user_choices_list
		]
		if selected_user_choices:
			self.fields['user'].initial = selected_user_choices

class MarketingAgentProfileForm(forms.Form):
	user = forms.ChoiceField( required=True, widget=forms.Select(attrs={"class": "form-control"}))
	agency_name = forms.CharField(max_length=250, required=False, widget=forms.TextInput(attrs={"class": "form-control"}))
	expertise_area = forms.CharField(max_length=250, required=True, widget=forms.TextInput(attrs={"class": "form-control"}))
	expertise_area = forms.CharField(max_length=250, required=True, widget=forms.TextInput(attrs={"class": "form-control"}))
	market_sector_focus = forms.CharField(max_length=250, required=False, widget=forms.TextInput(attrs={"class": "form-control"}))
	years_of_experience=forms.IntegerField( required=True, widget=forms.NumberInput(attrs={"class": "form-control"}))

	contact_phone = forms.CharField(max_length=250, required=True, widget=forms.TextInput(attrs={"class": "form-control"}))
	contact_email = forms.EmailField(required=True, widget=forms.TextInput(attrs={"type": "email","class": "form-control"}))
	address = forms.CharField( required=True, widget=forms.Textarea(attrs={"class": "form-control"}))
	has_ndasigned = forms.BooleanField(required=False,widget=forms.CheckboxInput(attrs={"class": "form-check-input"}))
	available_for_assignment = forms.BooleanField(required=False,widget=forms.CheckboxInput(attrs={"class": "form-check-input"}))
	def __init__(self, *args, **kwargs):
		user_choices_list = kwargs.pop('user_choices', [])
		initial_data = kwargs.get("initial", {})
		selected_user_choices = initial_data.get('user', '')
		super().__init__(*args, **kwargs)
		self.fields['user'].choices = [('', '---select---')] + [
			(
				record.get('id', ''),  
				f"{record['user'].get('name', '')} ({record['user'].get('roles', '')})"
			)
			for record in user_choices_list
		]
		if selected_user_choices:
			self.fields['user'].initial = selected_user_choices


class IssueReportForm(forms.Form):
	staff = forms.ChoiceField(required=True, widget=forms.Select(attrs={"class": "form-control"}))
	description = forms.CharField(required=False, widget=forms.Textarea(attrs={"class": "form-control"}))
	screen_name = forms.CharField(max_length=250, required=False, widget=forms.TextInput(attrs={"class": "form-control"}))
	filename = forms.CharField(max_length=250, required=False, widget=forms.TextInput(attrs={"class": "form-control"}))
	file_type = forms.CharField(max_length=250, required=False, widget=forms.TextInput(attrs={"class": "form-control"}))
	def __init__(self, *args, **kwargs):
		user_choices_list = kwargs.pop('user_choices', [])
		initial_data = kwargs.get("initial", {})
		selected_user_choices = initial_data.get('staff', '')
		super().__init__(*args, **kwargs)
		self.fields['staff'].choices = [('', '---select---')] + [(record.get('id', ''), record.get('first_name', '')) for record in user_choices_list]
		if selected_user_choices:
			self.fields['staff'].initial = selected_user_choices

class NotificationForm(forms.Form):
	name = forms.CharField(max_length=250, required=True, widget=forms.TextInput(attrs={"class": "form-control"}))
	msg = forms.CharField(max_length=250, required=True, widget=forms.TextInput(attrs={"class": "form-control"}))
	

class LawyerProfileForm(forms.Form):
	user = forms.ChoiceField(required=True, widget=forms.Select(attrs={"class": "form-control"}))
	law_firm = forms.CharField(max_length=250, required=True, widget=forms.TextInput(attrs={"class": "form-control"}))
	bar_registration_number = forms.CharField(max_length=250, required=True, widget=forms.TextInput(attrs={"class": "form-control"}))
	specialization_area = forms.CharField(max_length=250, required=True, widget=forms.TextInput(attrs={"class": "form-control"}))
	specialization_area = forms.CharField(max_length=250, required=True, widget=forms.TextInput(attrs={"class": "form-control"}))
	qualifications = forms.CharField(required=False, widget=forms.Textarea(attrs={"class": "form-control"}))
	years_of_practice=forms.IntegerField( required=True, widget=forms.NumberInput(attrs={"class": "form-control"}))
	contact_phone = forms.CharField(max_length=250, required=True, widget=forms.TextInput(attrs={"class": "form-control"}))
	contact_email = forms.EmailField(required=True, widget=forms.TextInput(attrs={"type": "email","class": "form-control"}))
	address = forms.CharField( required=True, widget=forms.Textarea(attrs={"class": "form-control"}))
	licensed = forms.BooleanField(required=False,widget=forms.CheckboxInput(attrs={"class": "form-check-input"}))
	nda_signed = forms.BooleanField(required=False,widget=forms.CheckboxInput(attrs={"class": "form-check-input"}))
	active = forms.BooleanField(required=False,widget=forms.CheckboxInput(attrs={"class": "form-check-input"}))
	def __init__(self, *args, **kwargs):
		user_choices_list = kwargs.pop('user_choices', [])
		initial_data = kwargs.get("initial", {})
		selected_user_choices = initial_data.get('user', '')
		super().__init__(*args, **kwargs)
		self.fields['user'].choices = [('', '---select---')] + [
			(
				record.get('id', ''),  # Lawyer ID, not User ID
				f"{record['user'].get('name', '')} ({record['user'].get('roles', '')})"
			)
			for record in user_choices_list
		]

				
		if selected_user_choices:
			self.fields['user'].initial = selected_user_choices

class MembersForm(forms.Form):
	email = forms.EmailField(required=True, widget=forms.TextInput(attrs={"type": "email","class": "form-control"}))
	password = forms.CharField(max_length=250, required=True, widget=forms.TextInput(attrs={"class": "form-control"}))
	otp = forms.CharField(max_length=250, required=True, widget=forms.TextInput(attrs={"class": "form-control"}))


class EventsForm(forms.Form):
	title = forms.CharField(max_length=250, required=True, widget=forms.TextInput(attrs={"class": "form-control"}))
	date = forms.DateField(input_formats=['%Y-%m-%d'],required=True, widget=forms.DateInput(attrs={"type": "date","class": "form-control"}))
	time =  forms.TimeField(input_formats=["%H:%M:%S"],required=True, widget=forms.TimeInput(attrs={"class": "your-time-input-class form-control"}))
	purpose = forms.CharField(required=False, widget=forms.Textarea(attrs={"class": "form-control"}))
	notes = forms.CharField(required=False, widget=forms.Textarea(attrs={"class": "form-control"}))
	venue = forms.CharField(max_length=250, required=False, widget=forms.TextInput(attrs={"class": "form-control"}))
	filename = forms.CharField(max_length=250, required=False, widget=forms.TextInput(attrs={"class": "form-control"}))
	file_type = forms.CharField(max_length=250, required=False, widget=forms.TextInput(attrs={"class": "form-control"}))


class StaffFeedbackForm(forms.Form):
	staff = forms.ChoiceField(required=True, widget=forms.Select(attrs={"class": "form-control"}))
	feedback = forms.CharField( required=True, widget=forms.Textarea(attrs={"class": "form-control"}))
	feedback = forms.CharField( required=True, widget=forms.Textarea(attrs={"class": "form-control"}))
	rating=forms.IntegerField( required=True, widget=forms.NumberInput(attrs={"class": "form-control"}))
	filename = forms.CharField(max_length=250, required=False, widget=forms.TextInput(attrs={"class": "form-control"}))
	file_type = forms.CharField(max_length=250, required=False, widget=forms.TextInput(attrs={"class": "form-control"}))
	def __init__(self, *args, **kwargs):
		user_choices_list = kwargs.pop('user_choices', [])
		initial_data = kwargs.get("initial", {})
		selected_user_choices = initial_data.get('staff', '')
		super().__init__(*args, **kwargs)
		self.fields['staff'].choices = [('', '---select---')] + [(record.get('id', ''), record.get('first_name', '')) for record in user_choices_list]
		if selected_user_choices:
			self.fields['staff'].initial = selected_user_choices


class TaskAssignmentForm(forms.Form):
	issue = forms.ChoiceField(required=True, widget=forms.Select(attrs={"class": "form-control"}))
	assigned_to = forms.ChoiceField(required=True, widget=forms.Select(attrs={"class": "form-control"}))
	due_date = forms.DateField(input_formats=['%Y-%m-%d'],required=False, widget=forms.DateInput(attrs={"type": "date","class": "form-control"}))
	notes = forms.CharField(required=False, widget=forms.Textarea(attrs={"class": "form-control"}))
	def __init__(self, *args, **kwargs):
		user_choices_list = kwargs.pop('user_choices', [])
		issue_choices_list = kwargs.pop('issue_choices', [])
		initial_data = kwargs.get("initial", {})
		selected_assigned_to_choices = initial_data.get('assigned_to', '')
		selected_issue_choices = initial_data.get('issue', '')
		super().__init__(*args, **kwargs)
		self.fields['assigned_to'].choices = [('', '---select---')] + [(record.get('id', ''), record.get('first_name', '')) for record in user_choices_list]
		self.fields['issue'].choices = [('', '---select---')] + [(record.get('id', ''), record.get('first_name', '')) for record in issue_choices_list]
		if selected_assigned_to_choices:
			self.fields['assigned_to'].initial = selected_assigned_to_choices
		if selected_issue_choices:
			self.fields['assigned_to'].initial = selected_issue_choices


class TimesheetRepotForm(forms.Form):
	date = forms.DateField(input_formats=['%Y-%m-%d'],required=False, widget=forms.DateInput(attrs={"type": "date","class": "form-control"}))
	status = forms.ChoiceField(choices=[('pending','pending'),('completed','completed'),('approved','approved'),('rejected','rejected')], required=False, widget=forms.Select(attrs={"class": "form-control"}))



class LoanCaseRepotForm(forms.Form):
	date = forms.DateField(input_formats=['%Y-%m-%d'],required=False, widget=forms.DateInput(attrs={"type": "date","class": "form-control"}))
