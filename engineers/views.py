import datetime

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, render, redirect
from django.views.generic import View

from engineers.forms import EngineerAddForm
from engineers.models import Engineer

from calls.models import CallAllocation

class EngineerView(LoginRequiredMixin, View):
    template_name           = 'engineers/engineer_list_view.html'

    def post(self, request):
        """
        Adds new engineer from engineer_list_view page modal
        """
        form                = EngineerAddForm(request.POST or None)
        if form.is_valid():
            instance        = form.save(commit=False)
            instance.added_by = self.request.user
            instance.save()
            messages.add_message(request, messages.INFO, 'Success - Engineer added successfully')
            return redirect('engineers:engineer_view')
        messages.add_message(request, messages.INFO, 'Failed - Invalid details!')
        return redirect('engineers:engineer_view')

    def get(self, request):
        """
        Returns list of all engineers
        """
        queryset            = Engineer.objects.all()
        context             = {
            "objects"   : queryset
        }
        return render(request, self.template_name, context)


class EngineerDeleteView(LoginRequiredMixin, View):
    template_name           = 'engineers/engineer_list_view.html'

    def post(self, request):
        """
        Delete engineer through modal form
        """
        try:
            instance        = Engineer.objects.get(pk=request.POST['engineer-id'])
        except Engineer.DoesNotExist:
            instance        = None
        if instance:
            instance.delete()
            messages.add_message(request, messages.INFO, 'Success - Engineer deleted')
            return redirect('engineers:engineer_view')
        messages.add_message(request, messages.INFO, 'Failed - Details provided are invalid!')
        return redirect('engineers:engineer_view')


class EngineerEditView(LoginRequiredMixin, View):
    template_name           = 'engineers/engineer_edit_view.html'

    def post(self, request):
        """
        Edits engineer by updating all existing details from
        engineer_list_view page modal
        """
        form                = EngineerAddForm(request.POST or None)
        if form.is_valid():
            id              = request.POST['eng-id']
            r = Engineer.objects.filter(pk=id).update(
                        engineer_name   =request.POST['engineer_name'],
                        mobile          =request.POST['mobile'],
                        edited_by       =self.request.user,
                        edit_datetime   =datetime.datetime.now()
                        )
            if not r:
                messages.add_message(request, messages.INFO, 'Failed - Invalid details!', fail_silently=True)
                return redirect('engineers:engineer_view')
            messages.add_message(request, messages.INFO, 'Success - Engineer edited successfully', fail_silently=True)
            return redirect('engineers:engineer_view')
        messages.add_message(request, messages.INFO, 'Failed - Invalid details!', fail_silently=True)
        return redirect('engineers:engineer_view')


class EngineerDetailView(LoginRequiredMixin, View):
    template_name           = 'engineers/engineer_detail_view.html'

    def get(self, request, id):
        """
        Returns specific engineer, allocated calls and visits
        """
        id_                 = id or None
        queryset            = CallAllocation.objects.filter(engineer_assigned=id_)
        return render(request, self.template_name, {'objects': queryset})
