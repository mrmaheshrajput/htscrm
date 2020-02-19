import datetime
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import View

from customers.models import ClientDetails
from customers.forms import ClientForm

class JSONResponseMixin:

    def render_to_json_response(self, context, **response_kwargs):
        """
        Returns a JSON Response, transferring 'context' to make the payload.
        """
        return JsonResponse(
            self.get_data(context),
            **response_kwargs
        )

    def get_data(self, context):
        """
        Return an object that will be serialized as JSON by json.dumps().
        """
        # Things to do
        return context

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
            messages.add_message(request, messages.INFO, 'Success - Customer added successfully!')
            return redirect('customers:customer_detail_view')
        messages.add_message(request, messages.INFO, 'Failed - Invalid details')
        return render(request, self.template_name)


class CustomerDetailView(LoginRequiredMixin, JSONResponseMixin, View):
    template_name           = 'customers/customer_detail_view.html'

    def get(self, request):
        queryset            = ClientDetails.objects.all()
        context             = {
            "objects"       : queryset
        }
        return render(request, self.template_name, context)

    def post(self, request):
        object              = ClientDetails.objects.get(pk=request.POST["id"])
        if not object:
            messages.add_message(request, messages.INFO, 'Failed - Invalid details')
            return render(request, self.template_name)
        queryset            = {
            "name"              : object.name,
            "calling_number"    : object.calling_number,
            "contact_number"    : object.contact_number,
            "address"           : object.address,
            "city"              : object.city,
            "state"             : object.state,
            "pin"               : object.pin
        }
        context             = {
            "object"        : queryset
        }
        return self.render_to_json_response(context)


class CustomerDeleteView(LoginRequiredMixin, View):
    template_name       = 'customers/customer_detail_view.html'

    def post(self, request):
        try:
            instance    = ClientDetails.objects.get(pk=request.POST['customer-id'])
        except ClientDetails.DoesNotExist:
            instance    = None
        if instance:
            instance.delete()
            messages.add_message(request, messages.INFO, 'Success - Customer deleted')
            return redirect('customers:customer_detail_view')
        messages.add_message(request, messages.INFO, 'Failed - Details provided are invalid!')
        return redirect('customers:customer_detail_view')


class CustomerEditView(LoginRequiredMixin, View):
    template_name       = 'customers/customer_edit_view.html'

    def get(self, request, id):
        try:
            object          = ClientDetails.objects.get(pk=id)
        except ClientDetails.DoesNotExist:
            object          = None
        if object:
            context         = {
                "object"    : object
            }
            return render(request, self.template_name, context)
        messages.add_message(request, messages.INFO, 'Failed - Invalid data!')
        return redirect('customers:customer_detail_view')

    def post(self, request, id):
        form                = ClientForm(request.POST or None)
        if form.is_valid():
            r = ClientDetails.objects.filter(pk=id).update(
                        name                = request.POST['name'],
                        contact_number      = request.POST['contact_number'],
                        calling_number      = request.POST['calling_number'],
                        address             = request.POST['address'],
                        city                = request.POST['city'],
                        state               = request.POST['state'],
                        pin                 = request.POST['pin'],
                        edited_by           = self.request.user,
                        edit_datetime       = datetime.datetime.now()
                        )
            print(r)
            messages.add_message(request, messages.INFO, 'Success - Customer edited successfully')
            return redirect('customers:customer_detail_view')
        messages.add_message(request, messages.INFO, 'Failed - Invalid details!')
        return redirect('customers:customer_detail_view')
