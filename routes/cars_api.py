import uuid

from flask import Blueprint, jsonify

from routes.api_common import apply_cors, error_response, json_body, row_to_json
from routes.users_api import _bearer_user_id
from x import db

bp = Blueprint("cars_api", __name__, url_prefix="/api/users")


@bp.after_request
def _cors(response):
    return apply_cors(response)


def _authorize(user_id: str):
    token_user_id = _bearer_user_id()
    if not token_user_id:
        return None, error_response("Ikke autoriseret", 401)
    if token_user_id != user_id:
        return None, error_response("Ingen adgang", 403)
    return token_user_id, None


@bp.get("/<user_id>/cars")
def get_user_cars(user_id):
    _, err = _authorize(user_id)
    if err:
        return err

    conn, cursor = None, None
    try:
        conn, cursor = db()
        cursor.execute(
            """
            SELECT car_id, user_id, car_license_plate
            FROM cars
            WHERE user_id = %s
            ORDER BY car_license_plate ASC
            """,
            (user_id,),
        )
        rows = cursor.fetchall()
        return jsonify({"cars": [row_to_json(r) for r in rows]})
    except Exception:
        return error_response("Kunne ikke hente køretøjer", 503)
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


@bp.post("/<user_id>/cars")
def create_car(user_id):
    _, err = _authorize(user_id)
    if err:
        return err

    data = json_body()
    plate = str(data.get("car_license_plate", "")).strip()
    if not plate:
        return error_response("Mangler nummerplade", 400)
    if len(plate) > 12:
        return error_response("Nummerplade må højst være 12 tegn", 400)

    car_id = uuid.uuid4().hex
    conn, cursor = None, None
    try:
        conn, cursor = db()
        cursor.execute(
            """
            INSERT INTO cars (car_id, user_id, car_license_plate)
            VALUES (%s, %s, %s)
            """,
            (car_id, user_id, plate),
        )
        conn.commit()
        return jsonify(
            {
                "message": "Køretøj oprettet",
                "car": {
                    "car_id": car_id,
                    "user_id": user_id,
                    "car_license_plate": plate,
                },
            }
        ), 201
    except Exception as e:
        if conn:
            conn.rollback()
        if hasattr(e, "errno") and e.errno == 1062:
            return error_response("Nummerpladen findes allerede", 409)
        return error_response("Kunne ikke oprette køretøj", 503)
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


@bp.put("/<user_id>/cars/<car_id>")
def update_car(user_id, car_id):
    _, err = _authorize(user_id)
    if err:
        return err

    data = json_body()
    plate = str(data.get("car_license_plate", "")).strip()
    if not plate:
        return error_response("Mangler nummerplade", 400)
    if len(plate) > 12:
        return error_response("Nummerplade må højst være 12 tegn", 400)

    conn, cursor = None, None
    try:
        conn, cursor = db()
        cursor.execute(
            "SELECT car_id FROM cars WHERE car_id = %s AND user_id = %s LIMIT 1",
            (car_id, user_id),
        )
        if not cursor.fetchone():
            return error_response("Køretøj ikke fundet", 404)

        cursor.execute(
            """
            UPDATE cars
            SET car_license_plate = %s
            WHERE car_id = %s AND user_id = %s
            """,
            (plate, car_id, user_id),
        )
        conn.commit()
        return jsonify({"message": "Køretøj opdateret"})
    except Exception as e:
        if conn:
            conn.rollback()
        if hasattr(e, "errno") and e.errno == 1062:
            return error_response("Nummerpladen findes allerede", 409)
        return error_response("Kunne ikke opdatere køretøj", 503)
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


@bp.delete("/<user_id>/cars/<car_id>")
def delete_car(user_id, car_id):
    _, err = _authorize(user_id)
    if err:
        return err

    conn, cursor = None, None
    try:
        conn, cursor = db()
        cursor.execute(
            "DELETE FROM cars WHERE car_id = %s AND user_id = %s",
            (car_id, user_id),
        )
        conn.commit()
        if cursor.rowcount == 0:
            return error_response("Køretøj ikke fundet", 404)
        return jsonify({"message": "Køretøj slettet"})
    except Exception:
        if conn:
            conn.rollback()
        return error_response("Kunne ikke slette køretøj", 503)
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
