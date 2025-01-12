#!/usr/bin/python3
"""the blue print for the index"""
import json
from urllib import response
from flask import Flask, jsonify, render_template
from api.v1.src.views import app_views


@app_views.route("/status")
def status():
    """to check the status of the api"""
    return jsonify({"status": "ok you are connected to sprout collab1 api"})


@app_views.route("/", strict_slashes=False)
def index():
    """the index route"""
    return jsonify({"response": "successful hit to the api"}), 200


@app_views.route("/stats")
def storage_counts():
    """
    return counts of all classes in storage
    """
    from models import storage
    cls_counts = {
        "Users": storage.count("User"),
        "Beneficiaries": storage.count("Beneficiary"),
        "Alumin Groups": storage.count("AlumniGroup"),
        "GroupMembers": storage.count("GroupMember"),
        "Amendments": storage.count("Amendment"),
        "Contracts": storage.count("Contract"),
        "Paymemts": storage.count("Payment"),
    }
    return jsonify(cls_counts)
