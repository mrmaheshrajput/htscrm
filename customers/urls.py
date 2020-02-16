from django.urls import path

from customers.views import CustomerCreateView, CustomerDetailView

app_name    = 'customers'
urlpatterns = [
    path('' ,CustomerDetailView.as_view(), name='customer_detail_view'),
    path('create/' ,CustomerCreateView.as_view(), name='customer_create_view'),
]
