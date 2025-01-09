from sqlalchemy import (
    JSON,
    Column,
    ForeignKey,
    String,
    Integer,
    Date,
    DateTime,
    Float,
    Enum,
    Boolean,
    func,
    text
)
from datetime import datetime
import enum

from models.basemodel import BaseModel, Base
from sqlalchemy.orm import relationship


class Status(enum.Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    LOCKED = "LOCKED"
    EXPIRED = "EXPIRED"
    TERMINATED = "TERMINATED"

class ContractHistory(BaseModel, Base):
    __tablename__ = "contract_history"

    contract_id = Column(String(60), ForeignKey("contracts.id"), index=True, nullable=False)
    version = Column(Integer, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    expiry_date = Column(Date, nullable=True)
    date_effective = Column(Date, nullable=True)
    is_signed = Column(Boolean, default=False)
    signed_date = Column(Date, nullable=True)
    status = Column(Enum(Status), nullable=False)
    total_amount = Column(Float, default=0.0, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    contract = relationship("Contract", back_populates="contract_history")
    contract_members_history = relationship("ContractMemberHistory", back_populates="contract_history", cascade="all, delete-orphan")
    created_by = Column(String(60), ForeignKey("users.id"), nullable=True)
    updated_by = Column(String(60), ForeignKey("users.id"), nullable=True)
    
    
    
    def set_version(self):
        from models import storage
        session = storage.get_session()
        if session:
            current_max_version = session.query(func.coalesce(func.max(ContractHistory.version), 0)).filter(
                ContractHistory.contract_id == self.contract_id
            ).scalar()
            self.version = current_max_version + 1



    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_version()