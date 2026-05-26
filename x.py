# Shared utilities: database connection, email sending, validation helpers, and password-reset key logic.
# Imported by routes/*.py modules — not a blueprint itself despite the bp definition below.

from time import time

from flask import request, make_response, Blueprint
import resend
import mysql.connector
import uuid
import re
from functools import wraps


bp = Blueprint("x", __name__)

##############################
import os
import mysql.connector


def db():
    """Opens a new database connection and returns (connection, cursor).
    The cursor uses dictionary=True so rows come back as dicts instead of tuples.
    Raises Exception("Database under maintenance", 500) if the connection fails.
    Called at the start of every route handler."""
    try:
        connection = mysql.connector.connect(
            host=os.environ.get("MYSQL_HOST", "mariadb"),
            port=int(os.environ.get("MYSQL_PORT", 3306)),
            user=os.environ["MYSQL_USER"],
            password=os.environ["MYSQL_PASSWORD"],
            database=os.environ["MYSQL_DATABASE"],
            charset="utf8mb4",
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
    """Reads user_email from request.form and validates the format.
    Used in older form-based flows. For JSON-body flows use validate_email() instead."""
    user_email = request.form.get("user_email", "").strip()
    if not re.match(REGEX_USER_EMAIL, user_email):
        raise Exception("company_exception user_email")
    return user_email


##############################
USER_FIRST_NAME_MIN = 2
USER_FIRST_NAME_MAX = 20
USER_FIRST_NAME_REGEX = f"^.{{{USER_FIRST_NAME_MIN},{USER_FIRST_NAME_MAX}}}$"


def validate_user_first_name():
    """Reads user_first_name from request.form and checks it is 2–20 characters."""
    user_first_name = request.form.get("user_first_name", "").strip()
    if not re.match(USER_FIRST_NAME_REGEX, user_first_name):
        raise Exception(f"--error-- user_first_name")

    return user_first_name


##############################
USER_LAST_NAME_MIN = 2
USER_LAST_NAME_MAX = 20


def validate_user_last_name():
    """Reads user_last_name from request.form and checks it is 2–20 characters."""
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
    """Reads user_username from request.form and checks it is 2–20 characters."""
    user_username = request.form.get("user_username", "").strip()
    if not re.match(USER_USERNAME_REGEX, user_username):
        raise Exception("--error-- user_username")
    return user_username


##############################
def no_cache(view):
    """Decorator that adds Cache-Control headers to prevent browsers from caching a page.
    Used on HTML template routes where stale data would be a problem."""
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
    """Reads user_password from request.form and checks it is 8–50 characters.
    NOTE: This form-based version is overridden later in this file by a second definition
    that takes a password argument directly. Only the second definition is active at runtime."""
    user_password = request.form.get("user_password", "").strip()
    if not re.match(REGEX_USER_PASSWORD, user_password):
        raise Exception("company_exception user_password")
    return user_password

###############################
CAR_NUMBER_PLATE_REGEX = r"^[A-Z0-9][A-Z0-9 \-]{0,10}[A-Z0-9]$"


class InvalidCarPlateError(ValueError):
    pass


def validate_car_number_plate(plate):
    """Normalizes and validates a license plate string (strips whitespace, uppercases).
    Raises InvalidCarPlateError (not plain Exception) so callers can catch it
    without accidentally swallowing unrelated errors like DB failures.
    Used in cars_api before inserting or updating a car."""
    car_number_plate = str(plate or "").strip().upper()
    if not car_number_plate or not re.match(CAR_NUMBER_PLATE_REGEX, car_number_plate):
        raise InvalidCarPlateError("Mangler nummerplade")
    return car_number_plate


###############################
########## E-Mail #############
###############################


def send_verification_email(receiver_email, firstname, verification_key):
    """Sends an HTML email to the user with a link to verify their account.
    The link points to /api/auth/verify/<verification_key> and expires after 10 minutes.
    Called in auth_api.register after a new user is created."""
    try:
        resend.api_key = os.environ["RESEND_API_KEY"]
        backend_url = os.environ.get("BACKEND_URL", "http://127.0.0.1:80")
        verification_link = f"{backend_url}/api/auth/verify/{verification_key}"

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

        resend.Emails.send({
            "from": "WashWorld <onboarding@resend.dev>",
            "to": receiver_email,
            "subject": "Please verify your account",
            "html": body,
        })
        print("Verification email sent successfully!", flush=True)
        return "email sent"

    except Exception as ex:
        print(ex, flush=True)
        raise Exception("Failed to send verification email", 500)

###############################

REGEX_RESET_PASSWORD_KEY = r"^[a-f0-9]{64}:[0-9]{10}$"
RESET_PASSWORD_TTL_SECONDS = 900  # 15 minutes


def validate_reset_password_key(reset_key):
    """Checks that the reset key matches the expected format: 64-char hex + ':' + 10-digit Unix timestamp.
    Raises Exception if invalid. Used by parse_reset_password_key before splitting the key."""
    reset_key = str(reset_key).strip()
    if not re.match(REGEX_RESET_PASSWORD_KEY, reset_key):
        raise Exception("company_exception reset_password_key invalid")
    return reset_key


def make_reset_password_key():
    """Generates a new reset password key: 64 random hex characters + ':' + Unix expiry timestamp.
    The expiry is RESET_PASSWORD_TTL_SECONDS (15 min) from now.
    Called in auth_api.forgot_password and stored in users.user_reset_password."""
    random_key = uuid.uuid4().hex + uuid.uuid4().hex
    expires_at = int(time()) + RESET_PASSWORD_TTL_SECONDS
    return f"{random_key}:{expires_at}"


def parse_reset_password_key(reset_key):
    """Splits a reset key into its (random_hex, expires_at_unix) components after validating format.
    Called by is_reset_password_key_expired."""
    reset_key = validate_reset_password_key(reset_key)

    random_key, expires_at = reset_key.split(":")
    expires_at = int(expires_at)

    return random_key, expires_at


def is_reset_password_key_expired(reset_key):
    """Returns True if the reset key's embedded expiry timestamp is in the past.
    Called in auth_api.reset_password before accepting the new password."""
    reset_key_parts = parse_reset_password_key(reset_key)
    expires_at = reset_key_parts[1]
    return int(time()) > expires_at

###########################
REGEX_EMAIL = "^(?:@a|@b|[^@\\s]+@(?:[a-zA-Z0-9-]+\\.)+[a-zA-Z]{2,})$"


def validate_email(email):
    """Validates an email string passed directly as a parameter (not from request.form).
    Raises Exception if invalid. Used in flows that receive email from JSON bodies."""
    email = email.strip()
    if not re.match(REGEX_EMAIL, email):
        raise Exception("company_exception email")
    return email


def send_reset_password_email(receiver_email, firstname, reset_key):
    """Sends an HTML email with a password-reset link to the user.
    The link points to the frontend reset page with the key as a query parameter.
    The link expires in 15 minutes (enforced by is_reset_password_key_expired).
    Called in auth_api.forgot_password after the reset key is stored in the DB."""
    try:
        resend.api_key = os.environ["RESEND_API_KEY"]
        frontend_url = os.environ.get("FRONTEND_URL", "http://localhost:3000")
        reset_link = f"{frontend_url}/reset-password/confirm?key={reset_key}"

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

        resend.Emails.send({
            "from": "WashWorld <onboarding@resend.dev>",
            "to": receiver_email,
            "subject": "Nulstil din adgangskode",
            "html": body,
        })
        print("Reset password email sent successfully!", flush=True)

        return "email sent"

    except Exception as ex:
        print(ex, flush=True)
        raise Exception("Failed to send reset password email", 500)

############################
# NOTE: USER_PASSWORD_MIN, USER_PASSWORD_MAX, and REGEX_USER_PASSWORD are redefined here.
# This second definition of validate_user_password (takes a password argument) overrides
# the earlier form-based version and is the one active at runtime.
USER_PASSWORD_MIN = 8
USER_PASSWORD_MAX = 50
REGEX_USER_PASSWORD = f"^.{{{USER_PASSWORD_MIN},{USER_PASSWORD_MAX}}}$"


def validate_user_password(password):
    """Validates a password string passed directly as a parameter.
    Checks it is 8–50 characters. Raises Exception if invalid."""
    user_password = password.strip()
    if not re.match(REGEX_USER_PASSWORD, user_password):
        raise Exception("company_exception user_password")
    return user_password
