from decimal import Decimal

from flask import jsonify, request


def apply_cors(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, PATCH, DELETE, OPTIONS"
    return response


def row_to_json(row):
    out = {}
    for key, value in row.items():
        if isinstance(value, Decimal):
            out[key] = float(value)
        elif hasattr(value, "isoformat"):
            out[key] = value.isoformat(sep=" ", timespec="seconds")
        else:
            out[key] = value
    return out


def json_body():
    return request.get_json(silent=True) or {}


def error_response(message, status=400):
    return jsonify({"error": message, "message": message}), status
