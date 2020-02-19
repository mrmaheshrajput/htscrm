import datetime

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, render, redirect
from django.views.generic import View

from engineers.forms import EngineerAddForm
from engineers.models import Engineer

class EngineerView(LoginRequiredMixin, View):
    template_name = 'engineers/engineer_view.html'

    def post(self, request):
        form            = EngineerAddForm(request.POST or None)
        if form.is_valid():
            instance    = form.save(commit=False)
            instance.added_by = self.request.user
            instance.save()
            messages.add_message(request, messages.INFO, 'Success - Engineer added successfully')
            return redirect('engineers:engineer_view')
        messages.add_message(request, messages.INFO, 'Failed - Invalid details!')
        return redirect('engineers:engineer_view')

    def get(self, request):
        queryset        = Engineer.objects.all()
        context         = {
            "objects"   : queryset
        }
        return render(request, self.template_name, context)


class EngineerDeleteView(LoginRequiredMixin, View):
    template_name       = 'engineers/engineer_view.html'

    def post(self, request):
        try:
            instance    = Engineer.objects.get(pk=request.POST['engineer-id'])
        except Engineer.DoesNotExist:
            instance    = None
        if instance:
            instance.delete()
            messages.add_message(request, messages.INFO, 'Success - Engineer deleted')
            return redirect('engineers:engineer_view')
        messages.add_message(request, messages.INFO, 'Failed - Details provided are invalid!')
        return redirect('engineers:engineer_view')


class EngineerEditView(LoginRequiredMixin, View):
    template_name           = 'engineers/engineer_edit.html'

    # def get(self, request, id):
    #     if id:
    #         try:
    #             instance    = Engineer.objects.get(pk=id)
    #         except Engineer.DoesNotExist:
    #             instance    = None
    #         if instance:
    #             form        = EngineerAddForm(initial=
    #                                 {'engineer_name': instance.engineer_name,
    #                                 'mobile'        : instance.mobile
    #                                 }
    #                             )
    #             return render(request, self.template_name, {"form": form})
    #     messages.add_message(request, messages.INFO, 'fail')
    #     return redirect('engineers:engineer_view')

    def post(self, request):
        form                = EngineerAddForm(request.POST or None)
        if form.is_valid():
            id              = request.POST['eng-id']
            r = Engineer.objects.filter(pk=id).update(
                        engineer_name   =request.POST['engineer_name'],
                        mobile          =request.POST['mobile'],
                        edited_by       =self.request.user,
                        edit_datetime   =datetime.datetime.now()
                        )
            print(r)
            messages.add_message(request, messages.INFO, 'Success - Engineer edited successfully')
            return redirect('engineers:engineer_view')
        messages.add_message(request, messages.INFO, 'Failed - Invalid details!')
        return redirect('engineers:engineer_view')
