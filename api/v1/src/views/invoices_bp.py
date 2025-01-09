#!/usr/bin/python3
""" objects that handle all default RestFul API actions for Invoices """
import os
from colorama import Fore, Style
from werkzeug.utils import secure_filename
from flask import (
    Flask,
    current_app,
    jsonify,
    make_response,
    request,
    abort,
    send_file,
    send_from_directory,
)
from pyparsing import removeQuotes
from api.v1.src.services.sendmail import send_email
from models import storage
from models.invoice import InvoiceStatus, Invoice
from models.attachments import Attachment
from models.alumni_group import AlumniGroup


from api.v1.src.views import app_views


@app_views.route("/invoices/users_invoices/<user_id>", methods=["GET"])
def get_users_invoices(user_id):
    """Retrieve all invoices of a user"""
    invoices = storage.all(Invoice).values()
    users_invoices = [
        invoice.to_dict() for invoice in invoices if invoice.billed_user_id == user_id
    ]
    return jsonify(users_invoices), 200


@app_views.route("/invoices", methods=["GET"])
def get_all_invoices():
    """Retrieve all invoices"""
    invoices = storage.all(Invoice).values()
    invoices_list = [invoice.to_dict() for invoice in invoices]
    return jsonify(invoices_list), 200


@app_views.route("/invoices/<invoice_id>", methods=["GET"])
def get_invoice(invoice_id):
    """Retrieve a specific invoice by ID"""
    invoice = storage.get(Invoice, invoice_id)
    if invoice is None:
        abort(404, description="Invoice not found")
    return jsonify(invoice.to_dict()), 200


@app_views.route("/invoices", methods=["POST"], strict_slashes=False)
def create_invoice():
    """Create a new invoice"""

    if not request.get_json():
        abort(400, description="No form data received")

    # Extract data from form
    form_data = request.get_json()
    required_fields = ["total_amount", "issue_date", "invoice_type", "group_id"]
    for field in required_fields:
        if field not in form_data:
            abort(400, description=f"Missing {field}")

    group = storage.get(AlumniGroup, form_data["group_id"])
    if group is None:
        abort(404, description="Group not found")

    # Create the Invoice object
    try:
        print(form_data)
        new_invoice = Invoice(
            invoice_number=(
                form_data["invoice_number"] if "invoice_number" in form_data else None
            ),
            amount=float(form_data["total_amount"]),
            insurance_package_id=group.package_id,
            contract_id=group.current_contract_id,
            **form_data,
        )
    except ValueError as error:
        abort(400, description=f"Invalid data: {str(error)}")

    new_invoice.save()

    return jsonify(new_invoice.to_dict()), 201


@app_views.route("/invoices/<invoice_id>", methods=["PUT"])
def update_invoice(invoice_id):
    """Update an existing invoice"""

    invoice = storage.get(Invoice, invoice_id)
    if invoice is None:
        abort(404, description="Invoice not found")

    if not request.get_json():
        abort(400, description="Not a JSON or form data")

    data = request.get_json()
    ignore = [
        "id",
        "created_at",
        "updated_at",
        "__class__",
        "invoice_number",
        "group",
        "billed_user",
    ]
    for key, value in data.items():
        if key not in ignore:
            setattr(invoice, key, value)

    storage.save()
    return jsonify(invoice.to_dict()), 200


@app_views.route("/invoices/<invoice_id>", methods=["DELETE"])
def delete_invoice(invoice_id):
    """Delete an invoice"""
    invoice = storage.get(Invoice, invoice_id)
    if invoice is None:
        abort(404, description="Invoice not found")

    storage.delete(invoice)
    storage.save()
    return jsonify({}), 200


@app_views.route("/send_invoice/<invoice_id>", methods=["POST"])
def send_invoice(invoice_id):
    """Delete an invoice"""
    invoice = storage.get(Invoice, invoice_id)
    if invoice is None:
        abort(404, description="Invoice not found")

    inv = invoice.generate_invoice()
    user_email = invoice.billed_user.email
    send_email(recipient=user_email, subject="Test", body=inv)

    return jsonify({}), 200
