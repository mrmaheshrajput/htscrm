from customers.models import ClientDetails
from django.contrib.auth.models import User
from django.db import models
from engineers.models import Engineer

class CallRegister(models.Model):
    # Choices
    SERVICE     = 'S'
    GAS         = 'G'
    PART        = 'P'
    NO_COOL     = 'N'
    OTHER       = 'O'
    COMPLAINT_CHOICES = [
        (SERVICE, 'Service'),
        (GAS, 'Gas Leakage'),
        (PART, 'Part Replacement'),
        (NO_COOL, 'No Cooling'),
        (OTHER, 'Other')
    ]

    # Model
    customer                = models.ForeignKey(ClientDetails,on_delete=models.SET_NULL,null=True,related_name='call_of')
    complaint_nature        = models.CharField(max_length=50)
    brand                   = models.CharField(max_length=50,blank=True,null=True)
    product_name            = models.CharField(max_length=50,blank=True,null=True)
    product_serial          = models.CharField(max_length=30,blank=True,null=True)
    product_coverage        = models.BooleanField(blank=True,null=True)
    appointment_date        = models.DateField(blank=True,null=True)
    appointment_time        = models.TimeField(blank=True,null=True)
    added_by                = models.ForeignKey(User,on_delete=models.SET_NULL,null=True,related_name='call_added_by')
    timestamp               = models.DateTimeField(auto_now_add=True)
    edited_by               = models.ForeignKey(User,on_delete=models.SET_NULL,null=True,related_name='call_edited_by')
    edit_datetime           = models.DateTimeField(null=True,blank=True)

    def __str__(self):
        return ('%s - %s') % (self.pk, self.customer)


class CallAllocation(models.Model):
    # Choices
    PENDING    = 'P'
    COMPLETED   = 'C'
    EXPIRED    = 'E'
    CALL_ALLOCATION_CHOICES = [
        (PENDING, 'Pending'),
        (COMPLETED, 'Completed'),
        (EXPIRED, 'Expired')
    ]


    call                    = models.ForeignKey(CallRegister,on_delete=models.SET_NULL,null=True,related_name='parent_call')
    status                  = models.CharField(max_length=1,default='P',choices=CALL_ALLOCATION_CHOICES)
    engineer_assigned       = models.ForeignKey(Engineer,on_delete=models.SET_NULL,null=True,related_name='assigned_engineer')
    added_by                = models.ForeignKey(User,on_delete=models.SET_NULL,null=True,related_name='call_allocated_by')
    timestamp               = models.DateTimeField(auto_now_add=True)
    edited_by               = models.ForeignKey(User,on_delete=models.SET_NULL,null=True,related_name='allocation_edited_by')
    edit_datetime           = models.DateTimeField(null=True,blank=True)

    def __str__(self):
        return ('(%s) %s - %s') % (self.pk ,self.call, self.status)
