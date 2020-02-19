from django.urls import path

from engineers.views import EngineerView, EngineerDeleteView, EngineerEditView

app_name    = 'engineers'
urlpatterns = [
    path('',EngineerView.as_view(), name='engineer_view'),
    path('delete/',EngineerDeleteView.as_view(), name='engineer_delete_view'),
    path('edit/', EngineerEditView.as_view(), name='engineer_edit_view'),
]
