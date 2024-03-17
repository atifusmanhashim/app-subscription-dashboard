from django.db import models


# Used for Timezone / Datetime
from django.utils import timezone
from datetime import datetime

#For Getting Random String
from django.utils.crypto import get_random_string

# Using AbstractUser to extend Django's built-in User model
from django.contrib.auth.models import AbstractUser

from django.conf import settings

# using Constants from common utils
from utils import constants

from utils.BasicModel import BasicModel

from utils.common_utils import CommonUtils

#Custom Abstract Model 
class AppUser (AbstractUser):

    def get_user_no():
        new_user_no=CommonUtils.get_unique_no('U')
        return new_user_no   

    user_no=models.CharField(max_length=50, null=True,
                            blank=True,
                            default=get_user_no,
                            db_index=True)
    name=models.CharField (max_length=50, null=True, default=None, blank=True)
    contact_no=models.CharField (max_length=50, null=True, default=None, blank=True)
    contact_no_flag=models.BooleanField (default=False)
    is_auth = models.BooleanField (default=True)
 
    def __str__(self):
        if self.name is not None and self.email is not None:
            return self.name + " ("+self.email+")"
        elif self.first_name is not None and self.last_name is not None and self.email is not None:
            return self.first_name + " " + self.last_name +" ("+self.email+")"
        else:
            return self.username

    class Meta:
      db_table = 'app_user_mst'  
      ordering = ['-id']
      constraints = [models.UniqueConstraint(fields=['user_no'], name='unique_user_no')]


class LoginAnalytics(BasicModel):
    
    def get_no():
        new_no=CommonUtils.get_unique_no('ULA')
        return new_no   

    login_code=models.CharField(max_length=50, null=True,
                            blank=True,
                            default=get_no,
                            db_index=True)
    action=models.CharField (max_length=50, null=True, default=None, blank=True)   
    user=models.ForeignKey(AppUser, null=True, on_delete=models.CASCADE)
    source=models.CharField (max_length=300, null=True, default=None, blank=True)
    device_ip=models.CharField (max_length=50, null=True, default=None, blank=True)
    

    class Meta:
      db_table = 'app_login_analytics'
      ordering = ['-id']

class AppActionAnalytics(BasicModel):

    action=models.CharField (max_length=50, null=True, default=None, blank=True)   
    user=models.ForeignKey(AppUser, null=True, on_delete=models.CASCADE)
    source=models.CharField (max_length=300, null=True, default=None, blank=True)
    device_ip=models.CharField (max_length=50, null=True, default=None, blank=True)

    class Meta:
      db_table = 'app_action_analytics'
      ordering = ['-id']
