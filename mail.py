import smtplib  
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587 
SENDER_EMAIL = "tummalasowmya2018@gmail.com"
SENDER_PASSWORD = "pzfm niqj xkpc xsgc"  


def send_email(to_email,subject,body):
    try:
        msg = MIMEMultipart()
        msg["From"] = SENDER_EMAIL
        msg["To"] = to_email
        msg["Subject"] = subject
        body = body
        msg.attach(MIMEText(body, "plain")) 


        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, to_email, msg.as_string())
        server.quit()

        print(f"Email sent to {to_email}")
        return True

    except Exception as e:
        print(f"Error sending email to {to_email}: {e}")
        return False



