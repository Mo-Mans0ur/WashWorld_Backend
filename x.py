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
    user_email = request.form.get("user_email", "").strip()
    if not re.match(REGEX_USER_EMAIL, user_email):
        raise Exception("company_exception user_email")
    return user_email


##############################
USER_FIRST_NAME_MIN = 2
USER_FIRST_NAME_MAX = 20
USER_FIRST_NAME_REGEX = f"^.{{{USER_FIRST_NAME_MIN},{USER_FIRST_NAME_MAX}}}$"


def validate_user_first_name():
    user_first_name = request.form.get("user_first_name", "").strip()
    if not re.match(USER_FIRST_NAME_REGEX, user_first_name):
        raise Exception(f"--error-- user_first_name")

    return user_first_name


##############################
USER_LAST_NAME_MIN = 2
USER_LAST_NAME_MAX = 20


def validate_user_last_name():
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
    user_username = request.form.get("user_username", "").strip()
    if not re.match(USER_USERNAME_REGEX, user_username):
        raise Exception("--error-- user_username")
    return user_username


##############################
def no_cache(view):
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
    user_password = request.form.get("user_password", "").strip()
    if not re.match(REGEX_USER_PASSWORD, user_password):
        raise Exception("company_exception user_password")
    return user_password

###############################
CAR_NUMBER_PLATE_REGEX = r"^[A-Z]{2}[0-9]{6}$"

def validate_car_number_plate():
    car_number_plate = request.form.get("car_number_plate", "").strip().upper()
    if not re.match(CAR_NUMBER_PLATE_REGEX, car_number_plate):
        raise Exception("company_exception car_number_plate")
    return car_number_plate

##############################
CAR_MODEL_MIN = 2
CAR_MODEL_MAX = 20
CAR_MODEL_REGEX = f"^.{{{CAR_MODEL_MIN},{CAR_MODEL_MAX}}}$"

def validate_car_model():
    car_model = request.form.get("car_model", "").strip()
    if not re.match(CAR_MODEL_REGEX, car_model):
        raise Exception("company_exception car_model")
    return car_model

##############################
CAR_BRAND_MIN = 2
CAR_BRAND_MAX = 20
CAR_BRAND_REGEX = f"^.{{{CAR_BRAND_MIN},{CAR_BRAND_MAX}}}$"

def validate_car_brand():
    car_brand = request.form.get("car_brand", "").strip()
    if not re.match(CAR_BRAND_REGEX, car_brand):
        raise Exception("company_exception car_brand")
    return car_brand
###############################
CAR_YEAR_MIN = 1900
CAR_YEAR_MAX = 2026
def validate_car_year():
    try:
        car_year = int(request.form.get("car_year", "").strip())
    except ValueError:
        raise Exception("company_exception car_year")
    if car_year < CAR_YEAR_MIN or car_year > CAR_YEAR_MAX:
        raise Exception("company_exception car_year")
    return car_year

##############################
CAR_COLOR_MAX = 20
REGEX_CAR_COLOR = rf"^[A-Za-zÆØÅæøå -]{{1,{CAR_COLOR_MAX}}}$"

def validate_car_color():
    car_color = request.form.get("car_color", "").strip()
    if not re.match(REGEX_CAR_COLOR, car_color):
        raise Exception("company_exception car_color")
    return car_color

###############################
SEARCH_QUERY_MIN = 2
SEARCH_QUERY_MAX = 50
REGEX_SEARCH_QUERY = rf"^[A-Za-zÆØÅæøå -]{{{SEARCH_QUERY_MIN},{SEARCH_QUERY_MAX}}}$"

def validate_search_query():
    search_query = request.args.get("search", "").strip()
    if not re.match(REGEX_SEARCH_QUERY, search_query):
        raise Exception("company_exception search_query")
    return search_query



###############################
########## E-Mail #############
###############################



def send_verification_email(receiver_email, firstname, verification_key):
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
RESET_PASSWORD_TTL_SECONDS = 60 # 1 minute

def validate_reset_password_key(reset_key):
    reset_key = str(reset_key).strip()
    if not re.match(REGEX_RESET_PASSWORD_KEY, reset_key):
        raise Exception("company_exception reset_password_key invalid")
    return reset_key


def make_reset_password_key():
    random_key = uuid.uuid4().hex + uuid.uuid4().hex
    expires_at = int(time()) + RESET_PASSWORD_TTL_SECONDS
    return f"{random_key}:{expires_at}"


def parse_reset_password_key(reset_key):
    reset_key = validate_reset_password_key(reset_key)

    random_key, expires_at = reset_key.split(":")
    expires_at = int(expires_at)

    return random_key, expires_at


def is_reset_password_key_expired(reset_key):
    reset_key_parts = parse_reset_password_key(reset_key)
    expires_at = reset_key_parts[1]
    return int(time()) > expires_at

###########################
REGEX_EMAIL = "^(?:@a|@b|[^@\\s]+@(?:[a-zA-Z0-9-]+\\.)+[a-zA-Z]{2,})$"


def validate_email(email):
    email = email.strip()
    if not re.match(REGEX_EMAIL, email):
        raise Exception("company_exception email")
    return email

############################
USER_PASSWORD_MIN = 8
USER_PASSWORD_MAX = 50
REGEX_USER_PASSWORD = f"^.{{{USER_PASSWORD_MIN},{USER_PASSWORD_MAX}}}$"


def validate_user_password(password):
    user_password = password.strip()
    if not re.match(REGEX_USER_PASSWORD, user_password):
        raise Exception("company_exception user_password")
    return user_password
