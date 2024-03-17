from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, views, generics, response, permissions, authentication
from rest_framework.authtoken.views import ObtainAuthToken  #for Getting Neew Token
from rest_framework.parsers import JSONParser

from django.contrib.auth import get_user_model  # Using for user default model
from django.contrib.auth import authenticate    #Using for Login
from rest_framework.permissions import IsAuthenticated  #for using Authenication of User
from rest_framework.decorators import api_view, permission_classes
from django.utils.decorators import method_decorator
from django.views.decorators.debug import sensitive_post_parameters
from django.views.decorators.csrf import csrf_protect
from django.shortcuts import redirect

# For updation of Last login time in current user
from django.contrib.auth.models import update_last_login 

from collections import namedtuple

from django.db import IntegrityError
from requests.exceptions import HTTPError
from django.shortcuts import render, HttpResponse
from django.db.models import Q
from django.http import HttpRequest
 
#Settings
from django.conf import settings

# Used for Timezone / Datetime
from django.utils import timezone
from datetime import datetime, date, timedelta

#For Oauth2 Token
from braces.views import CsrfExemptMixin
from oauth2_provider.views.mixins import OAuthLibMixin
from oauth2_provider.settings import oauth2_settings

#For Getting Access Token
from oauth2_provider.views.base import TokenView
from oauth2_provider.models import get_access_token_model
from oauth2_provider.signals import app_authorized

#for Combining objects
from itertools import chain

#For Getting Random String
from django.utils.crypto import get_random_string

import json 
import traceback
import math
import datetime
import base64

# Using for Common Functions
from utils.common_utils import CommonUtils

# Using Comming Variables
from utils import constants

#Using Models and Serializers of Auth App
from .models import (AppUser, LoginAnalytics, AppActionAnalytics) 

                    
from .functions import (get_application_credentials, 
                        get_auth_user,
                        get_new_access_token,
                        get_access_token_details,
                        get_refresh_token_details,
                        get_new_refresh_token,
                        user_account_deactivate,
                        get_logout,
                        email_exist,
                        contact_exist
                        )

from .serializers import (RegisterSerializer, 
                        LoginSerializer, 
                        UserListSerializer, 
                        ChangePasswordSerializer, 
                        ResetPasswordSerializer)

from utils.functions import (save_analytics,save_login_analytics)

# Getting Application Credentials
class ApplicationCredentials(APIView):

    def get(self, request, *args,**kwargs):
        try:
            application=get_application_credentials()
            
            if application is not None:
                status_code=status.HTTP_200_OK
                response={
                            'msg':'success',
                            'status':status_code,
                            'data': {
                                        'client_id':application.client_id,
                                        'client_secret':application.client_secret,
                                        'name':application.name,
                                        'authorization_grant_type':application.authorization_grant_type,
                                        'User':application.user.username
                            }
                            
                        }
            else:
                status_code=status.HTTP_200_OK
                response={
                            'msg':'success',
                            'status':status_code,
                            'data': {}
                        }
            return Response(response, status=status_code)
        except Exception as e:
            message=("Error Date/Time:{current_time}\nURL:{current_url}\nError:{current_error}\n\{tb}\nCuurent Inputs:{current_input}\nUser:{current_user}".format(
                    current_time=CommonUtils.current_date_time(),
                    current_url=request.build_absolute_uri(),
                    current_error=repr(e),
                    tb=traceback.format_exc(),
                    current_input=request.data,
                    current_user=None
                    
            ))
            

            CommonUtils.write_log_file(message)
            response={'response':{'msg':'fail','status':status.HTTP_400_BAD_REQUEST,'errors':str(e)}}
            return Response(response, status=status.HTTP_400_BAD_REQUEST)      

