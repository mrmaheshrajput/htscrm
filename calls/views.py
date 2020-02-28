import datetime
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core import serializers
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import View
from django.urls import reverse

from calls.models import CallRegister, CallAllocation
from calls.forms import CallRegisterForm
from customers.models import ClientDetails
from engineers.models import Engineer
from visits.models import CallVisit

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
        """
        Returns all calls list with related allocated engineer
        and returns all engineers too.
        """
        queryset                    = CallRegister.objects.all().order_by('-timestamp')

        # Reverse foreign key lookup for: engineer allocated,
        # engineer allocated status updated by visit_create_view,
        # call visit status from CallVisit modal
        # and appending to queryset
        for i in queryset:
            j = i.parent_call.filter(call=i.pk).order_by('-timestamp').first()
            if j:
                # Adding engineer assigned from enginner table
                i.engineer_assigned = j.engineer_assigned
                # Adding visit status from CallAllocation table
                i.visit_status      = j.get_status_display
                # # Adding relevant CallVisit object if visit done
                # i.call_status       = j.mother_call_id.filter(
                #                         call_id=k.pk
                #                         ).order_by('-timestamp').first()
        for k in queryset:
            l = k.mother_call_id.filter(call_id=k.pk).order_by('-timestamp').first()
            if l:
                k.call_status       = l

        engineers                   = Engineer.objects.all()
        context                     = {
            'objects'               : queryset,
            'engineers'             : engineers
        }

        return render(request, self.template_name, context)


class CallComplainsApi(LoginRequiredMixin, View):

    def get(self, request):
        """
        API to get unique complaint_nature from db for call regiser / call edit
        """
        data                = serializers.serialize('json', CallRegister.objects.all().distinct('complaint_nature'), fields=('complaint_nature'))
        return HttpResponse(data)


class CallRegisterView(LoginRequiredMixin, View):
    template_name                   = 'calls/call_create_view.html'

    def get(self, request):
        """
        Returns call register form from forms.py
        """
        form                        = CallRegisterForm()
        return render(request, self.template_name, {'form':form})

    def post(self, request):
        """
        Registers new call after finding customer by name (to change to id)
        """
        form                        = CallRegisterForm(request.POST or None)
        if form.is_valid():
            instance                = form.save(commit=False)
            # Getting only ONE customer from db
            # that matches passed name
            # MUST BE CHANGED
            instance.customer       = ClientDetails.objects.filter(name=request.POST['customer']).first()
            instance.added_by       = self.request.user
            instance.save()
            messages.add_message(request, messages.INFO, 'Success - Call added successfully!')
            return redirect('calls:calls_list_view')
        messages.add_message(request, messages.INFO, 'Failed - Invalid details')
        return render(request, self.template_name)


class CallDetailView(LoginRequiredMixin, View):
    template_name                   = 'calls/call_detail_view.html'

    def get(self, request, id):
        """
        Returns single call details, its all allocations with
        related visits and all enginners list
        """
        queryset                    = get_object_or_404(CallRegister, pk=id)
        call_allocations            = CallAllocation.objects.filter(call=queryset).order_by('-timestamp')
        if call_allocations:
            call_visits             = CallVisit.objects.filter(call_id=call_allocations[0].call.pk).order_by('-timestamp')
        else:
            call_visits             = None
        engineers                   = Engineer.objects.all()
        context                     = {
            'object'                : queryset,
            'call_allocations'      : call_allocations,
            'engineers'             : engineers,
            'call_visits'           : call_visits
        }
        return render(request, self.template_name, context)


class CallAllocateView(LoginRequiredMixin, View):

    def post(self, request):
        """
        Allocates new enginner against a call after all previous allocated
        engineers are marked expired.
        Data is received through form, which is at two places in app.
        """
        call_id                     = request.POST['call-id']
        engineer_id                 = request.POST['engineer-id']
        next                        = request.POST['next']
        if not next:
            next                    = reverse('calls:calls_list_view')
        if not call_id or not engineer_id:
            messages.add_message(request, messages.INFO, 'Failed - Invalid details')
            return redirect(next)
        CallAllocation.objects.filter(
            call=get_object_or_404(CallRegister, pk=call_id)
            ).filter(status='P').update(status='E')
        CallAllocation.objects.create(
                call                = get_object_or_404(CallRegister, pk=call_id),
                engineer_assigned   = get_object_or_404(Engineer, pk=engineer_id),
                added_by            = self.request.user
        )
        messages.add_message(request, messages.INFO, 'Success - Call allocated successfully!')
        return redirect(next)


class CallEditView(LoginRequiredMixin, View):
    template_name                   = 'calls/call_edit_view.html'

    def get(self, request, id):
        """
        Returns single call data from db, appointment_date is passed into
        form to display as form only.
        """
        object                      = get_object_or_404(CallRegister, pk=id)
        form                        = CallRegisterForm(instance=object)
        context                     = {
            'object'                : object,
            'form'                  : form
        }
        return render(request, self.template_name, context)

    def post(self, request, id):
        """
        Overrides all existing details of specific call, similar to
        call register.
        """
        form                        = CallRegisterForm(request.POST or None)
        if form.is_valid():
            object                  = get_object_or_404(CallRegister, pk=id)
            # Getting only ONE customer from db
            # that matches passed name
            # MUST BE CHANGED
            CallRegister.objects.filter(pk=id).update(
                customer            = ClientDetails.objects.filter(name=request.POST['customer']).first(),
                complaint_nature    = form.cleaned_data['complaint_nature'],
                brand               = form.cleaned_data['brand'],
                product_name        = form.cleaned_data['product_name'],
                product_serial      = form.cleaned_data['product_serial'],
                product_coverage    = form.cleaned_data['product_coverage'],
                appointment_date    = form.cleaned_data['appointment_date'],
                appointment_time    = form.cleaned_data['appointment_time'],
                edited_by           = self.request.user,
                edit_datetime       = datetime.datetime.now()
                )
            messages.add_message(request, messages.INFO, 'Success - Call detials edited successfully!')
            return redirect(reverse('calls:call_detail_view', kwargs={'id':id}))
        messages.add_message(request, messages.INFO, 'Failed - Invalid details')
        return redirect(reverse('calls:call_edit_view', kwargs={'id':id}))
