from flask import Flask, jsonify, request, abort
from models.payment_method import PaymentMethod
from models import storage


from api.v1.src.views import app_views


@app_views.route("/payment_methods", methods=["GET"])
def get_all_payment_methods():
    """Retrieve all payment methods"""
    payment_methods = storage.all(PaymentMethod).values()
    payment_methods_list = [
        payment_method.to_dict() for payment_method in payment_methods
    ]
    return jsonify(payment_methods_list), 200


@app_views.route("/payment_methods/<payment_method_id>", methods=["GET"])
def get_payment_method(payment_method_id):
    """Retrieve a specific payment method by ID"""
    payment_method = storage.get(PaymentMethod, payment_method_id)
    if payment_method is None:
        abort(404, description="Payment method not found")
    return jsonify(payment_method.to_dict()), 200


@app_views.route("/payment_methods", methods=["POST"])
def create_payment_method():
    """Create a new payment method"""
    if not request.json:
        abort(400, description="Not a JSON")

    data = request.json
    required_fields = ["name"]
    for field in required_fields:
        if field not in data:
            abort(400, description=f"Missing {field}")

    # Create new PaymentMethod object
    new_payment_method = PaymentMethod(**data)

    new_payment_method.save()

    return jsonify(new_payment_method.to_dict()), 201


@app_views.route("/payment_methods/<payment_method_id>", methods=["PUT"])
def update_payment_method(payment_method_id):
    """Update an existing payment method"""
    payment_method = storage.get(PaymentMethod, payment_method_id)
    if payment_method is None:
        abort(404, description="Payment method not found")

    if not request.json:
        abort(400, description="Not a JSON")

    data = request.json
    payment_method.name = data.get("name", payment_method.name)

    storage.save()
    return jsonify(payment_method.to_dict()), 200


@app_views.route("/payment_methods/<payment_method_id>", methods=["DELETE"])
def delete_payment_method(payment_method_id):
    """Delete a payment method"""
    payment_method = storage.get(PaymentMethod, payment_method_id)
    if payment_method is None:
        abort(404, description="Payment method not found")

    storage.delete(payment_method)
    storage.save()
    return jsonify({}), 200
