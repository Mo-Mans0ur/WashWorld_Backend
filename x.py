from time import time

from flask import request, make_response, Blueprint
import smtplib
import mysql.connector
import uuid
import re  # Regular expressions
from functools import wraps
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


bp = Blueprint("x", __name__)

##############################
import os
import mysql.connector

def db():
    try:
        # Connects to the database and returns the connection and cursor.
        connection = mysql.connector.connect(
            host="mariadb",
            user=os.environ["MYSQL_USER"],
            password=os.environ["MYSQL_PASSWORD"],
            database=os.environ["MYSQL_DATABASE"]
        )
        cursor = connection.cursor(dictionary=True)
        return connection, cursor
    except Exception as e:
        print(e, flush=True)
        raise Exception("Database under maintenance", 500)

##############################

"""REGEX_USER_EMAIL = "^(([^<>()[\]\\.,;:\s@\"]+(\.[^<>()[\]\\.,;:\s@\"]+)*)|(\".+\"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$"""
REGEX_USER_EMAIL = "^(?:@a|@b|[^@\s]+@(?:[a-zA-Z0-9-]+.)+[a-zA-Z]{2,})$"


def validate_user_email():
    # Checks if the user email has a valid format.
    user_email = request.form.get("user_email", "").strip()
    if not re.match(REGEX_USER_EMAIL, user_email):
        raise Exception("company_exception user_email")
    return user_email


##############################
USER_FIRST_NAME_MIN = 2
USER_FIRST_NAME_MAX = 20
USER_FIRST_NAME_REGEX = f"^.{{{USER_FIRST_NAME_MIN},{USER_FIRST_NAME_MAX}}}$"


def validate_user_first_name():
    # Checks if the first name is the right length.
    user_first_name = request.form.get("user_first_name", "").strip()
    if not re.match(USER_FIRST_NAME_REGEX, user_first_name):
        raise Exception(f"--error-- user_first_name")

    return user_first_name


##############################
USER_LAST_NAME_MIN = 2
USER_LAST_NAME_MAX = 20


def validate_user_last_name():
    # Checks if the last name is the right length.
    user_last_name = request.form.get("user_last_name", "").strip()
    if len(user_last_name) < USER_LAST_NAME_MIN:
        raise Exception(
            f"User last name minimum {USER_LAST_NAME_MIN} characters", 400)
    if len(user_last_name) > USER_LAST_NAME_MAX:
        raise Exception(
            f"User last name maximum {USER_LAST_NAME_MAX} characters", 400)
    return user_last_name


##############################
USER_USERNAME_MIN = 2
USER_USERNAME_MAX = 20
USER_USERNAME_REGEX = f"^.{{{USER_USERNAME_MIN},{USER_USERNAME_MAX}}}$"


def validate_user_username():
    # Checks if the username is the right length.
    user_username = request.form.get("user_username", "").strip()
    if not re.match(USER_USERNAME_REGEX, user_username):
        raise Exception("--error-- user_username")
    return user_username


##############################
def no_cache(view):
    # Adds headers so the browser does not cache the page.
    @wraps(view)
    def no_cache_view(*args, **kwargs):
        response = make_response(view(*args, **kwargs))
        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        return response
    return no_cache_view


###############################
USER_PASSWORD_MIN = 8
USER_PASSWORD_MAX = 50
REGEX_USER_PASSWORD = f"^.{{{USER_PASSWORD_MIN},{USER_PASSWORD_MAX}}}$"


def validate_user_password():
    # Checks if the user password is the right length.
    user_password = request.form.get("user_password", "").strip()
    if not re.match(REGEX_USER_PASSWORD, user_password):
        raise Exception("company_exception user_password")
    return user_password

###############################
CAR_NUMBER_PLATE_REGEX = r"^[A-Z]{2}[0-9]{6}$"

def validate_car_number_plate():
    # Checks if the car number plate matches the expected format.
    car_number_plate = str(car_number_plate or "").strip().upper().replace(" ", "")

    if not re.match(CAR_NUMBER_PLATE_REGEX, car_number_plate):
        raise Exception("company_exception car_number_plate")
    
    return car_number_plate


###############################
########## E-Mail #############
###############################



