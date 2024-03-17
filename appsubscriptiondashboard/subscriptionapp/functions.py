#Getting Random String
from django.utils.crypto import get_random_string

# Used for Timezone / Datetime
from django.utils import timezone
from datetime import datetime, date, timedelta
import datetime

#Using Models
from .models import (UserApp, SubscriptionPlan, UserAppSubscription)

#Using Constant Values
from utils import constants

# Using Common Utility Functions
from utils.common_utils import CommonUtils

#Types for Checking DataTypes
import types

# User App
def get_user_app(sel_app_id, sel_user):
    try:
        user_app=UserApp.objects.get(app_id=sel_app_id, app_owner=sel_user, is_active=True)
    except UserAppSubscription.DoesNotExist:
        user_app=None
    except:
        user_app=None
    return user_app 

# User App Subscription
def get_subscription(sel_subscription_id, sel_user):
    try:
        user_app_subscription=UserAppSubscription.objects.get(subscription_id=sel_subscription_id, subscription_user=sel_user, is_active=True)
    except UserAppSubscription.DoesNotExist:
        user_app_subscription=None
    except:
        user_app_subscription=None
    return user_app_subscription

# Getting Plan By Price
def get_plan_by_price(sel_plan_price):
    try:
        plan=SubscriptionPlan.objects.get(subscription_plan_price=sel_plan_price,is_active=True)
    except SubscriptionPlan.DoesNotExist:
        plan=None
    except:
        plan=None
    return plan    

# Getting Subscription Plan by Name
def get_plan_by_name(sel_plan_name):
    try:
        plan=SubscriptionPlan.objects.get(subscription_plan_name__icontains=sel_plan_name,is_active=True)
    except SubscriptionPlan.DoesNotExist:
        plan=None
    except:
        plan=None
    return plan    