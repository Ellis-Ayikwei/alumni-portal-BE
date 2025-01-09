from hmac import new
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
    func,
)
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import enum
from models.basemodel import BaseModel, Base
from models.payment import Payment


class InvoiceStatus(enum.Enum):
    DRAFT = "DRAFT"
    ISSUED = "ISSUED"
    PARTIALLY_PAID = "PARTIALLY_PAID"
    PAID = "PAID"
    OVERDUE = "OVERDUE"
    CANCELLED = "CANCELLED"


class InvoiceType(enum.Enum):
    GROUP_CONTRACT = "GROUP_CONTRACT"
    INDIVIDUAL_CONTRACT = "INDIVIDUAL_CONTRACT"


class Invoice(BaseModel, Base):
    """
    Comprehensive Invoice Model
    """

    __tablename__ = "invoices"

    # Relationship References
    group_id = Column(String(60), ForeignKey("alumni_groups.id"), nullable=True)
    contract_id = Column(
        String(60), ForeignKey("contracts.id", ondelete="SET NULL"), nullable=True
    )
    billed_user_id = Column(String(60), ForeignKey("users.id"))  # Billed user
    insurance_package_id = Column(
        String(60), ForeignKey("insurance_packages.id"), nullable=True
    )

    # Invoice Details
    invoice_number = Column(String(50), unique=True, nullable=False)

    # Financial Details
    total_amount = Column(Float, default=0.0, nullable=False)
    total_paid = Column(Float, default=0, nullable=False)

    # Status Tracking
    status = Column(Enum(InvoiceStatus), default=InvoiceStatus.DRAFT)
    invoice_type = Column(Enum(InvoiceType), nullable=False)

    # Date Tracking
    issue_date = Column(DateTime, default=datetime.utcnow)
    due_date = Column(DateTime, nullable=False)
    paid_date = Column(DateTime)

    # Additional Metadata
    description = Column(String(255))

    # Audit Fields
    created_by = Column(String(60), ForeignKey("users.id"), nullable=True)
    last_updated_by = Column(String(60), ForeignKey("users.id"), nullable=True)

    # Relationships
    group = relationship("AlumniGroup", foreign_keys=[group_id])
    contract = relationship("Contract", foreign_keys=[contract_id])
    billed_user = relationship("User", foreign_keys=[billed_user_id])
    created_by_user = relationship("User", foreign_keys=[created_by])
    last_updated_by_user = relationship("User", foreign_keys=[last_updated_by])

    insurance_package = relationship("InsurancePackage")

    # One-to-Many relationship with Invoice Line Items
    payments = relationship(
        "Payment", back_populates="invoice", foreign_keys=[Payment.invoice_id]
    )

    def __init__(self, *args, **kwargs):
        from models import storage

        super().__init__(*args, **kwargs)

        if "total_amount" in kwargs:
            total_amount = float(kwargs["total_amount"])
            if self.validate_amount(total_amount):
                self.total_amount = total_amount

        if not kwargs.get("invoice_number"):
            with storage.get_session() as session:
                last_invoice = (
                    session.query(Invoice)
                    .order_by(Invoice.invoice_number.desc())
                    .first()
                )
                new_invoice_number = (
                    int(last_invoice.invoice_number.split("-")[1]) + 1
                    if last_invoice
                    else 1
                )
                self.invoice_number = f"INV-{new_invoice_number:06d}"

    def to_dict(self, save_fs=None):
        dict_data = super().to_dict()
        dict_data["status"] = (
            self.status.name if isinstance(self.status, InvoiceStatus) else self.status
        )
        dict_data["invoice_type"] = (
            self.invoice_type.name
            if isinstance(self.invoice_type, InvoiceType)
            else self.invoice_type
        )
        dict_data["billed_user"] = (
            {
                "full_name": self.billed_user.full_name,
                "email": self.billed_user.email,
                "phone": self.billed_user.phone,
                "id": self.billed_user.id,
                "role": self.billed_user.role.name,
            }
            if self.billed_user
            else None
        )
        if self.group:
            current_contract = (
                {
                    "id": self.group.current_contract.id,
                    "name": self.group.current_contract.name,
                }
                if self.group.current_contract
                else None
            )
            insurance_package = (
                {
                    "id": self.group.insurance_package.id,
                    "name": self.group.insurance_package.name,
                }
                if self.group.insurance_package
                else None
            )
            dict_data["group"] = {
                "id": self.group.id,
                "name": self.group.name,
                "currrent_contract": current_contract,
                "insurance_package": insurance_package,
            }
        else:
            dict_data["group"] = None
        # dict_data["group"] = self.group.to_dict() if self.group else None
        # dict_data["contract"] = self.contract.to_dict() if self.contract else None
        # dict_data["user"] = self.user.to_dict() if self.user else None
        return dict_data

    @staticmethod
    def validate_amount(amount: float) -> None:
        if amount <= 0:
            raise ValueError(
                f"Invalid amount '{amount}': Amount must be greater than zero."
            )

    def generate_invoice(self):
        """Generate a simple invoice message to send to the users"""
        message = f"Invoice Number: {self.invoice_number}\n"
        message += f"Bill To: {self.billed_user.full_name}\n"
        message += f"Group: {self.group.name}\n"
        message += f"Insurance Package: {self.insurance_package.name}\n"
        message += f"Total Amount: {self.total_amount}\n"
        message += f"Due Date: {self.due_date.strftime('%Y-%m-%d')}\n"
        return message

    @staticmethod
    def validate_invoice_data(total_amount: float, due_date: datetime) -> None:
        if total_amount <= 0:
            raise ValueError(
                f"Invalid total_amount '{total_amount}': Must be a positive value."
            )
        print("...............tyeo", type(due_date))
        # if due_date < datetime.utcnow().date():
        #     raise ValueError(f"Invalid due_date '{due_date}': Cannot be in the past.")

    # @staticmethod
    # def create_personal_invoice(
    #     user_id: str,
    #     contract_id: str,
    #     total_amount: float,
    #     due_date: datetime,
    #     description: str = None,
    # ) -> 'Invoice':
    #     from models import storage
    #     from models.user import User

    #     # Validate input data
    #     Invoice.validate_invoice_data(total_amount, due_date)

    #     user = storage.get(User, user_id)
    #     if user is None:
    #         raise ValueError(f"User with ID '{user_id}' not found.")

    #     new_personal_invoice = Invoice(
    #         contract_id=contract_id,
    #         billed_user_id=user_id,
    #         total_amount=total_amount,
    #         due_date=due_date,
    #         description=description,
    #         invoice_type = InvoiceType.INDIVIDUAL_CONTRACT
    #     )
    #     new_personal_invoice.save()
    #     return new_personal_invoice

    # @staticmethod
    # def create_group_invoice(
    #     group_id: str,
    #     contract_id:str,
    #     total_amount: float,
    #     due_date: datetime,
    #     description: str = None,
    # ) -> 'Invoice':
    #     from models import storage
    #     from models.alumni_group import AlumniGroup

    #     # Validate input data
    #     Invoice.validate_invoice_data(total_amount, due_date)

    #     group = storage.get(AlumniGroup, group_id)
    #     if group is None:
    #         raise ValueError(f"Group with ID '{group_id}' not found.")

    #     new_group_invoice = Invoice(
    #         group_id=group_id,
    #         contract_id=contract_id,
    #         total_amount=total_amount,
    #         due_date=due_date,
    #         description=description,
    #         invoice_type=InvoiceType.GROUP_CONTRACT
    #     )
    #     new_group_invoice.save()
    #     return new_group_invoice
