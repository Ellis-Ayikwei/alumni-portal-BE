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
from datetime import datetime
import enum
from models.basemodel import BaseModel, Base


class Benefit(BaseModel, Base):
    """
    Represents a benefit available to a member

    Attributes:
        package_id (str): the id of the insurance package
        insurance_package (InsurancePackage): the insurance package
        name (str): the name of the benefit
        description (str): the description of the benefit
        is_active (bool): whether the benefit is available or not
    """

    __tablename__ = "benefits"

    name = Column(String(100), nullable=False)
    package_id = Column(
        String(60),
        ForeignKey("insurance_packages.id", ondelete="CASCADE"),
        nullable=False,
    )
    description = Column(String(255), nullable=True)
    premium_payable = Column(Float, nullable=True)

    insurance_package = relationship("InsurancePackage", back_populates="benefits")
