from click import group
from sqlalchemy import (
    JSON,
    Column,
    Integer,
    String,
    DateTime,
    Boolean,
    ForeignKey,
    Enum,
    Date,
    Float,
)
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import enum
from models.basemodel import BaseModel, Base


# Enum for payment status
class PaymentStatus(enum.Enum):
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


# Payment class definition
class Payment(BaseModel, Base):

    __tablename__ = "payments"

    amount = Column(Float, nullable=False)
    payment_date = Column(DateTime, nullable=False)
    status = Column(Enum(PaymentStatus), default=PaymentStatus.PENDING, nullable=False)
    payment_method_id = Column(
        String(60), ForeignKey("payment_methods.id"), nullable=True
    )
    group_id = Column(String(60), ForeignKey("alumni_groups.id"))
    contract_id = Column(String(60), ForeignKey("contracts.id"))
    invoice_id = Column(String(60), ForeignKey("invoices.id"), nullable=True)
    contract = relationship("Contract", back_populates="payments")
    payment_method = relationship("PaymentMethod", back_populates="payments")
    group = relationship("AlumniGroup", back_populates="payments")
    payer_id = Column(String(60), ForeignKey("users.id"))
    payer = relationship("User", back_populates="payments")
    attachments = relationship("Attachment")
    invoice = relationship(
        "Invoice", back_populates="payments", foreign_keys=[invoice_id]
    )

    @staticmethod
    def validate_amount(amount):
        if amount <= 0:
            raise ValueError("Amount must be a positive value.")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.validate_amount(float(kwargs["amount"]))

    def to_dict(self, save_fs=None):
        dict_data = super().to_dict()
        dict_data["status"] = (
            self.status.name if isinstance(self.status, PaymentStatus) else self.status
        )
        dict_data["payment_method"] = {
            "name": self.payment_method.name if self.payment_method else None
        }
        dict_data["payment_date"] = self.payment_date
        dict_data["group"] = self.group.to_dict() if self.group else None
        dict_data["payer"] = (
            {
                "full_name": self.payer.full_name,
                "email": self.payer.email,
                "phone": self.payer.phone,
                "id": self.payer.id,
                "role": self.payer.role.name,
            }
            if self.payer
            else None
        )
        dict_data["attachments"] = [
            attachment.to_dict() for attachment in self.attachments
        ]

        return dict_data
