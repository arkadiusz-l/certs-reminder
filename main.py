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
soon_expiring_certs = []
message_content = ""
DAYS = 7


def send_email():
    smtp_server = "mail.inbox.lv"
    port = 465
    sender_email = "wlucert556@mail.lv"
    receiver_email = "wlucert556@mail.lv"
    password = "VxKp4sBW2?"

    message = EmailMessage()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = "Expiring certificates"
    message.set_content(message_content)
    message.set_charset("utf-8")
    context = ssl.create_default_context()

    with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
        server.login(sender_email, password)
        server.send_message(message)
        print("The e-mail has been sent.")


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
            cert = f"{name} - expires today"
            soon_expiring_certs.append(cert)
        elif 0 < days_to_expire <= 7:
            cert = f"{name} - expires in {days_to_expire} days ({date})"
            soon_expiring_certs.append(cert)
        elif days_to_expire < 0:
            cert = f"{name} - expired {-days_to_expire} days ago ({date})"
            expired_certs.append(cert)


def get_expired_certs_str(expired_certs: list) -> str:
    expired_certs_str = ""
    for expired_cert in expired_certs:
        expired_certs_str += expired_cert + "\n"
    return expired_certs_str


def get_expiring_soon_certs_str(expiring_certs: list) -> str:
    soon_expiring_certs_str = ""
    for soon_expiring_cert in expiring_certs:
        soon_expiring_certs_str += soon_expiring_cert + "\n"
    return soon_expiring_certs_str


if __name__ == '__main__':
    if expired_certs or soon_expiring_certs:
        if expired_certs:
            expired_certs_str = get_expired_certs_str(expired_certs=expired_certs)
            message_content += f"""
        Certificates that have expired:
        {expired_certs_str}
        """
            print(f"Certificates that have expired: \n{expired_certs_str}")
        if soon_expiring_certs:
            soon_expiring_certs_str = get_expiring_soon_certs_str(expiring_certs=soon_expiring_certs)
            message_content += f"""
            Certificates that will expire in the next {DAYS} days:
        {soon_expiring_certs_str}
        """
            print(f"Certificates that will expire in the next {DAYS} days: \n{soon_expiring_certs_str}")
        send_email()
    else:
        print("All certificates are current.")
