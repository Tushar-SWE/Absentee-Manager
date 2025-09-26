import os
import sys
import pandas as pd
import requests
import urllib.parse
from dotenv import load_dotenv

load_dotenv()

# ==== API KEY ====
BREVO_API_KEY = os.getenv("BREVO_API_KEY")

# ==== API LIMIT ====
BREVO_LIMIT = 300
brevo_count = 0


# ==== SMS FUNCTION ====
def send_sms(name, phone, days_absent):
    if not phone or str(phone).strip() == '':
        print(f"⚠️ Skipping SMS - Missing phone for {name}")
        return

    params = {
        "user": "demoac",
        "password": "123123",
        "senderid": "ANUREN",
        "channel": "Trans",
        "DCS": "0",
        "flashsms": "0",
        "number": str(phone).strip(),
        "text": f"Dear {name}, you have been absent for {days_absent} consecutive days. Please report or contact your supervisor. ANURAG ENTERPRISES",
        "route": "02",
        "peid": "1601563160128923382",
        "DLTTemplateId": "1707175248465465981"
    }

    try:
        encoded = urllib.parse.urlencode(params, safe='')
        response = requests.get(f"http://smsfortius.in/api/mt/SendSMS?{encoded}")
        print(f"📤 SMS sent to {name} ({phone}): {response.text}")
    except Exception as e:
        print(f"❌ SMS failed for {name} ({phone}): {e}")


def send_bulk_sms_from_report(filepath, days_absent):
    try:
        df = pd.read_excel(filepath, engine='openpyxl')
        name_col = next((col for col in df.columns if 'name' in col.lower()), None)
        phone_col = next((col for col in df.columns if 'phone' in col.lower()), None)

        if not name_col or not phone_col:
            print(f"❌ Columns 'Name' or 'Phone' not found in: {filepath}")
            return

        print(f"\n📨 Sending SMS to {days_absent}-Day Absentees from: {filepath}")
        for _, row in df.iterrows():
            name = str(row.get(name_col, "Employee")).strip()
            phone = str(row.get(phone_col, "")).strip()
            send_sms(name, phone, days_absent)

    except Exception as e:
        print(f"❌ Failed to process SMS report: {e}")


# ==== EMAIL FUNCTION (BREVO ONLY) ====
def send_email_brevo(name, to_email, subject, message):
    global brevo_count
    if brevo_count >= BREVO_LIMIT:
        print(f"⏳ Email NOT sent to {name} ({to_email}) – Brevo limit reached.")
        return False

    headers = {
        "accept": "application/json",
        "api-key": BREVO_API_KEY,
        "content-type": "application/json"
    }
    data = {
        "sender": {"name": "Aquamart HR", "email": "sumitsin712@gmail.com"},
        "to": [{"email": to_email, "name": name}],
        "subject": subject,
        "textContent": message
    }

    try:
        response = requests.post("https://api.brevo.com/v3/smtp/email", headers=headers, json=data)
        if response.status_code == 201:
            brevo_count += 1
            print(f"📤 Brevo Email sent to {name} ({to_email})")
            return True
        else:
            print(f"❌ Brevo error for {name} ({to_email}): {response.text}")
            return False
    except Exception as e:
        print(f"❌ Brevo exception for {name}: {e}")
        return False


def send_bulk_email_from_report(filepath, days_absent):
    try:
        df = pd.read_excel(filepath, engine='openpyxl')
        name_col = next((col for col in df.columns if 'name' in col.lower()), None)
        email_col = next((col for col in df.columns if 'email' in col.lower()), None)

        if not name_col or not email_col:
            print(f"❌ Columns 'Name' or 'Email' not found in: {filepath}")
            return

        print(f"\n📧 Sending EMAIL to {days_absent}-Day Absentees from: {filepath}")

        for _, row in df.iterrows():
            name = str(row.get(name_col, "Employee")).strip()
            email = str(row.get(email_col, "")).strip()
            if not email:
                continue

            if days_absent == 6:
                subject = "6-Day Absence Warning"
                message = (
                    f"Dear {name},\n\n"
                    "You have been absent for 6 consecutive days.\n"
                    "This is a formal warning. Please report to your supervisor immediately.\n\n– Aquamart HR"
                )
            elif days_absent == 10:
                subject = "10-Day Absence – Separation Notice"
                message = (
                    f"Dear {name},\n\n"
                    "You have been absent fo`r 10 consecutive days without official communication.\n"
                    "As per company policy, this may be treated as job abandonment. Please contact HR immediately.\n\n– Aquamart HR"
                )
            else:
                continue

            send_email_brevo(name, email, subject, message)

    except Exception as e:
        print(f"❌ Failed to process email report: {e}")


# ==== Main Notification Function ====
def send_notifications_for_department_and_date(department, date_str):
    results = []

    # 📂 Reports are saved locally in this folder
    base_dir = os.path.join("data", "absentee_reports", department)

    try:
        for days in [3, 6, 10]:
            filename = f"{days}_Consecutive_Absentees_{date_str}.xlsx"
            local_path = os.path.join(base_dir, filename)

            if os.path.exists(local_path):
                if days == 3:
                    # send_bulk_sms_from_report(local_path, 3)
                    results.append("3-day SMS report ✅")
                else:
                    send_bulk_email_from_report(local_path, days)
                    results.append(f"{days}-day email report ✅")
            else:
                results.append(f"{days}-day report ❌ not found")

    except Exception as e:
        print(f"⚠️ Error while sending notifications: {e}")

    return results


# ==== CLI Execution ====
if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("❌ Usage: python notify.py <department> <dd.mm.yyyy>")
        sys.exit(2)

    department = sys.argv[1]
    date_str = sys.argv[2]

    send_notifications_for_department_and_date(department, date_str)
