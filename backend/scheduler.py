from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from config import SMTP_SERVER, SMTP_PORT, EMAIL_ADDRESS, EMAIL_PASSWORD

scheduler = BackgroundScheduler()

def send_email(to_email, subject, body):
    """Send email notification"""
    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_ADDRESS
        msg['To'] = to_email
        msg['Subject'] = subject
        
        msg.attach(MIMEText(body, 'plain'))
        
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        
        text = msg.as_string()
        server.sendmail(EMAIL_ADDRESS, to_email, text)
        server.quit()
        
        print(f"Email sent to {to_email}")
        
    except Exception as e:
        print(f"Error sending email: {e}")

def schedule_emails(email, schedule):
    """Schedule email reminders for user's classes"""
    day_mapping = {
        'monday': 0, 'tuesday': 1, 'wednesday': 2, 
        'thursday': 3, 'friday': 4, 'saturday': 5, 'sunday': 6
    }
    
    for course in schedule:
        for class_time in course['schedule']:
            day = class_time['day'].lower()
            start_time = class_time['start']
            
            if day in day_mapping:
                # Schedule reminder 15 minutes before class
                hour, minute = map(int, start_time.split(':'))
                reminder_time = datetime.now().replace(hour=hour, minute=minute) - timedelta(minutes=15)
                
                subject = f"Class Reminder: {course['code']}"
                body = f"""
Hi there!

This is a reminder that your class is starting soon:

Course: {course['code']} - {course['title']}
Time: {start_time}
Room: {course['room']}
Instructor: {course['instructor']}

Don't be late!

Best regards,
Schedly
                """
                
                # Schedule weekly reminder
                scheduler.add_job(
                    func=send_email,
                    trigger=CronTrigger(
                        day_of_week=day_mapping[day],
                        hour=reminder_time.hour,
                        minute=reminder_time.minute
                    ),
                    args=[email, subject, body],
                    id=f"{email}_{course['code']}_{day}_{start_time}",
                    replace_existing=True
                )

# Start the scheduler
if not scheduler.running:
    scheduler.start()