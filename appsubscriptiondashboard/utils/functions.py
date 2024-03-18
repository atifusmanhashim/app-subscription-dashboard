#Firebase Cloud Messaging
from authapp.models import (LoginAnalytics,AppActionAnalytics)


# Used for Timezone / Datetime
from django.utils import timezone
from datetime import datetime
from datetime import datetime, date, timedelta

#Used for  Path (File Handling, Folders)
from pathlib import Path

import datetime
import math
import json
import os
import requests

from . import constants
from django.conf import settings

#URLLibrary Parsing
import urllib.parse

#=========================================== Common Functions ====================================
#Merge 2 Dictionaries
def merge_two_dicts(x, y):
    z = x.copy()   # start with keys and values of x
    z.update(y)    # modifies z with keys and values of y
    return z
#Getting Dictionary
def getList(dict): 
    
    return dict

#Date Validation Function
def validate(date_text):
    
    isValidDate = True
    date_string = date_text
    format = "%Y-%m-%d"
    try :
        datetime.datetime.strptime(date_string, format)
        isValidDate = True
    except ValueError :
        isValidDate = False

    if(isValidDate) :
        return True
    else :
       return False

def current_date():

    current_date=date.today()
    return current_date

def current_date_time():

    current_date_time=format(datetime.datetime.now(),constants.datetime_format)
    return current_date_time

def display_date_time(date_text):
    req_format = constants.datetime_format

    dt=format(date_text,req_format)
    return dt

def get_client_ip(request):

    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip_address = x_forwarded_for.split(',')[0]
    else:
        ip_address = request.META.get('REMOTE_ADDR')

    return ip_address

def get_ip():
    response = requests.get('https://api64.ipify.org?format=json').json()
    return response["ip"]

def get_location(sel_ip_address):
    #ip_address = get_client_ip(request)
    ip_address=sel_ip_address
    response = requests.get(f'https://ipapi.co/{ip_address}/json/').json()
    location_data = {
        "ip": ip_address,
        "city": response.get("city"),
        "region": response.get("region"),
        "country": response.get("country_name"),
        "latitude":response.get("latitude"),
        "longitude":response.get('longitude')
    }
    return location_data

def format_epoch_dtime(sel_time):
    if sel_time is not None:
        if type(sel_time)==int:
            epoch_time = sel_time
            epoch_time_len=len(str(sel_time))
            if epoch_time_len > 10:
                epoch_time=epoch_time/1000
                dt = datetime.datetime.utcfromtimestamp(epoch_time).strftime(constants.datetime_format)
            else:
                epoch_time=epoch_time
                dt = datetime.datetime.utcfromtimestamp(epoch_time).strftime(constants.datetime_format)
        else:
            dt=None
    else:
        dt=None
    return dt

#=========================================== Pagination ====================================
#Used for Pagination
def pagination(request):

    
    if 'page' in request.data:
        page = int(request.data.get('page', 1))
    else:
        page = 1

    if 'reqRecs' in request.data:
        reqRecs=int(request.data.get('reqRecs',10))
    else:
        reqRecs=10

    startpage=(page-1)*reqRecs
    endpage=page*reqRecs
    #================================End of Pagination ===============================

    result={'start':startpage,'end':endpage,'page':page,'reqRecs':reqRecs}
    return result

#Getting Total Pages
def get_total_pages (sel_total_records, sel_req_records):

    if sel_total_records > 0 and sel_req_records > 0:
        total_pages=int(math.ceil(sel_total_records/sel_req_records))
        if total_pages==0:
            total_pages=1
    else:
        total_pages=0

    return total_pages

#=========================================== End of Pagination ====================================

#=========================================== Error Logs ===========================================
log_dir_path=os.path.join(Path().absolute().parent,'log/error_logs')

def write_log_file(sel_text):
    log_file_name=str(current_date()) + '.log'
    log_file_path=os.path.join(log_dir_path,log_file_name)
    sel_file = log_file_path

    if sel_file is not None:
        

        file=open(sel_file,"a+")
       
            
        if sel_text is not None:
            file.write('\n')
            file.write(sel_text)
            file.close()
    return True
#=========================================== Error Logs ===========================================



#=========================================== Analytics =====================================
#Saving Analytics
def save_analytics(sel_user,sel_action,request):

    data=request.data
    device_ip=get_client_ip(request)


    analytics=AppActionAnalytics.objects.create(user=sel_user,
                                                       action=sel_action,
                                                       search_params=request.data,
                                                       device_ip=device_ip
                                                       )


    return True

#Saving Login Analytics
def save_login_analytics(sel_user,sel_action,sel_source,request):

    data=request.data
    app_version = data.get('app_version', None)
    platform= data.get('platform', None)
    brand= data.get('brand', None)
    device= data.get('device_id', None)
    device_model= data.get('device_model', None)
    device_ip=get_client_ip(request)

    #user_ip_address=get_ip()
    location_data=get_location(device_ip)
    city_name=location_data['city']
    country_name=location_data['country']
    region_name=location_data['region']
    location_latitude=location_data['latitude']
    location_longitude=location_data['longitude']


    login_analytics=LoginAnalytics.objects.create(user=sel_user,action=sel_action,
                                source=sel_source)



    return True

#=========================================== Analytics =====================================

# ========================================== URL Parsing ==========================================
def get_url_query_params(sel_url):
    if sel_url is not None:
        parse_url=urllib.parse.urlparse(sel_url)
        parse_url_query=parse_url.query
        parse_url_query_params=urllib.parse.parse_qs(parse_url_query)
        query_params=parse_url_query_params
    else:
        query_params=[]
    return query_params
# ========================================== End of URL Parsing ==========================================

