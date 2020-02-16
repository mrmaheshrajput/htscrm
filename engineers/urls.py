from django.urls import path

from engineers.views import EngineerView, EngineerDeleteView

app_name    = 'engineers'
urlpatterns = [
    path('',EngineerView.as_view(), name='engineer_view'),
    path('delete/<int:id>/',EngineerDeleteView.as_view(), name='engineer_delete_view'),
]
