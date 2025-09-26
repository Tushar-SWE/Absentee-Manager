import os
import calendar

def get_month_name(month_num):
    return calendar.month_name[month_num]

def ensure_folder(path):
    os.makedirs(path, exist_ok=True)
