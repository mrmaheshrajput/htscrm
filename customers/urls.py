from django.urls import path

from customers.views import (
    CustomerCreateView,
    CustomerListView,
    CustomerDeleteView,
    CustomerEditView,
    CustomerListApi,
    CustomerDetailView
    )

app_name    = 'customers'
urlpatterns = [
    path('' ,CustomerListView.as_view(), name='customer_list_view'),
    path('create/' ,CustomerCreateView.as_view(), name='customer_create_view'),
    path('delete/',CustomerDeleteView.as_view(), name='customer_delete_view'),
    path('edit/<int:id>/',CustomerEditView.as_view(), name='customer_edit_view'),
    path('list_api/',CustomerListApi.as_view(), name='customer_list_api'),
    path('view/<int:id>/', CustomerDetailView.as_view(), name='customer_detail_view'),
]
