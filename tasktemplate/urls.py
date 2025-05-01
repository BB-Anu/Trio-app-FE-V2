from django.urls import path
from .views import *

urlpatterns = [
  path('create_template/', create_template_view, name='create_template'),
    path('templates/', template_list_view, name='template_list'),
    path('templates_delete/<pk>/', template_delete, name='templates_delete'),
    path('templates_edit/<pk>/', template_edit, name='templates_edit'),
    path('fill-and-save-template/<int:pk>/', fill_and_save_template_view, name='fill_and_save_template'),
 path('document-detail/<int:pk>/', document_detail_view, name='document_detail'),   
]
