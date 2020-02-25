from calls.models import CallRegister, CallAllocation
from customers.models import ClientDetails
from django.contrib.auth.models import User
from django.db import models
from engineers.models import Engineer


class CallVisit(models.Model):
    CNA   = 'CNA'
    DCP   = 'DCP'
    LNA   = 'LNA'
    HNA   = 'HNA'
    CVD   = 'CVD'
    VND   = 'VND'
    VISIT_STATUS_CHOICES = [
            (CNA, 'Customer was not available'),
            (DCP, 'Main door was closed'),
            (LNA, 'Light was out'),
            (HNA, 'Decision-maker was not available'),
            (VND, 'Visit not done - Other reason'),
            (CVD, 'Customer visit done')
        ]

    callallocation_id           = models.ForeignKey(CallAllocation,on_delete=models.SET_NULL,null=True,related_name='call_allocation_id')
    call_id                     = models.ForeignKey(CallRegister, on_delete=models.SET_NULL,null=True,related_name='mother_call_id')
    serviced_by                 = models.ForeignKey(Engineer,on_delete=models.SET_NULL,null=True,related_name='service_by_engineer')
    visit_status                = models.CharField(max_length=3,choices=VISIT_STATUS_CHOICES)
    visit_date_time             = models.DateTimeField()
    outcome                     = models.TextField()
    call_status_final           = models.BooleanField(default=True)
    call_visit_final_notes      = models.CharField(max_length=120)
    added_by                    = models.ForeignKey(User,on_delete=models.SET_NULL,null=True,related_name='call_visit_added_by')
    timestamp                   = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return '(%s) - %s. %s, call %s' % (self.pk, self.callallocation_id, self.visit_status, self.call_status_final)
