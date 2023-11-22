from email.message import EmailMessage
from datetime import date, datetime
from time import strptime
import smtplib
import ssl

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
expired_certs_str = ""
expire_certs_7_days = []
expire_certs_7_days_str = ""


def send_email():
    smtp_server = "xxxxx"
    port = 465
    sender_email = "xxxxx"
    receiver_email = "xxxxx"
    password = "xxxxx"

    message = EmailMessage()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = "Wygasąjace certyfikaty"
    message.set_content(f"""
        Certyfikaty, które wygasły:
        {expired_certs_str}
        Certyfikaty, które wygasają w ciągu najbliższych 7 dni:
        {expire_certs_7_days_str}
        """)
    message.set_charset("utf-8")
    context = ssl.create_default_context()

    with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
        server.login(sender_email, password)
        server.send_message(message)
        print("Email został wysłany.")


with open("sample_data.csv") as file:
    for row in file:
        name: str = row.split(",")[0].split(";")[0]
        day: str = row.split(";")[1].split(",")[0].split(" ")[1]
        month: str = row.split(",")[0].split(";")[1].split(" ")[0]
        month: str = months[month]
        year: str = row.split(",")[1].strip()
        date: str = year + "-" + month + "-" + day
        date = strptime(date, "%Y-%m-%d")
        date_of_expire: datetime.date = datetime(*date[:3]).date()
        calculate_days_to_expire = date_of_expire - today
        days_to_expire = str(calculate_days_to_expire).split(",")[0].split(" ")[0]
        date = date_of_expire.strftime('%Y.%m.%d')
        if days_to_expire == "0:00:00":
            days_to_expire = 0

        days_to_expire = int(days_to_expire)
        if days_to_expire == 0:
            cert = f"{name} - wygasa dzisiaj"
            expire_certs_7_days.append(cert)
        elif 0 < days_to_expire <= 7:
            cert = f"{name} - wygasa za {days_to_expire} dni ({date})"
            expire_certs_7_days.append(cert)
        elif days_to_expire < 0:
            cert = f"{name} - wygasł {-days_to_expire} dni temu ({date})"
            expired_certs.append(cert)

for expired_cert in expired_certs:
    expired_certs_str += expired_cert + "\n"

for expire_cert in expire_certs_7_days:
    expire_certs_7_days_str += expire_cert + "\n"

if len(expired_certs) > 0:
    print(f"Certyfikaty, które wygasły: \n{expired_certs_str}")
    print(f"Certyfikaty, które wygasają w ciągu najbliższych 7 dni: \n{expire_certs_7_days_str}")
    send_email()
else:
    print("Wszystkie certyfikaty są aktualne.")
