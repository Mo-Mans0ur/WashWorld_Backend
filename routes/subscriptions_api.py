import uuid

from icecream import ic
from flask import Blueprint, jsonify

from routes.api_common import apply_cors, error_response, json_body, row_to_json
from x import db


bp = Blueprint("subscriptions_api", __name__, url_prefix="/api")


@bp.after_request
def _cors(response):
    return apply_cors(response)


@bp.route("/subscriptions", methods=["OPTIONS"])
@bp.route("/subscriptions/<subscription_id>", methods=["OPTIONS"])
def subscriptions_options(subscription_id=None):
    return apply_cors(jsonify({}))


@bp.get("/subscriptions")
def get_subscriptions():
    conn, cursor = None, None

    try:
        conn, cursor = db()

        cursor.execute(
            """
            SELECT subscription_id, product_id, car_id, subscriptions_name,
                   subscriptions_price, subscriptions_status, subscriptions_start_date,
                   subscriptions_end_date, subscriptions_next_billing_date
            FROM subscriptions
            """
        )

        rows = cursor.fetchall()

        return jsonify({"subscriptions": [row_to_json(r) for r in rows]})

    except Exception as ex:
        ic(ex)
        return jsonify({"error": "Could not load subscriptions"}), 503

    finally:
        if cursor:
            cursor.close()

        if conn:
            conn.close()


@bp.post("/subscriptions")
def create_subscription():
    conn, cursor = None, None
    try:
        data = json_body()
        # product_id og car_id er nullable i DB — sendes som None hvis tomme
        product_id = str(data.get("product_id", "")).strip() or None
        car_id = str(data.get("car_id", "")).strip() or None
        subscription_name = str(data.get("subscription_name", "")).strip()
        subscription_price = str(data.get("subscription_price", "")).strip()
        subscription_status = str(data.get("subscription_status", "")).strip()
        subscription_start_date = str(data.get("subscription_start_date", "")).strip()
        subscription_end_date = str(data.get("subscription_end_date", "")).strip()
        subscription_next_billing_date = str(data.get("subscription_next_billing_date", "")).strip()

        if not subscription_name:
            return error_response("Mangler abonnementsnavn", 400)
        if not subscription_price:
            return error_response("Mangler pris", 400)
        if not subscription_status:
            return error_response("Mangler status", 400)
        if not subscription_start_date:
            return error_response("Mangler startdato", 400)
        if not subscription_end_date:
            return error_response("Mangler slutdato", 400)
        if not subscription_next_billing_date:
            return error_response("Mangler næste faktureringsdato", 400)

        subscription_id = uuid.uuid4().hex
        conn, cursor = db()
        cursor.execute(
            """
            INSERT INTO subscriptions (
                subscription_id, product_id, car_id, subscriptions_name,
                subscriptions_price, subscriptions_status, subscriptions_start_date,
                subscriptions_end_date, subscriptions_next_billing_date
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                subscription_id, product_id, car_id, subscription_name,
                subscription_price, subscription_status, subscription_start_date,
                subscription_end_date, subscription_next_billing_date,
            ),
        )
        conn.commit()
        return jsonify({"message": "Abonnement oprettet", "subscription_id": subscription_id}), 201
    except Exception as ex:
        ic(ex)
        if conn:
            conn.rollback()
        return error_response("Kunne ikke oprette abonnement", 503)
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


@bp.delete("/subscriptions/<subscription_id>")
def delete_subscription(subscription_id):
    conn, cursor = None, None
    try:
        subscription_id = (subscription_id or "").strip()
        if not subscription_id:
            return error_response("Mangler subscription id", 400)

        conn, cursor = db()
        cursor.execute(
            "DELETE FROM subscriptions WHERE subscription_id = %s",
            (subscription_id,),
        )
        conn.commit()

        if cursor.rowcount == 0:
            return error_response("Abonnement ikke fundet", 404)
        return jsonify({"message": "Abonnement slettet"})
    except Exception as ex:
        ic(ex)
        if conn:
            conn.rollback()
        return error_response("Kunne ikke slette abonnement", 503)
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


@bp.put("/subscriptions/<subscription_id>")
def update_subscription(subscription_id):
    conn, cursor = None, None
    try:
        subscription_id = (subscription_id or "").strip()
        if not subscription_id:
            return error_response("Mangler subscription id", 400)

        data = json_body()
        subscription_status = str(data.get("subscription_status", "")).strip()
        subscription_end_date = str(data.get("subscription_end_date", "")).strip()
        subscription_next_billing_date = str(data.get("subscription_next_billing_date", "")).strip()

        if not subscription_status:
            return error_response("Mangler status", 400)
        if not subscription_end_date:
            return error_response("Mangler slutdato", 400)
        if not subscription_next_billing_date:
            return error_response("Mangler næste faktureringsdato", 400)

        conn, cursor = db()
        cursor.execute(
            """
            UPDATE subscriptions
            SET subscriptions_status = %s,
                subscriptions_end_date = %s,
                subscriptions_next_billing_date = %s
            WHERE subscription_id = %s
            """,
            (subscription_status, subscription_end_date, subscription_next_billing_date, subscription_id),
        )
        conn.commit()

        if cursor.rowcount == 0:
            return error_response("Abonnement ikke fundet", 404)
        return jsonify({"message": "Abonnement opdateret"})
    except Exception as ex:
        ic(ex)
        if conn:
            conn.rollback()
        return error_response("Kunne ikke opdatere abonnement", 503)
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()