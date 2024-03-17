#Getting Random String
from django.utils.crypto import get_random_string

# Used for Timezone / Datetime
from django.utils import timezone
from datetime import datetime, date, timedelta
import datetime

#Oauth2 Provider
from oauth2_provider.models import AccessToken, Application, RefreshToken
from oauth2_provider.views.mixins import OAuthLibMixin
from oauth2_provider.settings import oauth2_settings
from oauth2_provider.generators import generate_client_id, generate_client_secret

#For Getting Access Token
from oauth2_provider.views import TokenView

#Using Models
from .models import (AppUser, AppActionAnalytics, LoginAnalytics)

#Using Constant Values
from utils import constants

# Using Common Utility Functions
from utils.common_utils import CommonUtils

#Types for Checking DataTypes
import types

from django.db.models import Q
from django.conf import settings

#==================================================Oauth2 ====================================
#Getting Application Oauth2 Credentials
def get_application_credentials():
    
    application_chk = Application.objects.filter(name=constants.app_name)
    if application_chk.count()==0:
        application=Application(
                                user= AppUser.objects.filter(is_superuser=True)[0],
                                client_type="confidential",
                                authorization_grant_type="password",
                                name=constants.app_name,
                                client_id=generate_client_id(),
                                client_secret=generate_client_secret(),
                                )   
        application.save()                        
    else:
        application=application_chk[0] 
            
    result=application
        
    return result

#Getting User using ID
def get_user(sel_id):
    if sel_id.isnumeric():
        try:
            sel_user=AppUser.objects.get(pk=sel_id)
        except AppUser.DoesNotExist:
            sel_user=None
    else:
       sel_user=None 
    return sel_user

def get_user_referral_code(sel_string,request):
    if sel_string is not None:
        user_referral_string=request.scheme+"://"+request.get_host()+"?referral="+sel_string
    else:
        user_referral_string=""
    return user_referral_string

def get_user_list():
    try:
        user_list=AppUser.objects.filter(is_active=True).order_by('-id')
    except AppUser.DoesNotExist:
        user_list=None
    return user_list

def get_user_search_list(txt_search):
    try:
        user_list=AppUser.objects.filter(Q(name__icontains=txt_search) | Q(email__icontains=txt_search) | Q(username__icontains=txt_search)| Q(contact_no__icontains=txt_search),is_active=True).order_by('-id')
    except AppUser.DoesNotExist:
        user_list=None
    return user_list

def get_phone_user(sel_contact_no):
    if sel_contact_no is not None:
        try:
            user_obj=AppUser.objects.get(is_active=True,contact_no=sel_contact_no,contact_no_flag=True)
            # user_no=user_obj.user_no
        except AppUser.DoesNotExist:
            new_user_no=CommonUtils.get_unique_no("U")
            user_obj=AppUser.objects.create(is_active=True, username=new_user_no,provider_id=0,contact_no=sel_contact_no, contact_no_flag=True)
            # user_no=user_obj.user_no

    else:
        user_obj=None
        # user_no=""
    return user_obj
 
#Getting Authorized User using Token
def get_auth_user(token):
    
    if token is not None: 
        token=str(token).strip()
        try:
            token_instance=AccessToken.objects.get(token=token)
            try:
                theuser=AppUser.objects.filter(is_active=True).get(pk=token_instance.user_id)
                result=theuser
            except AppUser.DoesNotExist:
                result=None
        except AccessToken.DoesNotExist:
            result=None
    else:
       result=None
    
    return result

# Account Deactivation
def user_account_deactivate(sel_user):
    if sel_user is not None:
        theuser=sel_user
        if sel_user.is_active==True:
            sel_user.is_active=False
            sel_user.save()
            return True
        else:
            return False
    else:
        return False


#Logut
def get_logout(token):
    
    theuser=get_auth_user(token)
    instance = AccessToken.objects.filter(user=theuser,token=token)
    instance.delete()
    
    return True

def get_token_expiration():
    # 'Access Token Expiration' and Scopes
    expire_seconds = oauth2_settings.user_settings['ACCESS_TOKEN_EXPIRE_SECONDS']
    
    expires=timezone.now() + timezone.timedelta(seconds=expire_seconds)
    
    result=expires
    return result

#Getting Scopes from Settings of Oauth2
def get_token_scopes():
    scopes = oauth2_settings.user_settings['SCOPES']
    return scopes

#Getting New Access Token
def get_access_token(seluser):
    
    application=get_application_credentials()
    access_token = AccessToken.objects.create(user=seluser,
                                                    application=application,
                                                    token=get_random_string(length=32),
                                                    expires=get_token_expiration(),
                                                    scope=get_token_scopes(),
                                                )
    result=access_token
    
    return result

def get_new_access_token(seluser):

    application=get_application_credentials()

    access_token = AccessToken.objects.create(
                                                    user=seluser,
                                                    application=application,
                                                    token=get_random_string(length=32),
                                                    expires=get_token_expiration(),
                                                    scope=get_token_scopes(),
                                                )
    result=access_token

    return result

#Getting New Refresh Token
def get_refresh_token(seluser):
    
    application=get_application_credentials()
    access_token=get_access_token(seluser)
    refresh_token = RefreshToken.objects.create(
                                                            user=seluser,
                                                            token=get_random_string(length=32),
                                                            access_token=access_token,
                                                            application=application)
    result=refresh_token
    return result

def get_new_refresh_token(seluser):

    application=get_application_credentials()
    access_token=get_new_access_token(seluser)
    refresh_token = RefreshToken.objects.create(
                                                            user=seluser,
                                                            token=get_random_string(length=32),
                                                            access_token=access_token,
                                                            application=application)
    result=refresh_token
    return result

def get_access_token_details(seltoken):

    if seltoken is not None:
        try:
            access_token=AccessToken.objects.get(token=seltoken)
        except AccessToken.DoesNotExist:
            access_token=None
    else:
        access_token=None
    return access_token

def get_refresh_token_details(selaccesstoken):

    if selaccesstoken is not None:
        try:
            refresh_token=RefreshToken.objects.get(access_token=selaccesstoken)
        except RefreshToken.DoesNotExist:
            refresh_token=None
    else:
        refresh_token=None
    return refresh_token
#==================================================Oauth2 ====================================

#================================================= Email And Contact Checking ================
def email_exist(sel_email):
    
    if sel_email is not None:
        queryset=AppUser.objects.filter(email=sel_email,is_active=True)
        if queryset.count() >=1:
            return True
        else:
            return False
    else:
        return False
    
def contact_exist(sel_contact):
    
    if sel_contact is not None:
        queryset=AppUser.objects.filter(contact_no=sel_contact,is_active=True,contact_no_flag=True)
        if queryset.count() >=1:
            return True
        else:
            return False
    else:
        return False    
#================================================= End of Email And Contact Checking ================

