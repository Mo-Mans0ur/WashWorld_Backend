import re
import uuid
from datetime import datetime, timedelta
from typing import Optional

from flask import Blueprint, jsonify, request, redirect
from werkzeug.security import check_password_hash, generate_password_hash

from routes.api_common import apply_cors, error_response, json_body, row_to_json
from routes.auth_tokens import create_access_token
from x import REGEX_USER_EMAIL, db, send_verification_email

PASSWORD_MIN = 8
PASSWORD_MAX = 50
VERIFICATION_LINK_TTL_MINUTES = 10 # min

bp = Blueprint("auth_api", __name__, url_prefix="/api/auth")


@bp.after_request
def _cors(response):
    # Adds CORS headers to auth responses.
    return apply_cors(response)


@bp.route("/login", methods=["OPTIONS"])
@bp.route("/register", methods=["OPTIONS"])
@bp.route("/verify/<verification_key>", methods=["OPTIONS"])
def auth_options(verification_key=None):
    # Handles browser preflight requests for auth routes.
    return apply_cors(jsonify({}))


def _public_user(row):
    # Builds the user object that is safe to send back to the frontend.
    return {
        "user_id": row["user_id"],
        "user_email": row["user_email"],
        "user_firstname": row["user_firstname"],
        "user_lastname": row["user_lastname"],
        "user_phone": row["user_phone"],
        "user_created_at": row_to_json(row)["user_created_at"],
        "user_updated_at": row_to_json(row)["user_updated_at"],
        "user_deleted_at": row_to_json(row).get("user_deleted_at"),
        "user_verified_at": row_to_json(row).get("user_verified_at"),
    }


def _validate_email(email: str) -> Optional[str]:
    # Checks if the email is valid.
    email = email.strip()
    if not re.match(REGEX_USER_EMAIL, email):
        return None
    return email


def _validate_password(password: str) -> Optional[str]:
    # Checks if the password length is valid.
    password = password.strip()
    if len(password) < PASSWORD_MIN or len(password) > PASSWORD_MAX:
        return None
    return password


def _fetch_user_by_email(cursor, email: str):
    # Finds one user by email.
    cursor.execute(
        """
        SELECT
            user_id,
            user_email,
            user_password_hashed,
            user_firstname,
            user_lastname,
            user_phone,
            user_created_at,
            user_updated_at,
            user_deleted_at,
            user_verification_key,
            user_verified_at
        FROM users
        WHERE user_email = %s
        LIMIT 1
        """,
        (email,),
    )
    return cursor.fetchone()


def _fetch_user_by_verification_key(cursor, verification_key: str):
    # Finds one user by their email verification key.
    cursor.execute(
        """
        SELECT
            user_id,
            user_email,
            user_password_hashed,
            user_firstname,
            user_lastname,
            user_phone,
            user_created_at,
            user_updated_at,
            user_deleted_at,
            user_verification_key,
            user_verified_at
        FROM users
        WHERE user_verification_key = %s
        LIMIT 1
        """,
        (verification_key,),
    )
    return cursor.fetchone()


@bp.post("/login")
def login():
    # Logs in a verified user and returns an access token.
    data = json_body()
    email = _validate_email(data.get("user_email", ""))
    password = _validate_password(data.get("user_password", ""))

    if not email or not password:
        return error_response("Ugyldig email eller kodeord", 400)

    conn, cursor = None, None

    try:
        conn, cursor = db()
        user = _fetch_user_by_email(cursor, email)

        if not user or user.get("user_deleted_at"):
            return error_response("Ugyldigt brugernavn eller kodeord", 401)

        if not check_password_hash(user["user_password_hashed"], password):
            return error_response("Ugyldigt brugernavn eller kodeord", 401)

        if not user.get("user_verified_at"):
            return error_response("Du skal bekræfte din email før du kan logge ind", 403)

        token = create_access_token(user["user_id"])

        return jsonify({
            "token": token,
            "user": _public_user(user),
        })

    except Exception as e:
        if hasattr(e, "args") and len(e.args) > 1 and e.args[1] == 500:
            message = str(e.args[0])
        else:
            message = "Kunne ikke logge ind"

        return error_response(message, 503)

    finally:
        if cursor:
            cursor.close()

        if conn:
            conn.close()


