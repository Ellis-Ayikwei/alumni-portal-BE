# models/beneficiary.py
from datetime import date
from sqlalchemy import Column, String, Date, ForeignKey
from sqlalchemy.orm import relationship
from models.basemodel import BaseModel, Base


class Beneficiary(BaseModel, Base):
    __tablename__ = "beneficiaries"

    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    email = Column(String(120), nullable=False)
    phone = Column(String(20))
    address = Column(String(255))
    other_names = Column(String(50))
    date_of_birth = Column(Date)
    relationship_type = Column(String(50))

    # Foreign keys
    benefactor_user_id = Column(String(60), ForeignKey("users.id"))
    group_member_id = Column(
        String(60), ForeignKey("group_members.id", ondelete="CASCADE")
    )

    # Relationships
    benefactor_user_info = relationship("User", back_populates="beneficiaries")
    group_members = relationship("GroupMember", back_populates="beneficiaries")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.full_name = f"{kwargs.get('first_name')} {kwargs.get('last_name')}"
