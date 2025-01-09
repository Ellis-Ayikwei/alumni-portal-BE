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
)
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import enum
from models.basemodel import BaseModel, Base


class ContractMember(BaseModel, Base):
    __tablename__ = "contract_members"

    contract_id = Column(String(60), ForeignKey("contracts.id"))
    user_id = Column(
        String(60), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    group_member_id = Column(
        String(60), ForeignKey("group_members.id", ondelete="CASCADE")
    )
    policy_number = Column(String(11), nullable=True)

    user = relationship("User", lazy="joined")
    contract = relationship("Contract", back_populates="contract_members")
    group_member = relationship("GroupMember", backref="contract_member", lazy="joined")

    def to_dict(self, save_fs=None):
        dict_data = super().to_dict(save_fs)
        dict_data["user"] = self.user.to_dict() if self.user else None
        dict_data["group_member"] = (
            self.group_member.to_dict() if self.group_member else None
        )
        return dict_data
