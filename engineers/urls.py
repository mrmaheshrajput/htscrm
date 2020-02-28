from django.urls import path

from engineers.views import (
    EngineerView,
    EngineerDeleteView,
    EngineerEditView,
    EngineerDetailView
    )

app_name    = 'engineers'
urlpatterns = [
    path('',EngineerView.as_view(), name='engineer_view'),
    path('delete/',EngineerDeleteView.as_view(), name='engineer_delete_view'),
    path('edit/', EngineerEditView.as_view(), name='engineer_edit_view'),
    path('view/<int:id>', EngineerDetailView.as_view(), name='engineer_detail_view'),
]
