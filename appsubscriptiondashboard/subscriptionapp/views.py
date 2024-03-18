from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, views, generics, response, permissions, authentication
from rest_framework.authtoken.views import ObtainAuthToken  #for Getting Neew Token
from rest_framework.parsers import JSONParser
from rest_framework.exceptions import ErrorDetail

from django.contrib.auth import get_user_model  # Using for user default model
from django.contrib.auth import authenticate    #Using for Login
from rest_framework.permissions import IsAuthenticated  #for using Authenication of User
from rest_framework.decorators import api_view, permission_classes
from django.utils.decorators import method_decorator
from django.views.decorators.debug import sensitive_post_parameters
from django.views.decorators.csrf import csrf_protect
from django.shortcuts import redirect

from collections import namedtuple

from django.db import IntegrityError
from requests.exceptions import HTTPError
from django.shortcuts import render, HttpResponse
from django.db.models import Q
from django.http import HttpRequest

#Versioning
from rest_framework.versioning import URLPathVersioning

import json 
import traceback
import math
import datetime
import base64

# Using for Common Functions
from utils.common_utils import CommonUtils

# Using Comming Variables
from utils import constants

from utils.functions import (save_analytics,save_login_analytics)

#Using Models of Auth App
from authapp.models import (AppUser, LoginAnalytics, AppActionAnalytics) 
from authapp.functions import (get_auth_user)

# Using Models of Subscription App
from .models import (SubscriptionPlan,UserApp,UserAppSubscription)
from .serializers import (SubscriptionPlanSerializer,UserAppSerializer,UserAppSubscriptionSerializer)
from .functions import (get_user_app, get_subscription, get_plan_by_name,get_plan_by_price)

#Creation of User App
class CreateUserApp(APIView):
    serializer_class = UserAppSerializer
    # Authentication using Bearer Access Token
    permission_classes = [IsAuthenticated, ]

    def post(self, request, *args, **kwargs):
        theuser=None
        try:
            if 'Authorization' in request.headers:
                token=request.META['HTTP_AUTHORIZATION'][6:]

                token=str(token).strip()
                theuser=get_auth_user(token)
                
                #Saving Analytics
                action="Creation of UserApp"
                analytics=save_analytics(theuser,action,request)
                
                required_data={
                                'app_owner':theuser.id,
                                'app_name':request.data.get('app_name'),
                                'app_description':request.data.get('app_description')
                            }
                serializer = self.serializer_class(data=required_data)
                if serializer.is_valid():
                    user_app_create=serializer.save()

                    mydata=serializer.data

                    response={'response':{'msg':'success','current_version':request.version,'status':status.HTTP_200_OK,'data':mydata}}
                    return Response(response, status=status.HTTP_200_OK) 
                else:
                    response={'response':{'msg':'fail','current_version':request.version,'status':status.HTTP_400_BAD_REQUEST,'errors':str(serializer.errors)}} 
                    return Response(response, status=status.HTTP_400_BAD_REQUEST) 

            else:
                response={'response':{'msg':'fail','current_version':request.version,'status':status.HTTP_401_UNAUTHORIZED,'error':'Unauthorized'}}
                return Response(response, status=status.HTTP_401_UNAUTHORIZED)  
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
        
        
#Update of User App
class UpdateUserApp(APIView):
    serializer_class = UserAppSerializer
    # Authentication using Bearer Access Token
    permission_classes = [IsAuthenticated, ]

    def post(self, request, *args, **kwargs):
        theuser=None
        try:
            if 'Authorization' in request.headers:
                token=request.META['HTTP_AUTHORIZATION'][6:]

                token=str(token).strip()
                theuser=get_auth_user(token)
                
                #Saving Analytics
                action="Updation of UserApp"
                analytics=save_analytics(theuser,action,request)
                
                if 'app_id' in request.data:
                    sel_app_id=request.data.get('app_id')
                    sel_user_app=get_user_app(sel_app_id, theuser)
                else:
                    sel_app_id=None
                    sel_user_app=None
                    
                if sel_user_app is not None:
                    
                    required_data={
                                    'app_name':request.data.get('app_name'),
                                    'app_description':request.data.get('app_description')
                                }
                    serializer = self.serializer_class(instance=sel_user_app,data=required_data, partial=True)
                    if serializer.is_valid():
                        user_app_update=serializer.save()

                        mydata=serializer.data
                        response={'response':{'msg':'success','current_version':request.version,'status':status.HTTP_200_OK,'data':mydata}}
                        return Response(response, status=status.HTTP_200_OK) 
                    else:
                        response={'response':{'msg':'fail','current_version':request.version,'status':status.HTTP_400_BAD_REQUEST,'errors':str(serializer.errors)}} 
                        return Response(response, status=status.HTTP_400_BAD_REQUEST) 
    
                else:
                    response={'response':{'msg':'fail','current_version':request.version,'status':status.HTTP_400_BAD_REQUEST,'error':'Invalid App ID Provided'}}
                    return Response(response, status=status.HTTP_401_UNAUTHORIZED)  
                
                    
            else:
                response={'response':{'msg':'fail','current_version':request.version,'status':status.HTTP_401_UNAUTHORIZED,'error':'Unauthorized'}}
                return Response(response, status=status.HTTP_401_UNAUTHORIZED)  
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
        
