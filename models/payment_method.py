from sqlalchemy import Column, String
from sqlalchemy.orm import relationship
from models import payment
from models.basemodel import BaseModel, Base


class PaymentMethod(BaseModel, Base):
    __tablename__ = "payment_methods"

    name = Column(String(60), nullable=False, unique=True)
    payments = relationship("Payment", back_populates="payment_method")

    def to_dict(self, save_fs=None):
        dict_data = super().to_dict()
        dict_data["name"] = self.name
        return dict_data
