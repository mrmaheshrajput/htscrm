from django.db import models

from django.urls import reverse
from django.contrib.auth.models import User
from django.core.validators import RegexValidator


class ClientDetails(models.Model):
    mobile_regex        = RegexValidator(regex=r'^\+?1?\d{10,11}$', message="Mobile number must be entered in the format: '987xxxxxxx'")
    name                = models.CharField(max_length=120)
    calling_number      = models.CharField(validators=[mobile_regex], max_length=12)
    contact_number      = models.CharField(validators=[mobile_regex], max_length=12)
    address             = models.TextField(blank=True,null=True)
    city                = models.CharField(max_length=50,blank=True,null=True)
    state               = models.CharField(max_length=50,blank=True,null=True)
    pin                 = models.IntegerField(blank=True,null=True)
    created_by          = models.ForeignKey(User,on_delete=models.SET_NULL,null=True,related_name='customer_created_by')
    timestamp           = models.DateTimeField(auto_now_add=True)
    edited_by           = models.ForeignKey(User,on_delete=models.SET_NULL,null=True,related_name='customer_edited_by')
    edit_datetime       = models.DateTimeField(null=True,blank=True)

    def __str__(self):
        return 'Customer: %s, number: %s' % (self.name, self.contact_number)
