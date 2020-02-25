from django.urls import path

from visits.views import VisitListView, VisitCreateView, VisitDetailView

app_name    = 'visits'
urlpatterns = [
    path('', VisitListView.as_view(), name='visit_list_view'),
    path('create/<int:id>/', VisitCreateView.as_view(), name='visit_create_view'),
    path('view/<int:id>/', VisitDetailView.as_view(), name='visit_detail_view'),
]
