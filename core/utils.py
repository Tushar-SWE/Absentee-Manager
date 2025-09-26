# core/utils.py

import pandas as pd
from datetime import datetime
import calendar
import os

def get_month_name(month_num):
    """Returns full month name from month number"""
    return calendar.month_name[month_num]

def ensure_folder(path):
    """Creates folder if it does not exist"""
    if not os.path.exists(path):
        os.makedirs(path)

def is_valid_date(date_str):
    """Checks if a string is a valid date in dd.mm.yyyy format."""
    try:
        datetime.strptime(date_str, "%d.%m.%Y")
        return True
    except ValueError:
        return False

def preprocess_sundays(df, id_column="Ticket. No."):
    """Fills all Sunday columns with 'SL' for valid rows."""
    for col in df.columns:
        if is_valid_date(str(col)):
            try:
                date_obj = datetime.strptime(str(col), "%d.%m.%Y")
                if date_obj.weekday() == 6:  # Sunday
                    df[col] = df.apply(
                        lambda row: 'SL' if pd.notna(row[id_column]) and str(row[id_column]).strip() != ''
                        and (pd.isna(row[col]) or str(row[col]).strip() == '')
                        else row[col],
                        axis=1
                    )
            except:
                pass
    return df

def highlight_absent_cells(row, absent_dates):
    """Highlights cells yellow where the employee was absent."""
    return [
        'background-color: yellow' if col in absent_dates and str(row[col]).strip().upper() == 'A'
        else ''
        for col in row.index
    ]

def get_consec_count_excl_sundays(row, df, current_date, max_backtrack_days=20):
    """Counts consecutive 'A' statuses excluding Sundays."""
    valid_dates = [col for col in df.columns if is_valid_date(col)]
    valid_dates_sorted = sorted(valid_dates, key=lambda d: datetime.strptime(d, "%d.%m.%Y"))

    if current_date not in valid_dates_sorted:
        return 0, []

    idx = valid_dates_sorted.index(current_date)
    consec_absent_dates = []
    i = idx

    while i >= 0 and len(consec_absent_dates) < max_backtrack_days:
        date = valid_dates_sorted[i]
        status = str(row.get(date, '')).strip().upper()

        if status == 'SL':
            i -= 1
            continue
        elif status == 'A':
            consec_absent_dates.append(date)
        else:
            break
        i -= 1

    return len(consec_absent_dates), list(reversed(consec_absent_dates))
