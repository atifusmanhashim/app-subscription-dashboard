from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth import get_user_model

# Import your custom User model
from .models import AppUser,LoginAnalytics,AppActionAnalytics

# Register your custom User model with the admin site
admin.site.register(AppUser, UserAdmin)
admin.site.register(LoginAnalytics)
admin.site.register(AppActionAnalytics)

from subscriptionapp.models import (SubscriptionPlan, UserApp, UserAppSubscription)

admin.site.register(SubscriptionPlan)
admin.site.register(UserApp)
admin.site.register(UserAppSubscription)