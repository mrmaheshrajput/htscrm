import datetime
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core import serializers
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import View

from calls.models import CallRegister, CallAllocation
from calls.forms import CallRegisterForm
from customers.models import ClientDetails
from engineers.models import Engineer

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


class CallsListView(LoginRequiredMixin, View):
    template_name                   = 'calls/calls_list_view.html'

    def get(self, request):
        queryset                    = CallRegister.objects.all()

        # Reverse foreign key lookup for engineer assigned
        # and append to queryset
        for i in queryset:
            j = i.parent_call.filter(call=i.pk).order_by('-timestamp').first()
            if j:
                i.engineer_assigned = j.engineer_assigned

        engineers                   = Engineer.objects.all()
        context                     = {
            'objects'               : queryset,
            'engineers'             : engineers
        }

        return render(request, self.template_name, context)

class CallComplainsApi(LoginRequiredMixin, View):
    def get(self, request):
        data                = serializers.serialize('json', CallRegister.objects.all().distinct('complaint_nature'), fields=('complaint_nature'))
        return HttpResponse(data)

class CallRegisterView(LoginRequiredMixin, View):
    template_name                   = 'calls/call_create_view.html'

    def get(self, request):
        form                        = CallRegisterForm()
        return render(request, self.template_name, {'form':form})

    def post(self, request):
        form                        = CallRegisterForm(request.POST or None)
        if form.is_valid():
            instance                = form.save(commit=False)
            instance.customer       = ClientDetails.objects.get(name=request.POST['customer'])
            instance.added_by       = self.request.user
            instance.save()
            messages.add_message(request, messages.INFO, 'Success - Call added successfully!')
            return redirect('calls:calls_list_view')
        messages.add_message(request, messages.INFO, 'Failed - Invalid details')
        return render(request, self.template_name)


class CallDetailView(LoginRequiredMixin, View):
    template_name                   = 'calls/call_detail_view.html'

    def get(self, request, id):
        queryset                    = CallRegister.objects.get(pk=id)
        call_allocations            = CallAllocation.objects.filter(call=queryset).order_by('-timestamp')
        engineers                   = Engineer.objects.all()
        context                     = {
            'object'                : queryset,
            'call_allocations'      : call_allocations,
            'engineers'             : engineers
        }
        return render(request, self.template_name, context)


class CallAllocateView(LoginRequiredMixin, View):

    def post(self, request):
        call_id                     = request.POST['call-id']
        engineer_id                 = request.POST['engineer-id']
        next                        = request.POST['next']
        if not next:
            next                    = reverse('calls:calls_list_view')
        if not call_id or not engineer_id:
            messages.add_message(request, messages.INFO, 'Failed - Invalid details')
            return redirect(next)
        CallAllocation.objects.filter(
            call=CallRegister.objects.get(pk=call_id)
            ).update(status='E')
        CallAllocation.objects.create(
                call                = CallRegister.objects.get(pk=call_id),
                engineer_assigned   = Engineer.objects.get(pk=engineer_id),
                added_by            = self.request.user
        )
        messages.add_message(request, messages.INFO, 'Success - Call allocated successfully!')
        return redirect(next)


class CallEditView(LoginRequiredMixin, View):
    template_name                   = 'calls/call_edit_view.html'

    def get(self, request, id):
        object                      = CallRegister.objects.get(pk=id)
        form                        = CallRegisterForm(instance=object)
        context                     = {
            'object'                : object,
            'form'                  : form
        }
        return render(request, self.template_name, context)
