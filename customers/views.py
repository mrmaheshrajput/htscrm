from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import View

from customers.models import ClientDetails
from customers.forms import ClientForm

class CustomerCreateView(LoginRequiredMixin, View):
    template_name           = 'customers/customer_create_view.html'

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        form                = ClientForm(request.POST or None)
        if form.is_valid():
            instance            = form.save(commit=False)
            instance.created_by = self.request.user
            instance.save()
            messages.add_message(request, messages.INFO, 'success')
            return redirect('customers:customer_detail_view')
        return render(request, self.template_name, {'error': 'Please provide valid details'})


class CustomerDetailView(LoginRequiredMixin, View):
    template_name           = 'customers/customer_detail_view.html'

    def get(self, request):
        queryset            = ClientDetails.objects.all()
        context             = {
            "objects"       : queryset
        }
        return render(request, self.template_name, context)
