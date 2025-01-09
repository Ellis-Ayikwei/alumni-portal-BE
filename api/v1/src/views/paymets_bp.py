from hmac import new
import os
from click import FLOAT
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
from models import storage
from models.payment import PaymentStatus, Payment
from models.attachments import Attachment
from api.v1.src.views import app_views
from api.v1.src.services.auditslogging.logginFn import log_audit
from flask import g
from models.audit_trails import AuditStatus


@app_views.route("/payments/users_payments/<user_id>", methods=["GET"])
def get_users_payments(user_id):
    """Retrieve all payments made by a user"""
    payments = storage.all(Payment).values()
    users_payments = [
        payment.to_dict() for payment in payments if payment.payer_id == user_id
    ]
    return jsonify(users_payments), 200


@app_views.route("/payments", methods=["GET"])
def get_all_payments():
    """Retrieve all payments"""
    payments = storage.all(Payment).values()
    payments_list = [payment.to_dict() for payment in payments]
    return jsonify(payments_list), 200


@app_views.route("/payments/<payment_id>", methods=["GET"])
def get_payment(payment_id):
    """Retrieve a specific payment by ID"""
    payment = storage.get(Payment, payment_id)
    if payment is None:
        abort(404, description="Payment not found")
    return jsonify(payment.to_dict()), 200


@app_views.route("/payments", methods=["POST"])
def create_payment():
    """Create a new payment"""
    from api.v1.app import uploaded_files

    if not request.form:
        abort(400, description="No form data received")

    # Extract data from form
    form_data = request.form
    required_fields = [
        "amount",
        "payment_date",
        "payer_id",
        "group_id",
        "payment_method_id",
    ]
    for field in required_fields:
        if field not in form_data:
            abort(400, description=f"Missing {field}")

    # Create the Payment object
    try:
        new_payment = Payment(
            amount=float(form_data["amount"]),
            payment_date=form_data["payment_date"],
            status=form_data.get("status", PaymentStatus.PENDING),
            payer_id=form_data["payer_id"],
            group_id=form_data["group_id"],
            payment_method_id=form_data["payment_method_id"],
        )
    except ValueError as error:
        abort(400, description=f"Invalid data: {str(error)}")

    request_files = request.files

    new_payment.save()
    # If files are present, process each one
    if request_files:
        for file in request_files.values():
            if file and file.filename:  # Ensure file is not empty and has a filename
                if uploaded_files.file_allowed(file, file.filename):
                    # Append the filename to the list of attachment URLs (you can modify this to suit your logic)

                    filename = uploaded_files.save(file)
                    new_attachment = Attachment(url=filename, payment_id=new_payment.id)
                    new_attachment.save()
                    # Save the file
                else:
                    abort(400, description="Invalid file type")

    return jsonify(new_payment.to_dict()), 201


@app_views.route("/payments/<payment_id>", methods=["PUT"])
def update_payment(payment_id):
    """Update an existing payment"""
    from api.v1.app import uploaded_files

    print(f"{Fore.GREEN} api hit {Style.RESET_ALL}")
    payment = storage.get(Payment, payment_id)
    if payment is None:
        abort(404, description="Payment not found")

    print(f"{Fore.GREEN} api hit1 {Style.RESET_ALL}")
    print(f"{Fore.GREEN} api hit1 {Style.RESET_ALL}")

    if not request.form:
        abort(400, description="Not a JSON or form data")

    print(f"{Fore.GREEN} api hit2 {Style.RESET_ALL}")
    data = request.form
    ignore = [
        "id",
        "created_at",
        "updated_at",
        "__class__",
        "payment_method",
        "group",
        "payer",
    ]
    for key, value in data.items():
        if key not in ignore:
            setattr(payment, key, value)

    files = request.files
    if files:
        for file in files.values():
            if file and file.filename:
                if uploaded_files.file_allowed(file, file.filename):
                    filename = uploaded_files.save(file)
                    attachment = Attachment(url=filename, payment_id=payment.id)
                    attachment.save()
                else:
                    abort(400, description="Invalid file type")

    storage.save()
    global_user_id = g.user.id
    log_audit(global_user_id, "updating payment", status=AuditStatus.COMPLETED, details=None, item_audited=None)
    return jsonify(payment.to_dict()), 200


@app_views.route("/payments/<payment_id>", methods=["DELETE"])
def delete_payment(payment_id):
    """Delete a payment"""
    payment = storage.get(Payment, payment_id)
    if payment is None:
        abort(404, description="Payment not found")

    storage.delete(payment)
    storage.save()
    global_user_id = g.user.id
    log_audit(global_user_id, "deleting payment", status=AuditStatus.COMPLETED, details=None, item_audited=None)
    return jsonify({}), 200


@app_views.route("/uploads/<filename>", methods=["GET"])
def serve_file(filename):
    """Serve a previously uploaded file"""

    upload_dir = os.path.abspath(current_app.config["UPLOADED_FILES_DEST"])
    file_path = os.path.join(upload_dir, filename)

    if not os.path.exists(file_path):
        return jsonify({"error": "File not found"}), 404

    # Determine the content type based on the file extension
    file_extension = os.path.splitext(filename)[1]
    content_type = None

    if file_extension == ".pdf":
        content_type = "application/pdf"
    elif file_extension == ".docx":
        content_type = (
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )

    with open(file_path, "rb") as f:
        file_content = f.read()

    response = make_response(file_content)
    response.headers["Content-Type"] = content_type
    return response


@app_views.route("/uploads/<id>/<filename>", methods=["DELETE"], strict_slashes=False)
def delete_file(id, filename):
    """Delete a previously uploaded file"""
    filename = secure_filename(filename)
    file = storage.get(Attachment, id)
    if file is None:
        return jsonify({"error": "File not found"}), 404

    storage.delete(file)
    storage.save()

    upload_dir = os.path.abspath(current_app.config["UPLOADED_FILES_DEST"])
    file_path = os.path.join(upload_dir, filename)

    if not os.path.exists(file_path):
        return jsonify({"error": "File not found"}), 404

    try:
        os.remove(file_path)
    except OSError as e:
        return jsonify({"error": "Error deleting file"}), 500

    global_user_id = g.user.id
    log_audit(global_user_id, "deleting file", status=AuditStatus.COMPLETED, details=None, item_audited=None)
    return jsonify({"message": "File deleted successfully"}), 200


from flask import send_file


@app_views.route("/download/<filename>", methods=["GET"])
def download_file(filename):
    upload_dir = os.path.abspath(current_app.config["UPLOADED_FILES_DEST"])
    file_path = os.path.join(upload_dir, filename)

    if not os.path.exists(file_path):
        return jsonify({"error": "File not found"}), 404

    return send_file(file_path, as_attachment=True)

