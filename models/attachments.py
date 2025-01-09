from sqlalchemy import JSON, Column, String, ForeignKey
from sqlalchemy.orm import relationship
from models.basemodel import BaseModel, Base


class Attachment(BaseModel, Base):
    __tablename__ = "attachments"

    url = Column(String(255), nullable=False)
    payment_id = Column(
        String(60), ForeignKey("payments.id", ondelete="CASCADE"), nullable=False
    )
