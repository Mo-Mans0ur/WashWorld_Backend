from flask import Blueprint, jsonify

from routes.api_common import apply_cors, row_to_json
from x import db

bp = Blueprint("offers_api", __name__, url_prefix="/api")


@bp.after_request
def _cors(response):
    return apply_cors(response)


@bp.get("/offers")
def list_offers():
    """Returnerer aktive tilbud til dashboard (inden for start- og slutdato)."""
    conn, cursor = None, None
    try:
        conn, cursor = db()
        cursor.execute(
            """
            SELECT offer_id, product_id, offer_description, offer_discount_percentage,
                   offer_start_date, offer_end_date, offer_photo_base64
            FROM offers
            WHERE offer_start_date <= NOW()
              AND offer_end_date >= NOW()
            ORDER BY offer_start_date DESC
            """
        )
        rows = cursor.fetchall()
        return jsonify({"offers": [row_to_json(r) for r in rows]})
    except Exception:
        return jsonify({"error": "Kunne ikke hente tilbud"}), 503
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
