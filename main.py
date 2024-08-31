import smtplib
import ssl
from datetime import date, datetime
from email.message import EmailMessage
from os import getenv
from time import strptime
from typing import List
from dotenv import load_dotenv

months = {
    "Jan.": "01",
    "Feb.": "02",
    "March": "03",
    "April": "04",
    "May": "05",
    "June": "06",
    "July": "07",
    "Aug.": "08",
    "Sept.": "09",
    "Oct.": "10",
    "Nov.": "11",
    "Dec.": "12",
}

today = date.today()
expired_certs = []
today_expiring_certs = []
soon_expiring_certs = []
message_content = ""
NEXT_DAYS = 7


def send_email() -> None:
    load_dotenv()
    smtp_server = getenv("SMTP_SERVER")
    smtp_port = int(getenv("SMTP_PORT"))
    sender_email = getenv("EMAIL")
    receiver_email = getenv("RECEIVER_EMAIL")
    sender_password = getenv("PASSWORD")

    message = EmailMessage()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = "Expiring certificates"
    message.set_content(message_content)
    message.set_charset("utf-8")
    context = ssl.create_default_context()

    with smtplib.SMTP_SSL(smtp_server, smtp_port, context=context) as server:
        server.login(sender_email, sender_password)
        server.send_message(message)
        print("The e-mail has been sent.")


def get_all_certs_from_file(filename: str) -> List[dict]:
    certs = []
    with open(filename) as file:
        for row in file:
            cert = parse_data(row)
            certs.append(cert)
    return certs


def get_date_of_expire(data: dict) -> datetime.date:
    date: str = data["year"] + "-" + data["month"] + "-" + data["day"]
    date = strptime(date, "%Y-%m-%d")
    date_of_expire: datetime.date = datetime(*date[:3]).date()
    return date_of_expire


def calculate_days_to_expire(date_of_expire: datetime.date) -> int:
    days_to_expire = date_of_expire - today  # if today, it returns no days..., only "0:00:00"
    days_to_expire = str(days_to_expire).split(",")[0].split(" ")[0]  # ... so this slicing doesn't work...
    if days_to_expire == "0:00:00":  # ... so we need to manually set the days
        days_to_expire = 0
    days_to_expire = int(days_to_expire)
    return days_to_expire


def create_expired_certs_str(expired_certs: list) -> str:
    expired_certs_str = ""
    for expired_cert in expired_certs:
        expired_certs_str += expired_cert + "\n"
    return expired_certs_str


def parse_data(cert: str) -> dict:
    name: str = cert.split(",")[0].split(";")[0]
    day: str = cert.split(";")[1].split(",")[0].split(" ")[1]
    month: str = cert.split(",")[0].split(";")[1].split(" ")[0]
    month: str = months[month]
    year: str = cert.split(",")[1].strip()
    return {
        "name": name,
        "day": day,
        "month": month,
        "year": year
    }


def parse_file(filename) -> List[str]:
    new_list_certs = []
    with open(filename) as file:
        for row in file:
            new_list_certs.append(row)
    return new_list_certs


def is_certificate_expired(days_to_expire) -> bool:
    if days_to_expire < 0:
        return True
    return False


def is_certificate_expiring_soon(days_to_expire) -> bool:
    if 0 < days_to_expire <= NEXT_DAYS:
        return True
    return False


def is_certificate_expiring_today(days_to_expire) -> bool:
    if days_to_expire == 0:
        return True
    return False


def create_message_content(certs: list, message_prefix: str) -> str:
    message_content = ""
    message_content += message_prefix
    for cert in certs:
        message_content += cert + "\n"
    return message_content


if __name__ == "__main__":
    certificates = parse_file("sample_data.csv")

    for certificate in certificates:
        data = parse_data(certificate)
        date_of_expire = get_date_of_expire(data=data)
        days_to_expire = calculate_days_to_expire(date_of_expire=date_of_expire)
        date = date_of_expire.strftime("%Y.%m.%d")

        if is_certificate_expiring_today(days_to_expire=days_to_expire):
            cert = f"{data['name']} - expires today"
            today_expiring_certs.append(cert)
        elif is_certificate_expiring_soon(days_to_expire=days_to_expire):
            cert = f"{data['name']} - expires in {days_to_expire} days ({date})"
            soon_expiring_certs.append(cert)
        elif is_certificate_expired(days_to_expire=days_to_expire):
            cert = f"{data['name']} - expired {-days_to_expire} days ago ({date})"
            expired_certs.append(cert)

    if today_expiring_certs:
        message_content += create_message_content(certs=today_expiring_certs,
                                                  message_prefix="Certificates that expire today:\n") + "\n"
    if expired_certs:
        message_content += create_message_content(certs=expired_certs,
                                                  message_prefix="Certificates that have expired:\n") + "\n"
    if soon_expiring_certs:
        message_content += create_message_content(certs=soon_expiring_certs,
                                                  message_prefix=f"Certificates that will expire in the next {NEXT_DAYS} days:\n") + "\n"

    if message_content:
        print(message_content)
        send_email()
    else:
        print("All certificates are current.")