#Deletion of User App
class DeleteUserApp(APIView):
    serializer_class = UserAppSerializer
    # Authentication using Bearer Access Token
    permission_classes = [IsAuthenticated, ]

    def post(self, request, *args, **kwargs):
        theuser=None
        try:
            if 'Authorization' in request.headers:
                token=request.META['HTTP_AUTHORIZATION'][6:]

                token=str(token).strip()
                theuser=get_auth_user(token)
                
                #Saving Analytics
                action="Deletion of UserApp"
                analytics=save_analytics(theuser,action,request)
                
                if 'app_id' in request.data:
                    sel_app_id=request.data.get('app_id')
                    sel_user_app=get_user_app(sel_app_id, theuser)
                else:
                    sel_app_id=None
                    sel_user_app=None
                    
                if sel_user_app is not None:
                    
                    required_data={
                                    'app_name':request.data.get('app_name'),
                                    'app_description':request.data.get('app_description'),
                                    'is_active':0
                                }
                    serializer = self.serializer_class(instance=sel_user_app,data=required_data, partial=True)
                    if serializer.is_valid():
                        user_app_update=serializer.save()

                        mydata=serializer.data
                        response={'response':{'msg':'success','current_version':request.version,'status':status.HTTP_200_OK,'data':mydata}}
                        return Response(response, status=status.HTTP_200_OK) 
                    else:
                        response={'response':{'msg':'fail','current_version':request.version,'status':status.HTTP_400_BAD_REQUEST,'errors':str(serializer.errors)}} 
                        return Response(response, status=status.HTTP_400_BAD_REQUEST) 
    
                else:
                    response={'response':{'msg':'fail','current_version':request.version,'status':status.HTTP_400_BAD_REQUEST,'error':'Invalid App ID Provided'}}
                    return Response(response, status=status.HTTP_401_UNAUTHORIZED)  
                
                    
            else:
                response={'response':{'msg':'fail','current_version':request.version,'status':status.HTTP_401_UNAUTHORIZED,'error':'Unauthorized'}}
                return Response(response, status=status.HTTP_401_UNAUTHORIZED)  
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
        
#Details of User App
class UserAppDetails(APIView):
    serializer_class = UserAppSerializer
    # Authentication using Bearer Access Token
    permission_classes = [IsAuthenticated, ]

    def post(self, request, *args, **kwargs):
        theuser=None
        try:
            if 'Authorization' in request.headers:
                token=request.META['HTTP_AUTHORIZATION'][6:]

                token=str(token).strip()
                theuser=get_auth_user(token)
                
                #Saving Analytics
                action="View Details of UserApp"
                analytics=save_analytics(theuser,action,request)
                
                if 'app_id' in request.data:
                    sel_app_id=request.data.get('app_id')
                    sel_user_app=get_user_app(sel_app_id, theuser)
                else:
                    sel_app_id=None
                    sel_user_app=None
                    
                if sel_user_app is not None:
                    
                   
                    serializer = self.serializer_class(instance=sel_user_app, partial=True)
                    mydata=serializer.data
                    response={'response':{'msg':'success','current_version':request.version,'status':status.HTTP_200_OK,'data':mydata}}
                    return Response(response, status=status.HTTP_200_OK) 
     
                else:
                    response={'response':{'msg':'fail','current_version':request.version,'status':status.HTTP_400_BAD_REQUEST,'error':'Invalid App ID Provided'}}
                    return Response(response, status=status.HTTP_401_UNAUTHORIZED)  
                
                    
            else:
                response={'response':{'msg':'fail','current_version':request.version,'status':status.HTTP_401_UNAUTHORIZED,'error':'Unauthorized'}}
                return Response(response, status=status.HTTP_401_UNAUTHORIZED)  
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

