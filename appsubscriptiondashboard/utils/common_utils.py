from django.utils import timezone
from datetime import datetime, date, timedelta
from pathlib import Path
import datetime
import math
import json
import os
import requests
import pandas as pd
import urllib.parse

from django.conf import settings
from . import constants  # Import constants from constants.py

#For Getting Random String
from django.utils.crypto import get_random_string

class CommonUtils:
    def __init__(self):
        pass

    @staticmethod
    def merge_two_dicts(x, y):
        z = x.copy()
        z.update(y)
        return z

    @staticmethod
    def getList(dict): 
        return dict

    @staticmethod
    def validate(date_text):
        isValidDate = True
        date_string = date_text
        format = "%Y-%m-%d"
        try:
            datetime.datetime.strptime(date_string, format)
            isValidDate = True
        except ValueError:
            isValidDate = False

        return isValidDate

    @staticmethod
    def current_date():
        return date.today()

    @staticmethod
    def current_date_time():
        return format(datetime.datetime.now(), constants.datetime_format)

    @staticmethod
    def display_date_time(date_text):
        req_format = constants.datetime_format
        return format(date_text, req_format)

    @staticmethod
    def get_app_base_url(request):
        base_url_string = request.scheme + ":" + request.get_host()
        return base_url_string

    @staticmethod
    def get_client_ip(request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip_address = x_forwarded_for.split(',')[0]
        else:
            ip_address = request.META.get('REMOTE_ADDR')

        return ip_address

    @staticmethod
    def format_epoch_dtime(sel_time):
        if sel_time is not None:
            if type(sel_time) == int:
                epoch_time = sel_time
                epoch_time_len = len(str(sel_time))
                if epoch_time_len > 10:
                    epoch_time = epoch_time / 1000
                    dt = datetime.datetime.utcfromtimestamp(epoch_time).strftime(constants.datetime_format)
                else:
                    epoch_time = epoch_time
                    dt = datetime.datetime.utcfromtimestamp(epoch_time).strftime(constants.datetime_format)
            else:
                dt = None
        else:
            dt = None
        return dt

    @staticmethod
    def get_unique_no(start_str):
        new_unique_no=start_str+get_random_string(constants.code_random_string_length)
        return new_unique_no
    
    @staticmethod
    def pagination(request):
        if 'page' in request.data:
            page = int(request.data.get('page', 1))
        else:
            page = 1

        if 'reqRecs' in request.data:
            reqRecs = int(request.data.get('reqRecs', 10))
        else:
            reqRecs = 10

        startpage = (page - 1) * reqRecs
        endpage = page * reqRecs

        result = {'start': startpage, 'end': endpage, 'page': page, 'reqRecs': reqRecs}
        return result

    @staticmethod
    def get_total_pages(sel_total_records, sel_req_records):
        if sel_total_records > 0 and sel_req_records > 0:
            total_pages = int(math.ceil(sel_total_records / sel_req_records))
            if total_pages == 0:
                total_pages = 1
        else:
            total_pages = 0

        return total_pages

    @staticmethod
    def write_log_file(sel_text):
        log_dir_path = os.path.join(Path().absolute().parent, 'log/error_logs')
        log_file_name = str(CommonUtils.current_date()) + '.log'
        log_file_path = os.path.join(log_dir_path, log_file_name)
        sel_file = log_file_path

        if sel_file is not None:
            file = open(sel_file, "a+")
            if sel_text is not None:
                file.write('\n')
                file.write(sel_text)
                file.close()
        return True

    @staticmethod
    def download_excel_path():
        excel_file_path = str(os.path.join(Path(__file__).absolute().parent.parent)) + "/excel_data"
        if not os.path.isdir(excel_file_path):
            os.makedirs(excel_file_path)
        return excel_file_path

    @staticmethod
    def delete_existing_csv():
        try:
            excel_file_path = CommonUtils.download_excel_path()
            excel_file_lst = list(os.listdir(excel_file_path))
            if len(excel_file_lst) > 0:
                for file_name in excel_file_lst:
                    file_path = os.path.join(excel_file_path, file_name)
                    os.remove(file_path)
            return True
        except:
            return False

    @staticmethod
    def get_url_query_params(sel_url):
        if sel_url is not None:
            parse_url = urllib.parse.urlparse(sel_url)
            parse_url_query = parse_url.query
            parse_url_query_params = urllib.parse.parse_qs(parse_url_query)
            query_params = parse_url_query_params
        else:
            query_params = []
        return query_params
