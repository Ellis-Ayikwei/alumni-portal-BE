from datetime import date
import re
from colorama import Fore
from flask import Flask, json, jsonify, request, abort, send_file
from api.v1.src.utils.contract_view_utils import get_group_by_contract, handle_contract_status_update, update_contract_fields, validate_request_data
from models import storage
from models.contract import Contract
from models.contract import Status as ContractStatus
from models.alumni_group import AlumniGroup
from flask_jwt_extended import jwt_required
from api.v1.src.views import app_views
from models.contract_member import ContractMember
from api.v1.src.services.auditslogging.logginFn import log_audit
from flask import g
from models.audit_trails import AuditStatus

@app_views.route("/contracts/my_contracts/<string:user_id>", methods=["GET"])
@jwt_required()
def get_contracts_for_user(user_id: str) -> tuple[list[dict], int]:
    """Retrieve all contracts for a user

    Args:
        user_id (str): The ID of the user

    Returns:
        tuple[list[dict], int]: A list of contracts and a status code
    """
    global_user_id = g.user.id
    all_contract_members = storage.all(ContractMember).values()
    user_contracts_memberships: list[ContractMember] = [
        contract_member
        for contract_member in all_contract_members
        if contract_member.user_id == user_id
    ]

    user_contracts: list[dict] = [c.contract for c in user_contracts_memberships]
    contracts_list: list[dict] = []
    for contract in user_contracts:
        print(contract.name)
        contracts_list.append(
            {
                "name": contract.name,
                "id": contract.id,
                "group": contract.group.name,
                "signed_date": contract.signed_date,
                "underwriter": (
                    contract.underwriter.full_name if contract.underwriter else None
                ),
            }
        )

    log_audit(global_user_id, "get contracts for user", status=AuditStatus.COMPLETED, details=None, item_audited=user_id)
    return jsonify(contracts_list), 200


@app_views.route("/contracts/my_contracts/<string:group_id>", methods=["GET"])
@jwt_required()
def get_contracts_for_group(group_id: str) -> tuple[list[dict], int]:
    """Retrieve all contracts for a group

    Args:
        group_id (str): The ID of the group

    Returns:
        tuple[list[dict], int]: A list of contracts and a status code
    """
    global_user_id = g.user.id
    all_contracts = storage.all(Contract).values()
    group_contracts: list[Contract] = [
        contract.to_dict()
        for contract in all_contracts
        if contract.group_id == group_id
    ]

    log_audit(global_user_id, "get contracts for group", status=AuditStatus.COMPLETED, details=None, item_audited=group_id)
    return jsonify(group_contracts), 200


@app_views.route("/contracts", methods=["GET"])
@jwt_required()
def get_all_contracts():
    """Retrieve all contracts"""
    global_user_id = g.user.id
    contracts = storage.all(Contract).values()
    contracts_list = []
    for contract in contracts:
        contract_dict = contract.to_dict()
        contract_dict["insurance_package"] = contract.insurance_package.to_dict()
        contract_dict["underwriter"] = (
            contract.underwriter.to_dict() if contract.underwriter else None
        )
        contracts_list.append(contract_dict)

    # log_audit(global_user_id, "get all contracts", status=AuditStatus.COMPLETED, details=None, item_audited=None)
    return jsonify(contracts_list), 200


@app_views.route("/contracts/<contract_id>", methods=["GET"])
@jwt_required()
def get_contract_by_id(contract_id):
    """Retrieve a specific contract by ID"""
    global_user_id = g.user.id
    contract = storage.get(Contract, contract_id)
    if contract is None:
        log_audit(global_user_id, "get contract by id", status=AuditStatus.FAILED, details="Contract not found", item_audited=contract_id)
        abort(404, description="Contract not found")

    log_audit(global_user_id, "get contract by id", status=AuditStatus.COMPLETED, details=None, item_audited=contract_id)
    return jsonify(contract.to_dict()), 200


@app_views.route("/contracts", methods=["POST"])
@jwt_required()
def create_contract():
    """Create a new contract"""
    global_user_id = g.user.id
    if not request.json:
        log_audit(global_user_id, "create contract", status=AuditStatus.FAILED, details="Not a JSON", item_audited=None)
        abort(400, description="Not a JSON")

    data = request.json
    print(data)
    required_fields = [
        "group_id",
        "expiry_date",
        "underwriter_id",
        "insurance_package_id",
    ]
    for field in required_fields:
        if field not in data:
            log_audit(global_user_id, "create contract", status=AuditStatus.FAILED, details=f"Missing {field}", item_audited=None)
            abort(400, description=f"Missing {field}")

    # Create new Contract object
    new_contract = Contract(**data)
    storage.new(new_contract)
    group = storage.get(AlumniGroup, data["group_id"])
    if not group:
        log_audit(global_user_id, "create contract", status=AuditStatus.FAILED, details="Group not found", item_audited=None)
        abort(404, description="Group not found")

    group.current_contract_id = new_contract.id

    storage.new(group)
    storage.save()

    log_audit(global_user_id, "create contract", status=AuditStatus.COMPLETED, details=None, item_audited=new_contract.id)
    return jsonify(new_contract.to_dict()), 201


