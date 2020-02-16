from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.db import models
from django.urls import reverse

class Engineer(models.Model):
    mobile_regex            = RegexValidator(regex=r'^\+?1?\d{10,11}$', message="Mobile number must be entered in the format: '987xxxxxxx'")
    added_by                = models.ForeignKey(User, on_delete=models.SET_NULL,null=True)
    engineer_name           = models.CharField(max_length=120)
    mobile                  = models.CharField(validators=[mobile_regex], max_length=12)
    timestamp               = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.engineer_name

    # def get_absolute_url(self):
    #     return reverse('engineers:engineer_delete_view', kwargs={'id':self.id})
