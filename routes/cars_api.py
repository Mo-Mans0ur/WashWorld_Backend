import uuid

from flask import Blueprint, jsonify

from routes.api_common import apply_cors, error_response, json_body, row_to_json
from routes.users_api import _bearer_user_id
from x import db

bp = Blueprint("cars_api", __name__, url_prefix="/api/users")

VALID_VEHICLE_TYPES = {"car", "motorcycle", "truck", "bus"}
CAR_SELECT = """
    SELECT car_id, user_id, car_license_plate, car_name, car_is_ev,
           car_country_code, car_vehicle_type, car_is_active
    FROM cars
"""


def _authorize(user_id: str):
    token_user_id = _bearer_user_id()
    if not token_user_id:
        return None, error_response("Ikke autoriseret", 401)
    if token_user_id != user_id:
        return None, error_response("Ingen adgang", 403)
    return token_user_id, None


def _parse_bool(value) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in ("1", "true", "yes")


def _parse_car_fields(data: dict):
    plate = str(data.get("car_license_plate", "")).strip()
    if not plate:
        return None, error_response("Mangler nummerplade", 400)
    if len(plate) > 12:
        return None, error_response("Nummerplade må højst være 12 tegn", 400)

    name = str(data.get("car_name", "")).strip() or None
    if name and len(name) > 50:
        return None, error_response("Køretøjsnavn må højst være 50 tegn", 400)

    is_ev = _parse_bool(data.get("car_is_ev", False))

    country_code = str(data.get("car_country_code", "DK")).strip().upper() or "DK"
    if len(country_code) > 2:
        return None, error_response("Ugyldig landekode", 400)

    vehicle_type = str(data.get("car_vehicle_type", "car")).strip().lower() or "car"
    if vehicle_type not in VALID_VEHICLE_TYPES:
        return None, error_response("Ugyldig køretøjstype", 400)

    return (plate, name, is_ev, country_code, vehicle_type), None


@bp.after_request
def _cors(response):
    return apply_cors(response)


@bp.get("/<user_id>/cars")
def get_user_cars(user_id):
    _, err = _authorize(user_id)
    if err:
        return err

    conn, cursor = None, None
    try:
        conn, cursor = db()
        cursor.execute(
            f"""
            {CAR_SELECT}
            WHERE user_id = %s AND car_is_active = 1
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

    fields, err = _parse_car_fields(json_body())
    if err:
        return err
    plate, name, is_ev, country_code, vehicle_type = fields

    car_id = uuid.uuid4().hex
    conn, cursor = None, None
    try:
        conn, cursor = db()
        cursor.execute(
            """
            INSERT INTO cars (
                car_id, user_id, car_license_plate, car_name, car_is_ev,
                car_country_code, car_vehicle_type, car_is_active
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, 1)
            """,
            (car_id, user_id, plate, name, int(is_ev), country_code, vehicle_type),
        )
        conn.commit()
        return jsonify(
            {
                "message": "Køretøj oprettet",
                "car": {
                    "car_id": car_id,
                    "user_id": user_id,
                    "car_license_plate": plate,
                    "car_name": name,
                    "car_is_ev": is_ev,
                    "car_country_code": country_code,
                    "car_vehicle_type": vehicle_type,
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

    fields, err = _parse_car_fields(json_body())
    if err:
        return err
    plate, name, is_ev, country_code, vehicle_type = fields

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
            SET car_license_plate = %s,
                car_name = %s,
                car_is_ev = %s,
                car_country_code = %s,
                car_vehicle_type = %s
            WHERE car_id = %s AND user_id = %s
            """,
            (plate, name, int(is_ev), country_code, vehicle_type, car_id, user_id),
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
            "SELECT car_id FROM cars WHERE car_id = %s AND user_id = %s",
            (car_id, user_id),
        )
        if not cursor.fetchone():
            return error_response("Køretøj ikke fundet", 404)
        cursor.execute(
            "UPDATE cars SET car_is_active = 0 WHERE car_id = %s AND user_id = %s",
            (car_id, user_id),
        )
        conn.commit()
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
