import smtplib
import os
from icalendar import Calendar, Event
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

def create_ics(meeting_details):
    """
    Generates an ICS file content string.
    """
    cal = Calendar()
    cal.add('prodid', '-//Voice-to-Cal//mxm.dk//')
    cal.add('version', '2.0')
    
    event = Event()
    event.add('summary', meeting_details['summary'])
    event.add('dtstart', meeting_details['start_time'])
    event.add('dtend', meeting_details['end_time'])
    
    cal.add_component(event)
    return cal.to_ical()

def send_email(recipient_email, meeting_details, sender_email=None):
    """
    Sends an email with ICS attachment using Scaleway TEM (SMTP).
    """
    # Scaleway TEM Creds
    smtp_server = "smtp.tem.scaleway.com"
    smtp_port = 587
    smtp_username = os.environ.get('SCW_ACCESS_KEY')
    smtp_password = os.environ.get('SCW_SECRET_KEY')
    
    if not sender_email:
        # Default sender must be verified in Scaleway TEM
        sender_email = os.environ.get('SENDER_EMAIL', 'noreply@example.com')

    ics_data = create_ics(meeting_details)
    
    msg = MIMEMultipart()
    msg['Subject'] = f"Invitation: {meeting_details['summary']}"
    msg['From'] = sender_email
    msg['To'] = recipient_email
    
    # Body
    body_text = f"Here is your meeting invite for '{meeting_details['summary']}'."
    msg.attach(MIMEText(body_text, 'plain'))
    
    # Attachment
    part = MIMEApplication(ics_data, Name='invite.ics')
    part['Content-Disposition'] = 'attachment; filename="invite.ics"'
    msg.attach(part)
    
    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_username, smtp_password)
            server.send_message(msg)
        return True, "Email sent successfully via Scaleway TEM"
    except Exception as e:
        return False, str(e)
