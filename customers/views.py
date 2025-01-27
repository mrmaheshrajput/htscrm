import datetime
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core import serializers
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import View
from django.urls import reverse

from calls.models import CallRegister
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
        next                = request.POST['next']
        if next == reverse('customers:customer_create_view'):
            next            = None
        if not next:
            next            = reverse('customers:customer_list_view')
        if form.is_valid():
            instance            = form.save(commit=False)
            instance.created_by = self.request.user
            instance.save()
            messages.add_message(request, messages.INFO, 'Success - Customer added successfully!')
            return redirect(next)
        messages.add_message(request, messages.INFO, 'Failed - Invalid details')
        return redirect(next)


class CustomerListView(LoginRequiredMixin, JSONResponseMixin, View):
    template_name           = 'customers/customer_list_view.html'

    def get(self, request):
        queryset            = ClientDetails.objects.all().order_by('-timestamp')
        for i in queryset:
            j = i.call_of.only('pk')
            counter = 0
            if j:
                counter += len(j)
                for k in j:
                    l = k.mother_call_id.filter(call_id=k.pk).only('call_visit_final_notes')
                    for m in l:
                        if m:
                            if m.call_status_final == False:
                                counter -= 1
                i.pending_call = counter
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


class CustomerListApi(LoginRequiredMixin, JSONResponseMixin, View):
    def get(self, request):
        data                = serializers.serialize('json', ClientDetails.objects.all(), fields=('name'))
        return HttpResponse(data)


class CustomerDeleteView(LoginRequiredMixin, View):
    template_name       = 'customers/customer_list_view.html'

    def post(self, request):
        try:
            instance    = ClientDetails.objects.get(pk=request.POST['customer-id'])
        except ClientDetails.DoesNotExist:
            instance    = None
        if instance:
            instance.delete()
            messages.add_message(request, messages.INFO, 'Success - Customer deleted')
            return redirect('customers:customer_list_view')
        messages.add_message(request, messages.INFO, 'Failed - Details provided are invalid!')
        return redirect('customers:customer_list_view')


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
        return redirect('customers:customer_list_view')

    def post(self, request, id):
        form                = ClientForm(request.POST or None)
        if form.is_valid():
            ClientDetails.objects.filter(pk=id).update(
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
            messages.add_message(request, messages.INFO, 'Success - Customer edited successfully')
            return redirect('customers:customer_list_view')
        messages.add_message(request, messages.INFO, 'Failed - Invalid details!')
        return redirect('customers:customer_list_view')


class CustomerDetailView(LoginRequiredMixin, View):
    template_name                    = 'customers/customer_detail_view.html'

    def get(self, request, id):
        id_                         = id or None
        customer                    = get_object_or_404(ClientDetails, pk=id_)
        queryset                    = CallRegister.objects.filter(customer=id_)
        context                     = {
            'objects'               : queryset,
            'customer'              : customer
        }
        return render(request, self.template_name, context)
