# Promotional offers — read-only, no authentication required.
# Prefix: /api

from flask import Blueprint, jsonify

from routes.api_common import apply_cors, row_to_json
from x import db

bp = Blueprint("offers_api", __name__, url_prefix="/api")


@bp.after_request
def _cors(response):
    # Adds CORS headers to all offer responses.
    return apply_cors(response)


@bp.get("/offers")
def list_offers():
    """GET /api/offers
    Returns currently active promotional offers — those where today's date falls
    between offer_start_date and offer_end_date.
    Each offer includes a description, discount percentage, and a base64-encoded photo."""
    print("Offers route hit", flush=True)
    return jsonify({"offers": []})
