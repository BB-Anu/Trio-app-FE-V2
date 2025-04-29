from django.urls import path
from .views import *

urlpatterns = [
  path('create_template/', create_template_view, name='create_template'),
    path('templates/', template_list_view, name='template_list'),
    path('fill-and-save-template/<int:pk>/', fill_and_save_template_view, name='fill_and_save_template'),
 path('document-detail/<int:pk>/', document_detail_view, name='document_detail'),   
]
