from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth import get_user_model

# Import your custom User model
from .models import AppUser

# Register your custom User model with the admin site
admin.site.register(AppUser, UserAdmin)
