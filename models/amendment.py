import datetime
from datetime import datetime as dt
from os import name
from sqlalchemy import Column, DateTime, ForeignKey, Index, Null, String, JSON, Enum
from models.basemodel import Base, BaseModel
from sqlalchemy.orm import relationship
import enum


# Enum for Amendment Status
class AmendmentStatus(enum.Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class Amendment(BaseModel, Base):
    """
    Represents an Amendment to a member's contract.
    The status of an amendment determines whether it has been approved or rejected.
    """

    __tablename__ = "amendments"

    name = Column(String(60), nullable=False)
    contract_id = Column(String(60), ForeignKey("contracts.id"))
    amender_user_id = Column(String(60), ForeignKey("users.id", ondelete="SET NULL"))
    change_date = Column(DateTime, default=datetime.datetime.utcnow)
    new_values = Column(JSON)
    old_values = Column(JSON)
    status = Column(
        Enum(AmendmentStatus), default=AmendmentStatus.PENDING, nullable=False
    )
    approver_id = Column(
        String(60), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    approval_date = Column(DateTime, nullable=True)

    contract = relationship(
        "Contract", back_populates="amendments", foreign_keys=[contract_id]
    )
    amended_by = relationship(
        "User",
        back_populates="amendments",
        foreign_keys=[amender_user_id],
        lazy="joined",
    )
    approved_by = relationship(
        "User", back_populates="amendments", foreign_keys=[approver_id], lazy="joined"
    )

    __table_args__ = (
        Index("ix_amendments_contract_id", "contract_id"),
        Index("ix_amendments_amender_user_id", "amender_user_id"),
        Index("ix_amendments_status", "status"),
    )

    def to_dict(self, save_fs=None):
        dict_data = super().to_dict(save_fs)
        dict_data["status"] = (
            self.status.name
            if isinstance(self.status, AmendmentStatus)
            else self.status
        )
        dict_data["new_values"] = self.new_values
        dict_data["old_values"] = self.old_values
        dict_data["approved_by"] = (
            self.approved_by.to_dict() if self.approved_by else None
        )
        dict_data["amended_by"] = self.amended_by.to_dict() if self.amended_by else None
        dict_data["contract"] = self.contract.to_dict() if self.contract else None
        return dict_data

    def approve_amendment(self, approver_id: str) -> None:
        """
        Approve the amendment, updating the contract with the new values.
        """
        self.status = AmendmentStatus.APPROVED
        self.approver_id = approver_id
        self.approval_date = datetime.datetime.utcnow()
        contract = self.contract

        allowed_fields = [
            "description",
            "name",
            "expiry_date",
            "is_signed",
            "signed_date",
            "date_effective",
            "status",
            "insurance_package_id",
            "policy_number",
        ]

        dates = ["expiry_date", "signed_date", "date_effective"]

        for field, value in self.new_values.items():
            if field in allowed_fields and value is not None:
                if field in dates:
                    if not is_valid_date(value):
                        value = dt.strptime(value, "%a, %d %b %Y %H:%M:%S %Z").date()
                setattr(contract, field, value)

        contract.save()

    def disapprove_amendment(self, user_id: str) -> None:
        self.status = AmendmentStatus.REJECTED
        self.approver_id = user_id
        self.approval_date = datetime.datetime.utcnow()
        contract = self.contract
        contract.save()


def is_valid_date(date_str, format="%Y-%m-%d"):
    try:
        # Attempt to parse the date string with the specified format
        dt.strptime(date_str, format)
        return True  # If parsing succeeds, it's a valid date in "YYYY-MM-DD" format
    except ValueError:
        return False
