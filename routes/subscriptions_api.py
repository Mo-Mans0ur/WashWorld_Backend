from icecream import ic
from flask import Blueprint, jsonify, request
import uuid

from routes.api_common import apply_cors
from x import db


bp = Blueprint("subscriptions_api", __name__, url_prefix="/api")


@bp.after_request
def _cors(response):
    return apply_cors(response)


@bp.get("/subscriptions")
def get_subscriptions():
    conn, cursor = None, None

    try:
        conn, cursor = db()

        cursor.execute(
            """
            SELECT *
            FROM subscriptions
            """
        )

        rows = cursor.fetchall()

        return jsonify({"subscriptions": [dict(row) for row in rows]})

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
        data = request.get_json(silent=True) or {}

        product_id = str(data.get("product_id", "")).strip()
        car_id = str(data.get("car_id", "")).strip()
        subscription_name = str(data.get("subscription_name", "")).strip()
        subscription_price = str(data.get("subscription_price", "")).strip()
        subscription_status = str(data.get("subscription_status", "")).strip()
        subscription_start_date = str(data.get("subscription_start_date", "")).strip()
        subscription_end_date = str(data.get("subscription_end_date", "")).strip()
        subscription_next_billing_date = str(
            data.get("subscription_next_billing_date", "")
        ).strip()

        if not product_id:
            return jsonify({"error": "Missing product id"}), 400

        if not car_id:
            return jsonify({"error": "Missing car id"}), 400

        if not subscription_name:
            return jsonify({"error": "Missing subscription name"}), 400

        if not subscription_price:
            return jsonify({"error": "Missing subscription price"}), 400

        if not subscription_status:
            return jsonify({"error": "Missing subscription status"}), 400

        if not subscription_start_date:
            return jsonify({"error": "Missing subscription start date"}), 400

        if not subscription_end_date:
            return jsonify({"error": "Missing subscription end date"}), 400

        if not subscription_next_billing_date:
            return jsonify({"error": "Missing subscription next billing date"}), 400

        subscription_id = uuid.uuid4().hex

        conn, cursor = db()

        cursor.execute(
            """
            INSERT INTO subscriptions (
                subscription_id,
                product_id,
                car_id,
                subscriptions_name,
                subscriptions_price,
                subscriptions_status,
                subscriptions_start_date,
                subscriptions_end_date,
                subscriptions_next_billing_date
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                subscription_id,
                product_id,
                car_id,
                subscription_name,
                subscription_price,
                subscription_status,
                subscription_start_date,
                subscription_end_date,
                subscription_next_billing_date,
            ),
        )

        conn.commit()

        return jsonify(
            {
                "message": "Subscription created successfully!",
                "subscription_id": subscription_id,
            }
        ), 201

    except Exception as ex:
        ic(ex)
        return jsonify({"error": "Could not create subscription"}), 503

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
            return jsonify({"error": "Missing subscription id"}), 400

        conn, cursor = db()

        cursor.execute(
            """
            DELETE FROM subscriptions
            WHERE subscription_id = %s
            """,
            (subscription_id,),
        )

        conn.commit()

        if cursor.rowcount == 0:
            return jsonify({"error": "Subscription not found"}), 404

        return jsonify({"message": "Subscription deleted successfully!"})

    except Exception as ex:
        ic(ex)
        return jsonify({"error": "Could not delete subscription"}), 503

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
        data = request.get_json(silent=True) or {}

        if not subscription_id:
            return jsonify({"error": "Missing subscription id"}), 400

        subscription_status = str(data.get("subscription_status", "")).strip()
        subscription_end_date = str(data.get("subscription_end_date", "")).strip()
        subscription_next_billing_date = str(
            data.get("subscription_next_billing_date", "")
        ).strip()

        if not subscription_status:
            return jsonify({"error": "Missing subscription status"}), 400

        if not subscription_end_date:
            return jsonify({"error": "Missing subscription end date"}), 400

        if not subscription_next_billing_date:
            return jsonify({"error": "Missing subscription next billing date"}), 400

        conn, cursor = db()

        cursor.execute(
            """
            UPDATE subscriptions
            SET
                subscriptions_status = %s,
                subscriptions_end_date = %s,
                subscriptions_next_billing_date = %s
            WHERE subscription_id = %s
            """,
            (
                subscription_status,
                subscription_end_date,
                subscription_next_billing_date,
                subscription_id,
            ),
        )

        conn.commit()

        if cursor.rowcount == 0:
            return jsonify({"error": "Subscription not found"}), 404

        return jsonify({"message": "Subscription updated successfully!"})

    except Exception as ex:
        ic(ex)
        return jsonify({"error": "Could not update subscription"}), 503

    finally:
        if cursor:
            cursor.close()

        if conn:
            conn.close()