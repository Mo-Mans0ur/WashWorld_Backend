from decimal import Decimal

from flask import Blueprint, jsonify

from x import db

bp = Blueprint("locations_api", __name__, url_prefix="/api")


@bp.after_request
def _cors(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    return response


def _row_to_json(row):
    out = {}
    for key, value in row.items():
        if isinstance(value, Decimal):
            out[key] = float(value)
        else:
            out[key] = value
    return out


@bp.get("/locations")
def list_locations():
    conn, cursor = None, None
    try:
        conn, cursor = db()
        cursor.execute(
            """
            SELECT location_id, location_name, location_address, location_zipcode,
                   location_coordinate_x, location_coordinate_y, location_open_hours
            FROM locations
            ORDER BY location_name
            """
        )
        rows = cursor.fetchall()
        return jsonify({"locations": [_row_to_json(r) for r in rows]})
    except Exception as e:
        if hasattr(e, "args") and len(e.args) > 1 and e.args[1] == 500:
            message = str(e.args[0])
        else:
            message = "Could not load locations"
        return jsonify({"error": message}), 503
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()