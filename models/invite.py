import code
from datetime import datetime
from click import DateTime, group
from sqlalchemy import Column, Date, ForeignKey, Integer, String
from models import user
from models.basemodel import BaseModel, Base


class Invite(BaseModel, Base):
    """
    A model representing an invite code
    """

    __tablename__ = "invites"

    code = Column(String(100), nullable=False)
    last_used_at = Column(Date, nullable=True)
    group_id = Column(
        String(60), ForeignKey("alumni_groups.id", ondelete="CASCADE"), nullable=False
    )
    creator_id = Column(String(60), ForeignKey("users.id"), nullable=True)
    times_used = Column(Integer, default=0)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.code = generate_base62_uuid(12)


def generate_base62_uuid(length=8):
    """
    Generate a Base62-encoded UUID4 with a specified length.

    Parameters:
        length (int): Desired length of the generated ID.

    Returns:
        str: A Base62-encoded UUID4 string.

    """

    import uuid
    import base64

    full_uuid = uuid.uuid4()
    uuid_bytes = full_uuid.bytes
    base64_uuid = base64.urlsafe_b64encode(uuid_bytes).decode("utf-8")
    base62_uuid = base64_uuid.rstrip("=").replace("-", "").replace("_", "")[:length]
    
    return base62_uuid
