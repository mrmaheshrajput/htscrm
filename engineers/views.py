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
            messages.add_message(request, messages.INFO, 'success')
            return redirect('engineers:engineer_view')
        messages.add_message(request, messages.INFO, 'fail')
        return redirect('engineers:engineer_view')

    def get(self, request):
        queryset        = Engineer.objects.all()
        print(messages)
        context         = {
            "objects"   : queryset
        }
        return render(request, self.template_name, context)


class EngineerDeleteView(LoginRequiredMixin, View):
    template_name       = 'engineers/engineer_view.html'

    def post(self, request, id):
        if id:
            try:
                instance    = Engineer.objects.get(pk=id)
            except Engineer.DoesNotExist:
                instance    = None
            if instance:
                instance.delete()
                messages.add_message(request, messages.INFO, 'success')
                return redirect('engineers:engineer_view')
        messages.add_message(request, messages.INFO, 'fail')
        return redirect('engineers:engineer_view')
