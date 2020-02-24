from django.urls import path

from calls.views import (
    CallsListView,
    CallRegisterView,
    CallComplainsApi,
    CallDetailView,
    CallAllocateView,
    CallEditView
)

app_name    = 'calls'
urlpatterns = [
    path('',CallsListView.as_view(), name='calls_list_view'),
    path('register/',CallRegisterView.as_view(), name='call_register_view'),
    path('complain_api/',CallComplainsApi.as_view(), name='call_complain_api'),
    path('<int:id>/',CallDetailView.as_view(), name='call_detail_view'),
    path('allocate/',CallAllocateView.as_view(), name='call_allocate_view'),
    path('edit/<int:id>/',CallEditView.as_view(), name='call_edit_view'),
]
