from email import policy
from hmac import new
from multiprocessing import Value
from typing import Optional
from click import group
from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Boolean,
    ForeignKey,
    Enum,
    Date,
    Float,
    true,
)
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import date, datetime
from colorama import Fore
import enum
from api.v1.src.services.policynumber import generate_policy_number
from models import payment
from models.amendment import AmendmentStatus
from models.basemodel import BaseModel, Base
import json

from models.contract_member import ContractMember
from models.contract_member_history import ContractMemberHistory


class Status(enum.Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    LOCKED = "LOCKED"
    EXPIRED = "EXPIRED"
    TERMINATED = "TERMINATED"


class ContractType(enum.Enum):
    PERSONAL = "PERSONAL"
    GROUP = "GROUP"


class Contract(BaseModel, Base):
    """
    Represents an insurance contract between an underwriter and an alumni group
    """
    __tablename__ = "contracts"
    name = Column(String(100), nullable=False)
    group_id = Column(String(60), ForeignKey("alumni_groups.id"), nullable=True)
    expiry_date = Column(Date, nullable=True)
    date_effective = Column(Date, nullable=True)
    is_signed = Column(Boolean, default=False)
    signed_date = Column(Date, nullable=True)
    status = Column(Enum(Status), default=Status.INACTIVE, nullable=False)
    last_renewed = Column(Date, nullable=True)
    renewal_count = Column(Integer, default=0, nullable=False)
    version = Column(Integer, default=1, nullable=False)
    underwriter_id = Column(
        String(60), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    insurance_package_id = Column(
        String(60),
        ForeignKey("insurance_packages.id", ondelete="SET NULL"),
        nullable=True,
    )
    description = Column(String(255), nullable=True)
    total_amount = Column(Float, default=0.0, nullable=False)
    
    # Relationships
    payments = relationship("Payment", back_populates="contract")
    group = relationship(
        "AlumniGroup", back_populates="contracts", foreign_keys=[group_id]
    )
    contract_members = relationship(
        "ContractMember", back_populates="contract", cascade="all, delete-orphan"
    )
    contract_history = relationship(
        "ContractHistory", back_populates="contract", cascade="all, delete-orphan"
    )
    underwriter = relationship("User", backref="contracts", lazy="joined")
    amendments = relationship("Amendment", back_populates="contract", lazy="joined")
    insurance_package = relationship(
        "InsurancePackage", backref="contracts", lazy="joined"
    )

    def to_dict(self, save_fs=None):
        dict_data = super().to_dict()
        dict_data["status"] = (
            self.status.name if isinstance(self.status, Status) else self.status
        )
        dict_data["group"] = self.group.to_dict() if self.group else None
        dict_data["underwriter"] = (
            self.underwriter.to_dict() if self.underwriter else None
        )
        dict_data["insurance_package"] = (
            self.insurance_package.to_dict() if self.insurance_package else None
        )
        dict_data["amendments"] = (
            [
                {
                    "name": amendment.name,
                    "new_values": amendment.new_values,
                    "old_values": amendment.old_values,
                    "approved_by": (
                        amendment.approved_by.to_dict()
                        if amendment.approved_by
                        else None
                    ),
                    "amended_by": (
                        amendment.amended_by.to_dict() if amendment.amended_by else None
                    ),
                    "status": (
                        amendment.status.name
                        if isinstance(amendment.status, AmendmentStatus)
                        else amendment.status
                    ),
                    "change_date": amendment.change_date.isoformat(),
                }
                for amendment in self.amendments
            ]
            if self.amendments
            else None
        )
        dict_data["contract_members"] = (
            [member.to_dict() for member in self.contract_members]
            if self.contract_members
            else None
        )
        return dict_data

    def lock_contract(self) -> Boolean:
        """Lock the contract, preventing further changes.

        This method sets the contract status to LOCKED and populates the contract_members list with the members of the group that have been approved and are part of the group.
        """
        if self.group:
            # approved_group_members = [
            #     member
            #     for member in self.group.members
            #     if member.to_dict()["status"] == "APPROVED" and member.to_dict()["is_approved"] == True or member.to_dict().status == "APPROVED" and member.to_dict().is_approved and member.group_id not in [contract.group_id for contract in self.group.contracts]
            # ]

            # for group_member in approved_group_members:
            #     if group_member.user_id in [contract_member.user_id for contract_member in self.contract_members]:
            #         continue
            #     ContractMember(
            #         contract_id=self.id,
            #         user_id=group_member.user_id,
            #         group_member_id=group_member.id
            #     ).save()
            self.status = "LOCKED"
            return true

    def __repr__(self):
        return json.dumps(self.to_dict(), default=lambda o: o.__dict__, indent=4)

    def activate_contract(self) -> Boolean:
        from models import storage
        from models.group_member import GroupMember
        from models.alumni_group import AlumniGroup

        """Activate the contract, setting the status
            to ACTIVE and populating the contract_members
            list with the members of the group that have been
            approved and are part of the group.
        """

        
        if self.group_id:
            group = storage.get_session().query(AlumniGroup).get(self.group_id)

        if group:
            approved_group_members = (
                storage.get_session()
                .query(GroupMember)
                .filter(
                    GroupMember.group_id == group.id,
                    GroupMember.status == "APPROVED",
                    GroupMember.is_approved.is_(True),
                )
                .all()
            )


            self.group.package_id = self.insurance_package_id
            for group_member in approved_group_members:
                if group_member.user_id in [
                    contract_member.user_id for contract_member in self.contract_members
                ]:
                    continue
                generated_policy_number = generate_policy_number()
                if group_member.policy_number is None:
                    group_member.policy_number = generated_policy_number
                ContractMember(
                    contract_id=self.id,
                    user_id=group_member.user_id,
                    group_member_id=group_member.id,
                    policy_number=group_member.policy_number,
                ).save()
                group_member.save()
            self.status = "ACTIVE"
            self.save()
            return True
        
    def serialize_contract_members(self) -> list[dict]:
        """
        Serializes the contract members into a JSON-compatible format.

        Returns:
            list[dict]: A list of serialized contract members, where each
                dictionary contains the following keys:

                - user_id (str): The ID of the user.
                - group_member_id (str): The ID of the group member.
                - policy_number (str): The policy number of the contract member.
                - added_at (str): The datetime when the contract member was added.
        """
        return [
            {
                "user_id": member.user_id,
                "group_member_id": member.group_member_id,
                "policy_number": member.policy_number,
                "added_at": member.created_at.isoformat(),  # Capture when added
            }
            for member in self.contract_members
        ]



    def renew_contract(self, new_expiry_date: date, new_date_effective: date, user_id: Optional[str] = None) -> bool:
        """
        Renews the contract by extending its expiry date and updating status.
        """
        from models import storage
        from models.contract_history import ContractHistory

        if self.status == Status.TERMINATED:
            raise ValueError(f"Contract cannot be renewed as it is {self.status}.")

        if new_expiry_date <= self.expiry_date:
            raise ValueError("New expiry date must be later than the current expiry date.")
        if new_date_effective <= self.date_effective or new_date_effective <= self.expiry_date:
            raise ValueError("New date effective must be greater than the previous expiry date and the date effective.")
        
        # Record renewal in ContractHistory
        contract_history = ContractHistory(
            contract_id=self.id,
            name=self.name,
            expiry_date=new_expiry_date,
            date_effective=self.date_effective,
            is_signed=self.is_signed,
            signed_date=self.signed_date,
            status=Status.ACTIVE.name,
            total_amount=self.total_amount,
            created_by=user_id
        )
        contract_history.save()

        # Create history records for contract members
        for member in self.contract_members:
            ContractMemberHistory(
                contract_history_id=contract_history.id,
                contract_id=self.id,
                user_id=member.user_id,
                group_member_id=member.group_member_id,
                policy_number=member.policy_number
            ).save()

        # Update contract attributes
        self.expiry_date = new_expiry_date
        self.date_effective = new_date_effective
        self.status = Status.ACTIVE.name
        self.last_renewed = datetime.now().date()
        self.renewal_count += 1
        self.version += 1
        self.updated_by = user_id
        self.save()

        return True

