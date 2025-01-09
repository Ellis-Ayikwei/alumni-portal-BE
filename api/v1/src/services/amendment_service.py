from models import amendment
from models.amendment import Amendment
from models import storage
from models.contract import Contract
from models.amendment import AmendmentStatus


def log_change(contract, key, old_value, new_value, amended_by):
    """
    Logs the changes made to a contract.

    Args:
        contract (Contract): The contract being modified.
        key (str): The attribute being changed.
        old_value: The old value of the attribute.
        new_value: The new value of the attribute.
        amended_by (str): The user who made the amendment.
    """
    # Implement the logging logic here
    pass


def apply_approved_amendment_to_contract(
    contract_id: str, amendment_id: str
) -> Contract:
    """
    Applies the changes from an approved amendment to the associated contract.

    Args:
        contract_id (str): The ID of the contract to update.
        amendment_id (str): The ID of the approved Amendment to apply.

    Returns:
        Contract: The updated Contract instance.
    """
    contract = storage.get(Contract, contract_id)
    amendment = storage.get(Amendment, amendment_id)

    if amendment.status != AmendmentStatus.APPROVED:
        raise ValueError("Amendment has not been approved yet")

    for key, new_value in amendment.new_values.items():
        if hasattr(contract, key):
            old_value = getattr(contract, key)
            setattr(contract, key, new_value)
            log_change(contract, key, old_value, new_value, amendment.amended_by)

    storage.save()
    return contract