@app_views.route("/contracts/<contract_id>", methods=["PUT"])
@jwt_required()
def update_contract(contract_id: str) -> tuple[dict, int]:
    """
    Update an existing contract
        -create new invoice when a contract gets activated

    Args:
        contract_id (str): The ID of the contract to update

    Returns:
        tuple[dict, int]: A JSON response and a status code
    """
    from models.invoice import Invoice
    global_user_id = g.user.id
    contract = storage.get(Contract, contract_id)
    if contract is None:
        log_audit(global_user_id, "update contract", status=AuditStatus.FAILED, details="Contract not found", item_audited=contract_id)
        abort(404, description="Contract not found")

    group = get_group_by_contract(contract)

    update_data = validate_request_data()

    if "action" in request.json and request.json["action"] == "activate":
        if "status" in update_data and update_data["status"] in ContractStatus.__members__:
            handle_contract_status_update(contract, update_data["status"], group)
            storage.save()
            log_audit(global_user_id, "update contract", status=AuditStatus.COMPLETED, details=None, item_audited=contract_id)
            return jsonify({}), 200

    update_contract_fields(contract, update_data)

    storage.save()
    log_audit(global_user_id, "update contract", status=AuditStatus.COMPLETED, details=None, item_audited=contract_id)
    return jsonify({}), 200


@app_views.route("/contracts/<contract_id>", methods=["DELETE"])
@jwt_required()
def delete_contract(contract_id):
    """Delete a contract"""
    global_user_id = g.user.id
    contract = storage.get(Contract, contract_id)
    if contract is None:
        log_audit(global_user_id, "delete contract", status=AuditStatus.FAILED, details="Contract not found", item_audited=contract_id)
        abort(404, description="Contract not found")

    storage.delete(contract)
    storage.save()
    log_audit(global_user_id, "delete contract", status=AuditStatus.COMPLETED, details=None, item_audited=contract_id)
    return jsonify({}), 200


from flask import send_file, abort, current_app
import os


@app_views.route("/contract_doc/<contract_id>", methods=["GET"], strict_slashes=True)
@jwt_required()
def get_contract_doc(contract_id):
    # Fetch the contract from the database
    global_user_id = g.user.id
    contract = storage.get(Contract, contract_id)
    if contract is None:
        log_audit(global_user_id, "get contract doc", status=AuditStatus.FAILED, details="Contract not found", item_audited=contract_id)
        abort(404, description="Contract not found")

    file_path = os.path.join(current_app.root_path, "src/views", "elcont.pdf")
    print(file_path)
    if not os.path.exists(file_path):
        log_audit(global_user_id, "get contract doc", status=AuditStatus.FAILED, details="PDF file not found", item_audited=contract_id)
        abort(403, description="PDF file not found")

    log_audit(global_user_id, "get contract doc", status=AuditStatus.COMPLETED, details=None, item_audited=contract_id)
    return send_file(file_path, mimetype="application/pdf")



@app_views.route("/contracts/<contract_id>/renew", methods=["PUT"])
@jwt_required()
def renew_contract(contract_id):
    """Renew a contract"""
    from flask_jwt_extended import get_jwt_identity
    from dateutil.parser import parse
    global_user_id = g.user.id
    contract = storage.get(Contract, contract_id)
    # request_data = json.loads(request.data.decode('utf-8'))

    # user_id = (
    #             request_data.get("user_id")
    #         )
    user_id = get_jwt_identity()
    print(f"{Fore.GREEN} - {user_id}")
    if contract is None:
        log_audit(global_user_id, "renew contract", status=AuditStatus.FAILED, details="Contract not found", item_audited=contract_id)
        abort(404, description="Contract not found")

    if not request.json:
        log_audit(global_user_id, "renew contract", status=AuditStatus.FAILED, details="Not a JSON", item_audited=contract_id)
        abort(400, description="Not a JSON")

    data = request.json
    # print(data)
    if "expiry_date" not in data:
        log_audit(global_user_id, "renew contract", status=AuditStatus.FAILED, details="Missing new_expiry_date", item_audited=contract_id)
        abort(400, description="Missing new_expiry_date")
    expiry_date = parse(data["expiry_date"]).date()
    date_effective = parse(data["date_effective"]).date()


    print(f"{Fore.GREEN} - {type(expiry_date)} - {type(date_effective)}")
    new_expiry_date = expiry_date
    new_date_effective = date_effective
    if not isinstance(new_expiry_date, date):
        # print(date(new_expiry_date))
        log_audit(global_user_id, "renew contract", status=AuditStatus.FAILED, details="new_expiry_date must be a date", item_audited=contract_id)
        abort(400, description="new_expiry_date must be a date")
    if not isinstance(new_date_effective, date):
        log_audit(global_user_id, "renew contract", status=AuditStatus.FAILED, details="new_date_effective must be a date", item_audited=contract_id)
        abort(400, description="new_date_effective must be a date")

    try:
        contract.renew_contract(new_expiry_date, new_date_effective, user_id)
    except ValueError as e:
        log_audit(global_user_id, "renew contract", status=AuditStatus.FAILED, details=str(e), item_audited=contract_id)
        abort(400, description=str(e))

    log_audit(global_user_id, "renew contract", status=AuditStatus.COMPLETED, details=None, item_audited=contract_id)
    return jsonify({}), 200

