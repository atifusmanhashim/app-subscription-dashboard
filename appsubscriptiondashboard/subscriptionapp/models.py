from django.db import models

# Used for Timezone / Datetime
from django.utils import timezone
from datetime import datetime

#For Getting Random String
from django.utils.crypto import get_random_string
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings

# using Constants from common utils
from utils import constants

from utils.BasicModel import BasicModel

from utils.common_utils import CommonUtils

from authapp.models import (AppUser)


class SubscriptionPlan(BasicModel):
    subscription_plan_no=CommonUtils.get_unique_no("SubPlan")
    subscription_plan_id=models.AutoField (primary_key=True)
    subscription_plan_name = models.CharField(max_length=100)
    subscription_plan_price = models.DecimalField(max_digits=10, default=0.00, decimal_places=2)

    def __str__(self):
        return self.subscription_plan_name + " ($ "+str(self.subscription_plan_price)+")"
    class Meta:
      db_table = 'subscription_plan'
      ordering=['subscription_plan_price']
      
class UserApp(BasicModel):
    
    app_no=CommonUtils.get_unique_no("UApp")
    app_id=models.AutoField (primary_key=True)
    app_owner = models.ForeignKey(AppUser, default=None, null=True,blank=True, on_delete=models.CASCADE)
    app_name = models.CharField (max_length=150, null=True, default=None, blank=True, unique=True)
    app_description = models.TextField(default=None, null=True, blank=True)
    
    def __str__(self):
        return self.app_name
   
    def app_owner_email(self):
        return self.app_owner.email
      
    class Meta:
      db_table = 'user_app'
      ordering=['app_name']

class UserAppSubscription(BasicModel):
    
    subscription_no=CommonUtils.get_unique_no("AppSub")
    subscription_id=models.AutoField (primary_key=True)
    subscription_app = models.OneToOneField(UserApp, default=None, null=True,blank=True, on_delete=models.CASCADE)
    subscription_plan = models.ForeignKey(SubscriptionPlan, default=None, null=True,blank=True, on_delete=models.CASCADE)
    subscription_user = models.ForeignKey(AppUser, default=None, null=True,blank=True, on_delete=models.CASCADE)

    def __str__(self):
        return self.subscription_app.app_name + "(Owner: "+self.subscription_user.name+", Plan: $"+str(self.subscription_plan.subscription_plan_price)+")"

    def subscription_app_name(self):
        return self.subscription_app.app_name
      
    def subscription_app_description(self):
        return self.subscription_app.app_description
      
    def subscription_plan_description(self):
        return self.subscription_plan.subscription_plan_name + "($+"+str(self.subscription_plan.subscription_plan_price)+")"
    
    class Meta:
      db_table = 'app_subscriptions'
      ordering=['-subscription_id']
      

@receiver(post_save, sender=UserApp)
def create_subscription(sender, instance, created, **kwargs):
    if created:
        # Create a subscription for the app with the Free Plan
        SubscriptionPlan.objects.get_or_create(subscription_plan_name='Free', subscription_plan_price=0)
        free_plan = SubscriptionPlan.objects.get(subscription_plan_name='Free')
        UserAppSubscription.objects.create(subscription_app=instance, subscription_user=instance.app_owner,subscription_plan=free_plan)