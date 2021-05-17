from datetime import datetime
import email
import smtplib
import requests


def create_session_info(center, session):
    return(
        {"name": center["name"],
         "date": session["date"],
         "slots": session["available_capacity"],
         "age_limit": session["min_age_limit"]}
    )


def get_session(data):
    for center in data["centers"]:
        for session in center["sessions"]:
            yield create_session_info(center, session)


def is_available(session):
    return(session["slots"] > 0)


def get_slot_7_days(start_date):
    url = "https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/calendarByDistrict"
    params = {"district_id": 307, "date": start_date.strftime("%d-%m-%Y")}
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0"}
    res = requests.get(url, params=params, headers=headers)
    data = res.json()
    return(session for session in get_session(data) if is_available(session))


def create_output(session_info):
    return(f"{session_info['date']} - {session_info['name']} ({session_info['slots']})")


content = "\n".join([create_output(session_info)
                     for session_info in get_slot_7_days(datetime.today())])


username = "Enter your email"
password = "Enter your password"
if not content:
    print("No availability")
else:
    email_msg = email.message.EmailMessage()
    email_msg["Subject"] = "Vaccination slot open"
    email_msg["From"] = username
    email_msg["To"] = username
    email_msg.set_content(content)

    with smtplib.SMTP(host="smtp.gmail.com", port="587") as server:
        server.starttls()
        server.login(username, password)
        server.send_message(email_msg, username, username)
