from flask import abort, jsonify, request
from models import storage
from models.contract import Contract, Status as ContractStatus
from models.alumni_group import AlumniGroup
from models.contract_member import ContractMember
from models.invoice import Invoice, InvoiceType

def get_contract_by_id(contract_id: str) -> Contract:
    contract = (
        storage.get_session().query(Contract).filter(Contract.id == contract_id).first()
    )
    if contract is None:
        abort(404, description="Contract not found")
    return contract


def get_group_by_contract(contract: Contract) -> AlumniGroup:
    group = storage.get(AlumniGroup, contract.group_id)
    if group is None:
        abort(404, description="Contract Group not found")
    return group


def validate_request_data() -> dict:
    if not request.get_json():
        abort(400, description="Not a JSON")
    return request.get_json()


def update_contract_fields(contract: Contract, update_data: dict):
    updateable_fields = [
        "group_id",
        "expiry_date",
        "signed_date",
        "status",
        "underwriter_id",
        "insurance_package_id",
    ]
    for key, value in update_data.items():
        if key in updateable_fields:
            setattr(contract, key, value)


def handle_contract_status_update(contract: Contract, status: str, group: AlumniGroup):
    from models.invoice import Invoice

    contract.status = ContractStatus[status]
    if contract.status == ContractStatus.LOCKED:
        contract.lock_contract()
    elif contract.status == ContractStatus.ACTIVE:
        # if group.president is None:
        #     abort(400, description="Group has no president")
        if contract.activate_contract():
            create_invoices_for_active_contract(contract, group)
        else:
            abort(500, description="Failed to activate contract")


def create_invoices_for_active_contract(contract: Contract, group: AlumniGroup):
    from models.invoice import Invoice

    if (
        group.current_invoice is None
        or group.current_invoice.contract_id != contract.id
    ):
        new_group_invoice = Invoice(
            group_id=group.id,
            contract_id=contract.id,
            total_amount=contract.total_amount,
            due_date=contract.expiry_date,
            billed_user_id=group.president_user_id,
            invoice_type=InvoiceType.GROUP_CONTRACT,
        )
        new_group_invoice.save()
        group.current_invoice_id = new_group_invoice.id
        group.save()
        storage.save()
        for contract_member in contract.contract_members:
            new_personal_invoice = Invoice(
                group_id=group.id,
                contract_id=contract.id,
                total_amount=contract.total_amount,
                due_date=contract.expiry_date,
                billed_user_id=contract_member.user_id,
                invoice_type=InvoiceType.INDIVIDUAL_CONTRACT,
            )
            storage.new(new_personal_invoice)
            storage.save()
