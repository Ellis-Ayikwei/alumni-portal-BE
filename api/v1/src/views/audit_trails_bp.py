#!/usr/bin/python3
""" objects that handle all default RestFul API actions for audit_trails """


from flask import Flask, jsonify, request, abort
from models import storage

from models.audit_trails import AuditTrails
from api.v1.src.views import app_views


@app_views.route("/audit_trails", methods=["GET"], strict_slashes=False)
def get_audit_trails():
    """Retrieve audit trails for a given user ID"""

    audit_trails = storage.all(AuditTrails).values()
    dicts = []
    for trail in audit_trails:

        dicts.append(trail.to_dict())
    return jsonify(dicts), 200
