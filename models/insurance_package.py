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


class PaymentFrequency(enum.Enum):
    MONTHLY = "MONTHLY"
    QUARTERLY = "QUARTERLY"
    ANNUALLY = "ANNUALLY"
    ONETIME = "ONETIME"


class InsurancePackage(BaseModel, Base):
    """
    Represents an insurance package

    Attributes:
        name (str): Package name
        description (str): Package description
        price (float): Package price
        benefits (str): Package benefits
        payment_terms (str): Package payment terms
        payment_interval (str): Package payment interval (e.g. monthly, quarterly, etc.)
        image_url (str): Package image URL
        is_active (bool): Whether the package is active
    """

    __tablename__ = "insurance_packages"

    name = Column(String(100), nullable=False)
    description = Column(String(255), nullable=False)
    sum_assured = Column(Float, nullable=False)
    monthly_premium_ghs = Column(Float, nullable=False)
    annual_premium_ghs = Column(Float, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    groups = relationship("AlumniGroup", back_populates="insurance_package")
    benefits = relationship(
        "Benefit", back_populates="insurance_package", cascade="all, delete-orphan"
    )
