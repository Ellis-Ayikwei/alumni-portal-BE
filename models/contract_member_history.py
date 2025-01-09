from sqlalchemy import Column, String, DateTime, ForeignKey
import datetime   
from models.basemodel import BaseModel, Base
from sqlalchemy.orm import relationship 
class ContractMemberHistory(BaseModel, Base):
    """
    Tracks the contract members for each version of contract
    """

    __tablename__ = "contract_member_history"

    contract_history_id = Column(String(60), ForeignKey("contract_history.id", ondelete="CASCADE"), index=True, nullable=False)
    contract_id = Column(String(60), ForeignKey("contracts.id"), index=True, nullable=False)
    user_id = Column(String(60), ForeignKey("users.id"), nullable=False)
    group_member_id = Column(String(60), ForeignKey("group_members.id"), nullable=False)
    policy_number = Column(String(60), nullable=True)
    added_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False) # the time when this record was added.

    contract_history = relationship("ContractHistory", back_populates="contract_members_history")