# Normal Login API
class UserLogin(APIView):

     def post(self, request, *args, **kwargs):
        try:
            serializer = LoginSerializer(data=request.data)
            
            if serializer.is_valid():

                user = serializer.validated_data['user']
                if user:
                    if user.is_active:

                        #Updation of last login
                        update_last_login(None, user)

                        #Getting and Saving Device Information
                        data = request.data 
                        
                        action="Login"
                        analytics=save_analytics(user,action,request)

                        login_action="Login"
                        source="normal"
                        login_analytics=save_login_analytics(user,action,source,request)

                        
                        #Creating Customer Instance

                        if user.provider_id is None:
                            user.provider_id=0
                            user.save()

                        if user.name is None:
                            user_name=""
                        else:
                            user_name=user.name

                        if user.email is None:
                            user.email=""
                        else:
                            user_email=""

                        if user.delivery_address is None:
                            user_delivery_address=""
                        else:
                            user_delivery_address=user.delivery_address


                        if user.userCity is not None:
                            user_city=user.userCity.name
                        else:
                            user_city=""

                        if user.userCountry is not None:
                            user_country=user.userCountry.name
                        else:
                            user_country=""

                        #Get Access Token
                        access_token = get_new_access_token(user) 
                        
                        #Get Refresh Token
                        refresh_token = get_new_refresh_token(user)

                            

                        data={
                            "msg":'success',
                            "status":200,
                            'data': {
                                        'id':user.id,
                                        'user_no':user.user_no,
                                        'username':user.username,
                                        'name':user.name,
                                        'access_token':access_token.token,
                                        'expires':CommonUtils.display_date_time(access_token.expires),
                                        'refresh_token':refresh_token.token,
                                        'email':user.email,
                                        'contact_no':user.contact_no,
                                        'date_joined':CommonUtils.display_date_time(user.date_joined),
                                        'is_auth':user.is_auth,
                                        'token_type':'Bearer'
                                    }
                        }
                        
                        return Response(data,status=200)
                    else:
                        data={
                            "msg":'User Account is not active',
                            "status":200
                        }
                        return Response(data,status=200)
                else:
                    data={
                        "response":{
                            "msg":'Login Fail! Email or Password is Invalid',
                            "status":status.HTTP_400_BAD_REQUEST
                        }
                    }
                    return Response(data,status=status.HTTP_400_BAD_REQUEST)



            else:
                data={
                    "response":{
                        "msg":'Something Went Wrong',
                        "status":status.HTTP_400_BAD_REQUEST,
                        "errors":str(serializer.errors)
                    }
                }
                return Response(data,status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            status_code=status.HTTP_400_BAD_REQUEST
            message=("Error Date/Time:{current_time}\nURL:{current_url}\nError:{current_error}\n\{tb}\nCuurent Inputs:{current_input}\nUser:{current_user}".format(
                    current_time=CommonUtils.current_date_time(),
                    current_url=request.build_absolute_uri(),
                    current_error=repr(e),
                    tb=traceback.format_exc(),
                    current_input=request.data,
                    current_user=""
                    
            ))
            

            CommonUtils.write_log_file(message)
            response={'response':{'msg':'fail','status':status_code,'errors':str(e)}}
            return Response(response, status=status_code)    

#Normal Signup
class UserCreate(APIView):

    """
    Creates the user.
    """

    def post(self, request, format='json'):
        try:
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                ip = x_forwarded_for.split(',')[0]
            else:
                ip = request.META.get('REMOTE_ADDR') 

            data=request.data

            if 'email' in data:
                if data.get('email') is not None:
                    if email_exist(data.get('email'))==True:
                        response={'response':{'msg':'fail','status':status.HTTP_400_BAD_REQUEST,'errors':{"ErrorDetail(string='Email Address Already taken')"}}} 
                        return Response(response, status=status.HTTP_400_BAD_REQUEST) 
                else:
                    response={'response':{'msg':'fail','status':status.HTTP_400_BAD_REQUEST,'errors':{"ErrorDetail(string='Invalid Email Address')"}}} 
                    return Response(response, status=status.HTTP_400_BAD_REQUEST) 
            else:
                response={'response':{'msg':'fail','status':status.HTTP_400_BAD_REQUEST,'errors':{"ErrorDetail(string='Email Address is required')"}}} 
                return Response(response, status=status.HTTP_400_BAD_REQUEST) 

            if 'contact_no' in data:
                if data.get('contact_no') is not None:
                    if contact_exist(data.get('contact_no'))==True:
                        response={'response':{'msg':'fail','status':status.HTTP_400_BAD_REQUEST,'errors':{"ErrorDetail(string='Contact No. Already taken')"}}}
                        return Response(response, status=status.HTTP_400_BAD_REQUEST)
                else:
                    response={'response':{'msg':'fail','status':status.HTTP_400_BAD_REQUEST,'errors':{"ErrorDetail(string='Invalid Contact #')"}}}
                    return Response(response, status=status.HTTP_400_BAD_REQUEST)
            else:
                response={'response':{'msg':'fail','status':status.HTTP_400_BAD_REQUEST,'errors':{"ErrorDetail(string='Contact No. is required')"}}}
                return Response(response, status=status.HTTP_400_BAD_REQUEST)

            serializer = RegisterSerializer(data=request.data)
            
            if serializer.is_valid():
                user = serializer.save()
                if user:
                    
                    app_version = data.get('app_version', None)
                    platform= data.get('platform', None)
                    brand= data.get('brand', None)
                    device= data.get('device_id', None)
                    device_model= data.get('device_model', None)
                    registered_token=data.get('registered_token',None)
                    
                    #Get Access Token
                    access_token = get_new_access_token(user) 
                        
                    #Get Refresh Token
                    refresh_token = get_new_refresh_token(user)

                    #Saving Analytics
                    action="Normal Signup"
                    analytics=save_analytics(user,action,request)

                    login_action="Normal Signup"
                    source="signup"
                    login_analytics=save_login_analytics(user,action,source,request)

                            
                    #Custom User Credentials Response
                    user_data={
                            "response":{
                                'msg':'Successfully registered',
                                'status':200,
                                'data':{
                                        'id':user.id,
                                        'user_no':user.user_no,
                                        'username':user.username,
                                        'name':user.name,
                                        'access_token':access_token.token,
                                        'expires':CommonUtils.display_date_time(access_token.expires),
                                        'refresh_token':refresh_token.token,
                                        'email':user.email,
                                        'contact_no':user.contact_no,
                                        'date_joined':CommonUtils.display_date_time(user.date_joined),
                                        'is_auth':user.is_auth,
                                        'token_type':'Bearer',
                                }
                            }
                    }
                    return Response(user_data, status=status.HTTP_200_OK)
                else:
                    response={"response":{'msg':'fails due to Validation Errors','status':status.HTTP_400_BAD_REQUEST}}
                    return Response(response, status=status.HTTP_400_BAD_REQUEST)
            else:
                response={"response":{'msg':'Something Went Wrong','status':status.HTTP_400_BAD_REQUEST,'errors':str(serializer.errors)}}
                return Response(response, status==status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            message=("Error Date/Time:{current_time}\nURL:{current_url}\nError:{current_error}\n\{tb}\nCuurent Inputs:{current_input}\nUser:{current_user}".format(
                    current_time=CommonUtils.current_date_time(),
                    current_url=request.build_absolute_uri(),
                    current_error=repr(e),
                    tb=traceback.format_exc(),
                    current_input=request.data,
                    current_user=None
                    
            ))
            

            CommonUtils.write_log_file(message)
            response={'response':{'msg':'fail','status':status.HTTP_400_BAD_REQUEST,'errors':str(e)}}
            return Response(response, status=status.HTTP_400_BAD_REQUEST)   

#Email Check
class EmailCheck(APIView):

    def post(self, request, *args, **kwargs):
        try:
            if 'email' in request.data:
                if request.data.get('email') is not None:
                    email_address=request.data.get('email')
                else:
                    email_address=None
            else:
                email_address=None
                
            if (email_address is None):
                status_code=status.HTTP_400_BAD_REQUEST
                data={
                    "response":{
                        "msg":"Email Address not Provided",
                        "status":status_code
                    }
                }
                return Response(data, status=status.HTTP_400_BAD_REQUEST)
            
            if (email_address is not None):
                chk_type="Checking Email Address"
                if AppUser.objects.filter(email=email_address).exists():
                    user = AppUser.objects.get(email=email_address)

                    #Saving Analytics
                    action="Email Checking"
                    analytics=save_analytics(user,action,request)

                    status_code=status.HTTP_200_OK
                    user_data={
                        "msg":"success",
                        "status":status_code,
                        "data":{
                                    "isUserRegister":True,
                                    "chk_type":chk_type,
                                    "email":user.email,
                                    "contact_no":user.contact_no
                                }
                    }
                    
                else:
                    status_code=status.HTTP_200_OK
                    user_data={
                            "msg":"fail",
                            "status":status_code,
                                "data":{
                                    "isUserRegister":False,
                                    "chk_type":chk_type
                                }
                    }
                        
                return Response(user_data, status=status_code)
                    
                    
        except Exception as e:
            message=("Error Date/Time:{current_time}\nURL:{current_url}\nError:{current_error}\n\{tb}\nCuurent Inputs:{current_input}\nUser:{current_user}".format(
                    current_time=CommonUtils.current_date_time(),
                    current_url=request.build_absolute_uri(),
                    current_error=repr(e),
                    tb=traceback.format_exc(),
                    current_input=request.data,
                    current_user=user
                    
            ))
            
            CommonUtils.write_log_file(message)
            response={'response':{'msg':'fail','status':status.HTTP_400_BAD_REQUEST,'errors':str(e)}}
            return Response(response, status=status.HTTP_400_BAD_REQUEST)   

#Update Profile
class UpdateProfile(APIView):
   
    # Authentication using Bearer Access Token
    permission_classes = [IsAuthenticated, ]
    
    def post(self, request, *args, **kwargs):
        try:
            if 'Authorization' in request.headers:
                token=request.META['HTTP_AUTHORIZATION'][6:]

                token=str(token).strip()
                theuser=get_auth_user(token)
                user=theuser
                
                #Saving Analytics
                action="Update Profile"
                analytics=save_analytics(user,action,request)

                if 'username' in request.data:
                    if str(request.data.get('username')).strip() is not None:
                        new_user_name=str(request.data.get('username')).strip()
                        user_name_chk=AppUser.objects.filter(username=new_user_name)
                        if user_name_chk.count()==0:
                            user.username=new_user_name
                            user.save()

                if 'email' in request.data:
                    if str(request.data.get('email')).strip() is not None:
                        new_email=str(request.data.get('email')).strip()
                        new_email_chk=AppUser.objects.filter(is_active=True,email=new_email)
                        if new_email_chk.count()==0:
                            user.email=new_email
                            user.save()
                        else:
                            errors={
                                    "ErrorDetail(string='Email Address Already Exists')"
                            }

                            response={'response':{'msg':'fail','status':status.HTTP_400_BAD_REQUEST,'errors':errors}}
                            return Response(response, status=status.HTTP_400_BAD_REQUEST)


                if 'name' in request.data:
                    if request.data.get('name') is not None:
                        user_name=request.data.get('name')
                    else:
                        user_name=user.name
                    user.name=user_name
                    user.save()

                if 'contact_no' in request.data:
                    if request.data.get('contact_no') is not None:
                        if contact_exist(request.data.get('contact_no'))==False:
                            try:
                                user.contact_no=request.data.get('contact_no')
                                user.contact_no_flag=True
                                user.save()
                            except IntegrityError:
                                user.contact_no=user.contact_no
                        else:
                            errors={
                                    "ErrorDetail(string='Contact No. Already Exists')"
                            }

                            response={'response':{'msg':'fail','status':status.HTTP_400_BAD_REQUEST,'errors':errors}}
                            return Response(response, status=status.HTTP_400_BAD_REQUEST)
            

                serializer=UserListSerializer(instance=user)
                
                user_data=serializer.data
                
                response={'response':{'msg':'success','status':200,'data':user_data}}
                return Response(response, status=status.HTTP_200_OK)
        except Exception as e:
            message=("Error Date/Time:{current_time}\nURL:{current_url}\nError:{current_error}\n\{tb}\nCuurent Inputs:{current_input}\nUser:{current_user}".format(
                    current_time=CommonUtils.current_date_time(),
                    current_url=request.build_absolute_uri(),
                    current_error=repr(e),
                    tb=traceback.format_exc(),
                    current_input=request.data,
                    current_user=user
                    
            ))
            
            CommonUtils.write_log_file(message)
            response={'response':{'msg':'fail','status':status.HTTP_400_BAD_REQUEST,'errors':str(e)}}
            return Response(response, status=status.HTTP_400_BAD_REQUEST) 

#User Profile
class UserProfile(APIView):
    serializer_class=UserListSerializer
    permission_classes = [IsAuthenticated, ]

    def post(self, request, format='json'):
        try:
            token=request.META['HTTP_AUTHORIZATION'][6:]
            # Checking Token
            token=str(token).strip()
            # Checking User from Instance of Token
            theuser=get_auth_user(token)
            serializer=self.serializer_class(instance=theuser)
            user_data=serializer.data
            
            response={'response':{'msg':'success','status':status.HTTP_200_OK,'data':user_data}}
            return Response(response, status=status.HTTP_200_OK)

        except Exception as e:
            message=("Error Date/Time:{current_time}\nURL:{current_url}\nError:{current_error}\n\{tb}\nCuurent Inputs:{current_input}\nUser:{current_user}".format(
                    current_time=CommonUtils.current_date_time(),
                    current_url=request.build_absolute_uri(),
                    current_error=repr(e),
                    tb=traceback.format_exc(),
                    current_input=request.data,
                    current_user=theuser

            ))


            CommonUtils.write_log_file(message)
            response={'response':{'msg':'fail','status':status.HTTP_400_BAD_REQUEST,'errors':str(e)}}
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

#Change Password API
class changepassword(APIView):
    serializer_class=ChangePasswordSerializer
    permission_classes = [IsAuthenticated, ]
    
    def post(self, request, format='json'):
        try:
            
            if 'old_password' not in request.data:
                 errors={
                           "ErrorDetail(string='Current Password Not Provided')"
                 }
                 response={'response':{'msg':'fail','status':status.HTTP_400_BAD_REQUEST,'errors':errors}}
                 return Response(response, status=status.HTTP_400_BAD_REQUEST)
            if request.data.get('old_password') is None:
                 errors={
                           "ErrorDetail(string='Current Password Not Provided')"
                 }
                 response={'response':{'msg':'fail','status':status.HTTP_400_BAD_REQUEST,'errors':errors}}
                 return Response(response, status=status.HTTP_400_BAD_REQUEST)
            if request.data.get('new_password') is None:

                 errors={
                           "ErrorDetail(string='New Password Not Provided')"
                 }
                 response={'response':{'msg':'fail','status':status.HTTP_400_BAD_REQUEST,'errors':errors}}
                 return Response(response, status=status.HTTP_400_BAD_REQUEST)
            if 'new_password' not in request.data:
                 errors={
                           "ErrorDetail(string='New Password Not Provided')"
                 }
                 response={'response':{'msg':'fail','status':status.HTTP_400_BAD_REQUEST,'errors':errors}}
                 return Response(response, status=status.HTTP_400_BAD_REQUEST)

            serializer=self.serializer_class(data=request.data)
            
            if serializer.is_valid():
                #Extracting Token From Authorization
                token=request.META['HTTP_AUTHORIZATION'][6:] 
                # Checking Token
                token=str(token).strip()
                # Checking User from Instance of Token
                user=get_auth_user(token)

                #Checking Old / Current Password
                if not user.check_password(serializer.data.get('old_password')):
                    errors={
                           "ErrorDetail(string='Incorrect Current Password')" 
                    }
                    response={'response':{'msg':'fail','status':status.HTTP_400_BAD_REQUEST,'errors':errors}}
                    return Response(response, status=status.HTTP_400_BAD_REQUEST)

                user.set_password(serializer.data.get('new_password'))
                user.save()
                
                access_token = get_new_access_token(user)
                refresh_token =  get_new_refresh_token(user)

                #Saving Analytics
                action="Change Password"
                analytics=save_analytics(user,action,request)

                        
                if user.contact_no is None:
                    user_contact_no=""
                else:
                    user_contact_no=user.contact_no  
                            
                if user.email is None:
                    user_email=""
                else:
                    user_email=user.email
                

                user_data={
                            'id':user.id,
                            'user_no':user.user_no,
                            'username':user.username,
                            'name':user.name,
                            'access_token':access_token.token,
                            'expires':CommonUtils.display_date_time(access_token.expires),
                            'refresh_token':refresh_token.token,
                            'email':user_email,
                            'contact_no':user_contact_no,
                            'date_joined':CommonUtils.display_date_time(user.date_joined),
                            'is_auth':user.is_auth,
                            'token_type':'Bearer',
                        }      

                response={'response':{'msg':'success','status':status.HTTP_200_OK,'data':user_data}} 
                return Response(response, status=status.HTTP_200_OK)

            else:
                response={'response':{'msg':'fail','status':status.HTTP_400_BAD_REQUEST,'errors':serializer.errors}} 
                return Response(response, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            message=("Error Date/Time:{current_time}\nURL:{current_url}\nError:{current_error}\n\{tb}\nCuurent Inputs:{current_input}\nUser:{current_user}".format(
                    current_time=CommonUtils.current_date_time(),
                    current_url=request.build_absolute_uri(),
                    current_error=repr(e),
                    tb=traceback.format_exc(),
                    current_input=request.data,
                    current_user=user
                    
            ))
            

            CommonUtils.write_log_file(message)
            response={'response':{'msg':'fail','status':status.HTTP_400_BAD_REQUEST,'errors':str(e)}}
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
