from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from email.mime.application import MIMEApplication
import smtplib
import re, os
from datetime import datetime
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
from urllib.parse import urlparse

from google_books.settings import EMAIL_HOST_USER, EMAIL_HOST_PASSWORD

def invalid_mobile_numbers_list():
    try:
        nums = [ str(i) for i in range(10)]
        p1= ''.join(nums)
        temp=[]
        temp.append(p1)
        temp.append(p1[::-1])
        for i in nums:
            temp.append(''.join([i]*10))
            for j in nums:
                if i!=j:
                    p = f"{i}{j*9}"
                    temp.append(p)
                    temp.append(p[::-1])
        return temp
    except Exception as e:
        print(str(e))

# Mobile Numbers Validation.
def mobile_number_validator(mobile_number,invalid_numbers = invalid_mobile_numbers_list()):
    try:
        mobile_number = str(mobile_number).replace(' ','')
        mobile_number = re.sub(r'\D', '', str(mobile_number))
        
        # mobile_number = re.sub(r'[+\-_ ]', '', mobile_number)
        if len(mobile_number)==12 and (mobile_number.startswith('91') or mobile_number.startswith('00')):
            mobile_number = mobile_number[2:]
        elif len(mobile_number)==11 and mobile_number.startswith('0'):
            mobile_number = mobile_number[1:]
        elif len(mobile_number)==13 and mobile_number.startswith('091'):
            mobile_number = mobile_number[3:]
            
        if len(mobile_number)!=10 or mobile_number.isnumeric()==False:
            return False

        for i in range(5):
            if mobile_number.startswith(str(i)):
                return False

        if mobile_number in invalid_numbers:
            return False
        return True
    except Exception as e:
        print(str(e))

def email_validator(email):
    import re
    # pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    pattern = r'^[\w\.-]+(\+[\w\.-]+)?@[\w\.-]+\.\w+$'
    # re.match(pattern, email)
    if re.match(pattern, email):
        return True
    else:
        return False

def password_validator(password):
    if len(password) < 8:
        return False
    if not any(char.isupper() for char in password):
        return False
    if not re.search(r'[!@#$%^&*()_+{}\[\]:;<>,.?`~]', password):
        return False
    if not any(char.isdigit() for char in password):
        return False
    return True


def date_validator(date_str):
    try:
        if not re.match(r'^\d{4}-\d{2}-\d{2}$', date_str):
            return False
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        min_date = datetime(1900, 1, 1)
        if date_obj < min_date or date_obj > datetime.today():
            return False
        return True
    except:
        return False
    
def url_validator(url):
    try:
        validator = URLValidator()
        validator(url)
        parsed_url = urlparse(url)
        return bool(parsed_url.scheme) and bool(parsed_url.netloc)
    except ValidationError:
        return False
    

def send_otp_email(to_email, subject, otp, user_name):
    try:
        if not (to_email and subject and otp and user_name):
            return False
        
        additional_text = f"""Hi {user_name},

We received a request to reset your Books Buzz password. Please use the OTP below to proceed:

OTP: {otp}

This OTP expires in 5 minutes. If you didn't request this, please ignore this email.

Best,
The Books Buzz Team"""
        
        email_content = additional_text

        # Create MIMEText object for plain text content
        msgText = MIMEText(email_content, 'plain')
        mail = MIMEMultipart()
        mail.attach(msgText)

        # Set email subject, sender, and recipient
        mail['Subject'] = subject
        mail['From'] = EMAIL_HOST_USER
        mail['To'] = to_email

        # Connect to the SMTP server and send the email
        domain_info = ('smtp.gmail.com', 465)
        s = smtplib.SMTP_SSL(*domain_info)
        s.login(EMAIL_HOST_USER, EMAIL_HOST_PASSWORD)
        s.sendmail(EMAIL_HOST_USER, to_email, mail.as_string())
        s.quit()

        return True
    except Exception as e:
        print(e)
        return False


def send_welcome_email(to_email, subject, user_name):
    try:
        if not (to_email and subject and user_name):
            return False

        additional_text = f"""Dear {user_name},

Welcome to Books Buzz World!

Thank you for joining our vibrant community of book enthusiasts. We're thrilled to have you with us and are excited to share our passion for books with you. Whether you're here to discover new reads, share your favorite books, or connect with fellow book lovers, you've come to the right place.
Here's what you can do next:

- Explore: Dive into our curated collection of books across various genres.
- Share: Write reviews and share your thoughts on the books you've read.

As a new member, you'll receive personalized recommendations, exclusive previews, and access to our community events.

If you have any questions or need assistance, feel free to reach out to our support team at support@booksbuzzworld.com.
Happy Reading!

Best regards,
The Books Buzz World Team
"""
        
        email_content = additional_text

        # Create MIMEText object for plain text content
        msgText = MIMEText(email_content, 'plain')
        mail = MIMEMultipart()
        mail.attach(msgText)

        # Set email subject, sender, and recipient
        mail['Subject'] = subject
        mail['From'] = EMAIL_HOST_USER
        mail['To'] = to_email

        # Connect to the SMTP server and send the email
        domain_info = ('smtp.gmail.com', 465)
        s = smtplib.SMTP_SSL(*domain_info)
        s.login(EMAIL_HOST_USER, EMAIL_HOST_PASSWORD)
        s.sendmail(EMAIL_HOST_USER, to_email, mail.as_string())
        s.quit()

        return True
    except Exception as e:
        print(f"An error occurred: {e}")
        return False




