import datetime
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core import serializers
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import View, ListView
from django.urls import reverse

from calls.models import CallAllocation
from visits.models import CallVisit
from visits.forms import CallVisitForm


class VisitListView(LoginRequiredMixin, ListView):
    template_name                   = 'visits/visit_list_view.html'
    queryset                        = CallVisit.objects.all()


class VisitCreateView(LoginRequiredMixin, View):
    template_name                   = 'visits/visit_create_view.html'

    def get(self, request, id):
        """
        Returns list of all allocated calls
        """
        # r = CallAllocation.objects.get(pk=id)
        # k = r.call_allocation_id.filter(call_status_final=True)
        # print(k)
        object                      = get_object_or_404(CallAllocation,pk=id)
        form                        = CallVisitForm(instance=object)
        print(form.instance.engineer_assigned)
        context                     = {
            'form'                  : form,
            'object'                : object
        }
        return render(request, self.template_name, context)

    def post(self, request, id):
        """
        Saves new call visit by taking call allocation id from url
        """
        form                        = CallVisitForm(request.POST or None)
        if form.is_valid():
            print(form.cleaned_data)
            instance                = form.save(commit=False)
            object                  = get_object_or_404(CallAllocation, pk=id)
            instance.callallocation_id = object
            if request.POST['call_status'] == 'Closed':
                instance.call_status_final = False
            else:
                instance.call_status_final = True
            instance.added_by       = self.request.user
            instance.save()
            CallAllocation.objects.filter(pk=id).update(status = 'C')
            messages.add_message(request, messages.INFO, 'Success - Call visit added successfully!')
            return redirect('visits:visit_list_view')
        messages.add_message(request, messages.INFO, 'Failed - Invalid details')
        return redirect(reverse('visits:visit_create_view', kwargs={'id':id}))


class VisitDetailView(LoginRequiredMixin, View):
    template_name                   = 'visits/visit_detail_view.html'

    def get(self, request, id):
        queryset                    = get_object_or_404(CallVisit, pk=id)
        return render(request, self.template_name, {'object' : queryset})
