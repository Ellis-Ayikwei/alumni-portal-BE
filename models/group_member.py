# models/groupmember.py
from email import policy
from click import group
from colorama import Fore
from sqlalchemy import Column, False_, String, Enum, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from api.v1.src.services.policynumber import generate_policy_number
from models.basemodel import BaseModel, Base
import enum


class Status(enum.Enum):
    PENDING = "PENDING"
    DISAPPROVED = "DISAPPROVED"
    APPROVED = "APPROVED"


class GroupMember(BaseModel, Base):
    __tablename__ = "group_members"

    user_id = Column(
        String(60), ForeignKey("users.id", ondelete="CASCADE"), nullable=True
    )
    added_by = Column(
        String(60), ForeignKey("users.id", ondelete="CASCADE"), nullable=True
    )
    group_id = Column(
        String(60), ForeignKey("alumni_groups.id", ondelete="CASCADE"), nullable=False
    )
    status = Column(Enum(Status), default=Status.PENDING, nullable=False)
    is_approved = Column(Boolean, default=False)
    is_president = Column(Boolean, default=False, nullable=True)
    policy_number = Column(String(11), nullable=True)

    # Relationships
    user_info = relationship(
        "User", back_populates="group_memberships", foreign_keys=[user_id]
    )
    added_by_user = relationship("User", foreign_keys=[added_by])
    group = relationship(
        "AlumniGroup", back_populates="members", foreign_keys=[group_id]
    )
    beneficiaries = relationship("Beneficiary", back_populates="group_members")

    def to_dict(self, save_fs=None):
        dict_data = super().to_dict()
        dict_data["status"] = (
            self.status.name if isinstance(self.status, Status) else self.status
        )
        
        dict_data["added_by_user"] = (
            {'full_name': self.added_by_user.full_name, 'email': self.added_by_user.email, 'phone': self.added_by_user.phone} if self.added_by_user else None
        )
        dict_data["user_info"] = (
            {'full_name': self.user_info.full_name, 'occupation':self.user_info.occupation, 'email': self.user_info.email, 'phone': self.user_info.phone} if self.user_info else None
        )
        dict_data["group"] = [{'name': self.group.name, 'id': self.group.id}] if self.group else None
        return dict_data

    def _approve(self):
        from models.contract_member import ContractMember

        self.is_approved = True
        self.status = "APPROVED"
        if self.policy_number is None:
            self.policy_number = generate_policy_number()
        if (
            self.group.current_contract
            and self.group.current_contract.to_dict()["status"] == "ACTIVE"
        ):
            new_contract_member = ContractMember(
                contract_id=self.group.current_contract_id,
                user_id=self.user_id,
                group_member_id=self.id,
                policy_number=self.policy_number,
            )
            new_contract_member.save()
            print(f"{Fore.RED} - new contract member inserted ")

    def _disapprove(self):
        from models.contract_member import ContractMember
        from models import storage

        self.is_approved = False
        self.status = "DISAPPROVED"
        self.handle_president_removal()
        self._remove_from_contract_members()
        storage.save()

    def _remove_from_contract_members(self):
        from models import storage
        from models.contract_member import ContractMember

        contract_member = (
            storage.get_session()
            .query(ContractMember)
            .filter_by(group_member_id=self.id)
            .first()
        )
        # print("contract member", contract_member)
        print("type ... ", type(contract_member))
        if contract_member is None:
            return
        if (
            self.group.current_contract
            and self.group.current_contract.to_dict()["status"] == "ACTIVE"
        ):
            storage.delete(contract_member)
        return True

    def set_isApproved(self):
        self.is_approved = True

    def handle_president_removal(self):
        if self.is_president:
            alumni_group = self.group
            alumni_group.president_user_id = None
            alumni_group.president = None
            self.is_president = False
