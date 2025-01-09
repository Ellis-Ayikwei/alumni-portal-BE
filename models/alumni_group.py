from http.client import LOCKED
from click import group
from colorama import Fore
from flask import session
from requests import post
from sqlalchemy import (
    Column,
    Index,
    Integer,
    String,
    DateTime,
    Boolean,
    ForeignKey,
    Enum,
    Date,
    Float,
    Table,
    insert,
)
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import enum
from models import group_member
from models.basemodel import BaseModel, Base
from models.contract import Contract
from models.group_member import GroupMember


class Status(enum.Enum):
    ACTIVATED = "ACTIVATED"
    DEACTIVATED = "DEACTIVATED"
    LOCKED = "LOCKED"


admins = Table(
    "admins",
    Base.metadata,
    Column("alumni_group_id", String(60), ForeignKey("alumni_groups.id")),
    Column("user_id", String(60), ForeignKey("users.id")),
)

class AlumniGroup(BaseModel, Base):
    from models.invoice import Invoice

    __tablename__ = "alumni_groups"

    id = Column(String(60), primary_key=True)
    name = Column(String(100), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    school = Column(String(100), nullable=False)
    status = Column(Enum(Status), default=Status.ACTIVATED)
    package_id = Column(
        String(60),
        ForeignKey("insurance_packages.id", ondelete="SET NULL"),
        nullable=True,
    )
    description = Column(String(255), nullable=True)
    current_contract_id = Column(
        String(60),
        ForeignKey("contracts.id", ondelete="SET NULL"),
        nullable=True,
        unique=True,
    )
    current_invoice_id = Column(
        String(60), ForeignKey("invoices.id", ondelete="SET NULL"), nullable=True
    )
    is_one_time_payment_paid = Column(Boolean, default=False, nullable=False)
    president_user_id = Column(
        String(60), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

    president = relationship(
        "User", back_populates="groups_as_president", foreign_keys=[president_user_id]
    )
    payments = relationship("Payment", back_populates="group")
    members = relationship(
        "GroupMember",
        back_populates="group",
        cascade="all, delete-orphan",
        lazy="joined",
    )

    # Explicit foreign key specification for contracts
    contracts = relationship(
        "Contract",
        primaryjoin="AlumniGroup.id == Contract.group_id",
        back_populates="group",
        lazy="joined",
    )
    current_contract = relationship(
        "Contract",
        primaryjoin="AlumniGroup.current_contract_id == Contract.id",
        post_update=True,
        lazy="joined",
    )
    current_invoice = relationship(
        "Invoice",
        primaryjoin="AlumniGroup.current_invoice_id == Invoice.id",
        post_update=True,
    )
    insurance_package = relationship("InsurancePackage", back_populates="groups")
    invoices = relationship(
        "Invoice", foreign_keys=[Invoice.group_id], back_populates="group"
    )
    
    admins = relationship("User", secondary=admins, back_populates="groups_as_admin")

    __table_args__ = (
        Index("ix_alumni_groups_name", "name"),
        Index("ix_alumni_groups_school", "school"),
        Index("ix_alumni_groups_status", "status"),
    )

    def to_dict(self):
        from models import storage
        from models.user import User
        dict_data = super().to_dict()

        if isinstance(self.status, Status):
            dict_data["status"] = self.status.name
        else:
            dict_data["status"] = self.status

        # Contracts list simplified, including only basic info
        dict_data["contracts"] = [
            {"id": contract.id, "name": contract.name} for contract in self.contracts
        ]
        dict_data["current_contract"] = (
            {"id": self.current_contract.id, "name": self.current_contract.name, "total_amount": self.current_contract.total_amount}
            if self.current_contract
            else None
        )
        dict_data["members"] = (
            [{'user_id': member.user_info.id, 'full_name': member.user_info.full_name}  for member in self.members] if self.members else None
        )
        admins = []
        for admin in self.admins:
            user=storage.get_session().query(User).filter(User.id == admin.id).first()
            admins.append({'phone': user.phone, 'full_name': user.full_name, 'user_id': user.id})
        dict_data["admins"] = admins
        return dict_data


    def make_admin(self, user_id):
        from models import storage
        session = storage.get_session()

        max_admins = 3
        if len(self.admins) >= max_admins:
            raise ValueError(f"A maximum of {max_admins} admins are allowed per group")

        current_admin_ids = [admin.id for admin in self.admins]
        if user_id in current_admin_ids:
            raise ValueError("User is already an admin of this group")

        add_admin_stmt = insert(admins).values(alumni_group_id=self.id, user_id=user_id)

        session.execute(add_admin_stmt)
        session.commit()
    
    def remove_admin(self, user_id):
        from models import storage
        session = storage.get_session()
        
        delete_statement = admins.delete().where(
            admins.c.alumni_group_id == self.id,
            admins.c.user_id == user_id
        )
        session.execute(delete_statement)
        session.commit()