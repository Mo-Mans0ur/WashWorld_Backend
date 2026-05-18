from flask import Blueprint, jsonify, request

from routes.api_common import apply_cors, error_response, row_to_json
from routes.auth_api import _public_user
from routes.auth_tokens import load_user_id_from_token
from x import db

bp = Blueprint("users_api", __name__, url_prefix="/api/users")


@bp.after_request
def _cors(response):
    return apply_cors(response)


def _bearer_user_id():
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        return None
    token = auth[7:].strip()
    return load_user_id_from_token(token)


def _fetch_user_by_id(cursor, user_id: str):
    cursor.execute(
        """
        SELECT user_id, user_email, user_firstname, user_lastname, user_phone,
               user_created_at, user_updated_at, user_deleted_at, user_verified_at
        FROM users
        WHERE user_id = %s AND user_deleted_at IS NULL
        LIMIT 1
        """,
        (user_id,),
    )
    return cursor.fetchone()


@bp.get("/<user_id>")
def get_user(user_id):
    token_user_id = _bearer_user_id()
    if not token_user_id:
        return error_response("Ikke autoriseret", 401)
    if token_user_id != user_id:
        return error_response("Ingen adgang", 403)

    conn, cursor = None, None
    try:
        conn, cursor = db()
        user = _fetch_user_by_id(cursor, user_id)
        if not user:
            return error_response("Bruger ikke fundet", 404)
        return jsonify(_public_user(user))
    except Exception as e:
        if hasattr(e, "args") and len(e.args) > 1 and e.args[1] == 500:
            message = str(e.args[0])
        else:
            message = "Kunne ikke hente bruger"
        return error_response(message, 503)
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