# Unsubscribe
class SubscriptionDelete(APIView):
    serializer_class = UserAppSubscriptionSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        try:
            # Extract user from request
            the_user = request.user

            # Extract subscription_id from request data
            sel_subscription_id = request.data.get('subscription_id')

            # Get subscription associated with the user and provided subscription_id
            subscription = UserAppSubscription.objects.filter(subscription_user=the_user, subscription_id=sel_subscription_id).first()

            if subscription:
                subscription.is_active=False
                subscription.save()
                serializer = self.serializer_class(subscription)
                return Response({'response': {'msg': 'success', 'data': serializer.data}}, status=status.HTTP_200_OK)
            else:
                return Response({'response': {'msg': 'fail', 'error': 'Invalid Subscription ID'}}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            message = ("Error Date/Time:{current_time}\nURL:{current_url}\nError:{current_error}\n\{tb}\nCuurent Inputs:{current_input}\nUser:{current_user}".format(
                current_time=CommonUtils.current_date_time(),
                current_url=request.build_absolute_uri(),
                current_error=repr(e),
                tb=traceback.format_exc(),
                current_input=request.data,
                current_user=request.user
            ))
            CommonUtils.write_log_file(message)
            return Response({'response': {'msg': 'fail', 'error': str(e)}}, status=status.HTTP_400_BAD_REQUEST)

# Update Subscription with Pricing Plan
class SubscriptionUpdatePricePlan(APIView):
    serializer_class = UserAppSubscriptionSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        try:
            # Extract user from request
            the_user = request.user

            # Extract subscription_id from request data
            sel_subscription_id = request.data.get('subscription_id')
            sel_subscription_plan_id = request.data.get('plan_id')
            
            # Get subscription associated with the user and provided subscription_id
            subscription = UserAppSubscription.objects.filter(subscription_user=the_user, subscription_id=sel_subscription_id, is_active=True).first()
            subscription_plan = SubscriptionPlan.objects.filter(subscription_plan_id=sel_subscription_plan_id, subscription_plan_price__gt=0, is_active=True).first()
            if subscription and subscription_plan:
                subscription.subscription_plan=subscription_plan
                subscription.save()
                serializer = self.serializer_class(subscription)
                return Response({'response': {'msg': 'success', 'data': serializer.data}}, status=status.HTTP_200_OK)
            else:
                return Response({'response': {'msg': 'fail', 'error': 'Invalid Subscription ID / Plan ID'}}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            message = ("Error Date/Time:{current_time}\nURL:{current_url}\nError:{current_error}\n\{tb}\nCuurent Inputs:{current_input}\nUser:{current_user}".format(
                current_time=CommonUtils.current_date_time(),
                current_url=request.build_absolute_uri(),
                current_error=repr(e),
                tb=traceback.format_exc(),
                current_input=request.data,
                current_user=request.user
            ))
            CommonUtils.write_log_file(message)
            return Response({'response': {'msg': 'fail', 'error': str(e)}}, status=status.HTTP_400_BAD_REQUEST)
        
# Subscription Details
class SubscriptionDetails(APIView):
    serializer_class = UserAppSubscriptionSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        try:
            # Extract user from request
            the_user = request.user

            # Extract subscription_id from request data
            sel_subscription_id = request.data.get('subscription_id')

            # Get subscription associated with the user and provided subscription_id
            subscription = UserAppSubscription.objects.filter(subscription_user=the_user, subscription_id=sel_subscription_id).first()

            if subscription:
                serializer = self.serializer_class(subscription)
                return Response({'response': {'msg': 'success', 'data': serializer.data}}, status=status.HTTP_200_OK)
            else:
                return Response({'response': {'msg': 'fail', 'error': 'Invalid Subscription ID'}}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            message = ("Error Date/Time:{current_time}\nURL:{current_url}\nError:{current_error}\n\{tb}\nCuurent Inputs:{current_input}\nUser:{current_user}".format(
                current_time=CommonUtils.current_date_time(),
                current_url=request.build_absolute_uri(),
                current_error=repr(e),
                tb=traceback.format_exc(),
                current_input=request.data,
                current_user=request.user
            ))
            CommonUtils.write_log_file(message)
            return Response({'response': {'msg': 'fail', 'error': str(e)}}, status=status.HTTP_400_BAD_REQUEST)