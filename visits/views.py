import datetime
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core import serializers
from django.http import HttpResponse, JsonResponse, Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import View, ListView
from django.urls import reverse

from calls.models import CallRegister, CallAllocation
from visits.models import CallVisit
from visits.forms import CallVisitForm


class VisitListView(LoginRequiredMixin, ListView):
    template_name                   = 'visits/visit_list_view.html'
    queryset                        = CallVisit.objects.all().order_by('-timestamp')


class VisitCreateView(LoginRequiredMixin, View):
    template_name                   = 'visits/visit_create_view.html'

    def get(self, request, id):
        """
        Checks passed call id with call allocation modal, if call
        found in call allocation i.e. call is allocated then it is
        passed as object to be returned in post request.
        Returns visit create template.
        """
        object                      = CallAllocation.objects.filter(call=id).order_by('-timestamp').first()
        if not object:
            raise Http404
        form                        = CallVisitForm()
        context                     = {
            'form'                  : form,
            'object'                : object
        }
        return render(request, self.template_name, context)

    def post(self, request, id):
        """
        Saves new call visit by taking call allocation id which
        was passed in object in get request.
        Mind call_status is modified to put in call_status
        """
        form                        = CallVisitForm(request.POST or None)
        if form.is_valid():
            instance                = form.save(commit=False)
            object                  = get_object_or_404(CallAllocation, pk=id)
            instance.callallocation_id = object
            instance.call_id        = object.call
            if request.POST['call_status'] == 'Closed':
                instance.call_status_final = False
            else:
                instance.call_status_final = True
            instance.added_by       = self.request.user
            instance.save()
            CallAllocation.objects.filter(pk=id).update(status = 'C')
            messages.add_message(request, messages.INFO, 'Success - Call visit added successfully!')
            return redirect(reverse('visits:visit_list_view'))
        messages.add_message(request, messages.INFO, 'Failed - Invalid details')
        return redirect(reverse('visits:visit_list_view'))


class VisitDetailView(LoginRequiredMixin, View):
    template_name                   = 'visits/visit_detail_view.html'

    def get(self, request, id):
        queryset                    = get_object_or_404(CallVisit, pk=id)
        return render(request, self.template_name, {'object' : queryset})