@bp.post("/register")
def register():
    # Creates a new user and sends a verification email.
    data = json_body()
    email = _validate_email(data.get("user_email", ""))
    password = _validate_password(data.get("user_password", ""))
    firstname = (data.get("user_firstname") or "").strip()
    lastname = (data.get("user_lastname") or "").strip()
    phone = (data.get("user_phone") or "").strip()

    if not email or not password:
        return error_response("Ugyldig email eller kodeord", 400)
    if len(firstname) < 2 or len(firstname) > 50:
        return error_response("Fornavn skal være 2–50 tegn", 400)
    if len(lastname) < 2 or len(lastname) > 50:
        return error_response("Efternavn skal være 2–50 tegn", 400)
    if len(phone) > 20:
        return error_response("Telefonnummer er for langt", 400)

    user_id = uuid.uuid4().hex
    verification_key = uuid.uuid4().hex
    password_hash = generate_password_hash(
        password,
        method="pbkdf2:sha256",
    )
    now = datetime.utcnow()

    conn, cursor = None, None
    try:
        conn, cursor = db()
        if _fetch_user_by_email(cursor, email):
            return error_response("Email er allerede registreret", 409)

        cursor.execute(
            """
    INSERT INTO users (
        user_id, user_email, user_password_hashed,
        user_firstname, user_lastname, user_phone,
        user_created_at, user_updated_at, user_deleted_at,
        user_verification_key, user_verified_at, user_reset_password
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NULL, %s, NULL, NULL)
    """,
            (
                user_id,
                email,
                password_hash,
                firstname,
                lastname,
                phone,
                now,
                now,
                verification_key,
            ),
        )
        conn.commit()


        try:
            send_verification_email(email, firstname, verification_key)
        except Exception as email_error:
            print(email_error, flush=True)
            return jsonify({
                "message": "Bruger oprettet, men verification email kunne ikke sendes",
                "user_id": user_id,
            }), 201

        return jsonify({
            "message": "Bruger oprettet. Tjek din email for at bekræfte kontoen.",
            "user_id": user_id,
        }), 201

    except Exception as e:
        if conn:
            conn.rollback()

        if hasattr(e, "args") and len(e.args) > 1 and e.args[1] == 500:
            message = str(e.args[0])
        else:
            message = "Kunne ikke oprette bruger"

        return error_response(message, 503)

    finally:
        if cursor:
            cursor.close()

        if conn:
            conn.close()


@bp.get("/verify/<verification_key>")
def verify_email(verification_key):
    # Verifies a user account from the email link.
    conn, cursor = None, None

    try:
        verification_key = str(verification_key or "").strip()

        if not verification_key:
            return error_response("Missing verification key", 400)

        conn, cursor = db()

        user = _fetch_user_by_verification_key(cursor, verification_key)

        if not user:
            return redirect("http://localhost:3000/email-verified?status=invalid")

        if user.get("user_deleted_at"):
            return redirect("http://localhost:3000/email-verified?status=deleted")

        if datetime.utcnow() >= user["user_created_at"] + timedelta(minutes=VERIFICATION_LINK_TTL_MINUTES):
            return redirect("http://localhost:3000/email-verified?status=expired")

        if user.get("user_verified_at"):
            return redirect("http://localhost:3000/email-verified?status=already-verified")

        
        now = datetime.utcnow()
        new_verification_key = uuid.uuid4().hex

        cursor.execute(
            """
            UPDATE users
            SET
                user_verified_at = %s,
                user_updated_at = %s,
                user_verification_key = %s
            WHERE user_id = %s
            """,
            (
                now,
                now,
                new_verification_key,
                user["user_id"],
            ),
        )

        conn.commit()

        return redirect("http://localhost:3000/email-verified?status=success")

    except Exception as e:
        print(e, flush=True)

        if conn:
            conn.rollback()

        return error_response("Could not verify email", 503)

    finally:
        if cursor:
            cursor.close()

        if conn:
            conn.close()