def send_verification_email(receiver_email, firstname, verification_key):
    # Sends an email with a link the user can click to verify their account.
    try:    
        # Create a gmail 
        # Enable (turn on) 2 step verification/factor in the google account manager
        # Visit: https://myaccount.google.com/apppasswords
        # Copy the key :
 
        # Email and password of the sender's Gmail account
        sender_email = "washworldtest2026@gmail.com"
        password = "cfbx erul ezpe ksuj"  # If 2FA is on, use an App Password instead

        verification_link = f"http://127.0.0.1:80/api/auth/verify/{verification_key}"
 
        # Receiver email address
        receiver_email = receiver_email
        
        # Create the email message
        message = MIMEMultipart()
        message["From"] = "Washworld <washworldtest2026@gmail.com>"
        message["To"] = receiver_email
        message["Subject"] = "Please verify your account"
 
        # Body of the email
        body = f"""<div style="font-family: Gilroy, Arial, sans-serif; line-height: 1.5; color: #333; padding: 20px; background-color: #f9f9f9; border-radius: 10px; max-width: 600px; margin: auto;">
                <h1>Welcome to WashWorld</h1>
                    <h1>Hi {firstname}</h1>
                    
                    <p>We're excited to have you on board. Please verify your account to get started.</p>

                    <p>You can verify your account by clicking the link below:</p>
                    <h2>
                        <a href="{verification_link}" 
                            style="
                            display: inline-block; 
                            background-color: #06C167; 
                            color: white; 
                            padding: 10px 8px; 
                            text-decoration: none; 
                            font-weight: bold;
                        
                        
                            ">
                            Verify Account
                        </a>
                        
                    </h2>

                    <p>If the button above does not work, please copy and paste the following link into your browser:</p>
                    <p><a href="{verification_link}">{verification_link}</a></p>
                   </div>"""
        message.attach(MIMEText(body, "html"))
 
        # Connect to Gmail's SMTP server and send the email
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()  # Upgrade the connection to secure
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, message.as_string())
        print("Verification email sent successfully!", flush=True)
 
        return "email sent"
       
    except Exception as ex:
        print(ex, flush=True)
        raise Exception("Failed to send verification email", 500)

###############################

REGEX_RESET_PASSWORD_KEY = r"^[a-f0-9]{64}:[0-9]{10}$"
RESET_PASSWORD_TTL_SECONDS = 900 # 15 minutes

def validate_reset_password_key(reset_key):
    # Checks if the reset password key has the correct format.
    reset_key = str(reset_key).strip()
    if not re.match(REGEX_RESET_PASSWORD_KEY, reset_key):
        raise Exception("company_exception reset_password_key invalid")
    return reset_key


def make_reset_password_key():
    # Creates a reset password key with an expiry time.
    random_key = uuid.uuid4().hex + uuid.uuid4().hex
    expires_at = int(time()) + RESET_PASSWORD_TTL_SECONDS
    return f"{random_key}:{expires_at}"


def parse_reset_password_key(reset_key):
    # Splits the reset password key into the random key and expiry time.
    reset_key = validate_reset_password_key(reset_key)

    random_key, expires_at = reset_key.split(":")
    expires_at = int(expires_at)

    return random_key, expires_at


def is_reset_password_key_expired(reset_key):
    # Checks if the reset password key has expired.
    reset_key_parts = parse_reset_password_key(reset_key)
    expires_at = reset_key_parts[1]
    return int(time()) > expires_at

###########################
REGEX_EMAIL = "^(?:@a|@b|[^@\\s]+@(?:[a-zA-Z0-9-]+\\.)+[a-zA-Z]{2,})$"


def validate_email(email):
    # Checks if an email has a valid format.
    email = email.strip()
    if not re.match(REGEX_EMAIL, email):
        raise Exception("company_exception email")
    return email

def send_reset_password_email(receiver_email, firstname, reset_key):
    # Sends an email with a link the user can click to reset their password.
    try:
        sender_email = "washworldtest2026@gmail.com"
        password = "cfbx erul ezpe ksuj"

        reset_link = f"http://localhost:3000/reset-password/confirm?key={reset_key}"

        message = MIMEMultipart()
        message["From"] = "Washworld <washworldtest2026@gmail.com>"
        message["To"] = receiver_email
        message["Subject"] = "Nulstil din adgangskode"

        body = f"""<div style="font-family: Gilroy, Arial, sans-serif; line-height: 1.5; color: #333; padding: 20px; background-color: #f9f9f9; border-radius: 10px; max-width: 600px; margin: auto;">
                <h1>WashWorld</h1>
                <h1>Hej {firstname}</h1>

                <p>Vi har modtaget en anmodning om at nulstille adgangskoden til din WashWorld-konto.</p>
                <p>Klik på knappen nedenfor for at vælge en ny adgangskode. Linket udløber om 15 minutter.</p>

                <h2>
                    <a href="{reset_link}"
                        style="
                        display: inline-block;
                        background-color: #06C167;
                        color: white;
                        padding: 10px 8px;
                        text-decoration: none;
                        font-weight: bold;
                        ">
                        Nulstil adgangskode
                    </a>
                </h2>

                <p>Hvis knappen ikke virker, kopiér og indsæt dette link i din browser:</p>
                <p><a href="{reset_link}">{reset_link}</a></p>

                <p>Hvis du ikke har anmodet om at nulstille din adgangskode, kan du se bort fra denne email.</p>
               </div>"""
        message.attach(MIMEText(body, "html"))

        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, message.as_string())
        print("Reset password email sent successfully!", flush=True)

        return "email sent"

    except Exception as ex:
        print(ex, flush=True)
        raise Exception("Failed to send reset password email", 500)

############################
USER_PASSWORD_MIN = 8
USER_PASSWORD_MAX = 50
REGEX_USER_PASSWORD = f"^.{{{USER_PASSWORD_MIN},{USER_PASSWORD_MAX}}}$"


def validate_user_password(password):
    # Checks if a password is the right length.
    user_password = password.strip()
    if not re.match(REGEX_USER_PASSWORD, user_password):
        raise Exception("company_exception user_password")
    return user_password
