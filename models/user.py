from math import perm
import uuid
from click import group
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
    Table,
)
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import enum
from models.amendment import Amendment
from models.basemodel import BaseModel, Base
import bcrypt
from models.alumni_group import admins

from models.group_member import GroupMember




class UserRole(enum.Enum):
    SUPER_ADMIN = "SUPER_ADMIN"
    ADMIN = "ADMIN"
    REGULAR = "REGULAR"
    UNDERWRITER = "UNDERWRITER"
    PREMIUM_ADMIN = "PREMIUM_ADMIN"
    SALES = "SALES"
    MEMBER = "MEMBER"


user_permission = Table(
    "user_permission",
    Base.metadata,
    Column("user_id", String(60), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    Column("permission_id", String(60), ForeignKey("permissions.id"), primary_key=True),
)

class User(BaseModel, Base):
    __tablename__ = "users"

    id = Column(String(60), primary_key=True)
    email = Column(String(120), unique=True, nullable=False)
    username = Column(String(50), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    middle_names = Column(String(100), nullable=True)
    gender = Column(String(10), nullable=True)
    role = Column(Enum(UserRole), default=UserRole.REGULAR, nullable=False)
    azure_id = Column(String(255), unique=True)
    is_active = Column(Boolean, default=True)
    dob = Column(Date, nullable=True)
    phone = Column(String(20), nullable=True)
    occupation = Column(String(50), nullable=True)
    address = Column(String(255), nullable=True)
    other_names = Column(String(50), nullable=True)
    full_name = Column(String(100), nullable=True)
    payments = relationship("Payment", back_populates="payer")
    permissions = relationship("Permission", secondary=user_permission, back_populates="users")


    # Relationship to AlumniGroup where the user is the president
    beneficiaries = relationship("Beneficiary", back_populates="benefactor_user_info")
    groups_as_president = relationship(
        "AlumniGroup",
        back_populates="president",
        foreign_keys="AlumniGroup.president_user_id",
        cascade="all, delete-orphan",
    )
    
    
    groups_as_admin = relationship(
        "AlumniGroup",
        secondary=admins,
        back_populates="admins",
        lazy="joined",
    )
    
    group_memberships = relationship(
        "GroupMember",
        back_populates="user_info",
        foreign_keys=[GroupMember.user_id],
        cascade="all, delete-orphan",
    )
    amendments = relationship(
        "Amendment",
        foreign_keys=[Amendment.amender_user_id],
        back_populates="amended_by",
    )

    def __init__(self, *args, **kwargs):
        """Initialization of the user"""
        super().__init__(*args, **kwargs)
        if "password" in kwargs:
            encoded_password = kwargs["password"].encode("utf-8")
            self.password = bcrypt.hashpw(encoded_password, bcrypt.gensalt())
        if "first_name" in kwargs and "last_name" in kwargs:
            self.full_name = (
                f"{kwargs['first_name']} {kwargs['last_name']} {kwargs['other_names'] if 'other_names' in kwargs else ''}" 
            )

    def to_dict(self, save_fs=None) -> dict:
        from models.permission import Action, ResourceType

        """Return a dictionary representation of the user, ensuring enum conversion"""
        user_dict = super().to_dict()

        # Convert the role enum to its string representation for serialization
        user_dict["role"] = (
            self.role.name if isinstance(self.role, UserRole) else self.role
        )

        full_name = (
            self.full_name if self.full_name else f"{self.first_name} {self.last_name}"
        )
        user_dict["full_name"] = full_name
        user_dict["groups_as_admin"] = [group.to_dict() for group in self.groups_as_admin] if self.groups_as_admin else None
        user_dict["permissions"] = [
            {
                "id": perm.id,
                "name": perm.name,
                "resource_type": (
                    perm.resource_type.name if isinstance(perm.resource_type, ResourceType) else perm.resource_type
                ),
                "action": (
                    perm.action.name if isinstance(perm.action, Action) else perm.action
                ),
                "description": perm.description,
            }
            for perm in self.permissions
        ] if self.permissions else None
        return user_dict


    @staticmethod
    def validate_password_strength(password: str) -> bool:
        """Ensure the password meets basic complexity requirements."""
        import re

        return bool(
            re.match(r"^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d@$!%*?&]{8,}$", password)
        )

    def verify_password(self, password: str) -> bool:
        """Verify the password against the hashed password."""
        try:

            # print((password.encode("utf-8"), self.password))
            return (
                bcrypt.checkpw(password.encode("utf-8"), self.password.encode("utf-8"))
                if self.password
                else False
            )
        except (ValueError, TypeError):
            return False

    def update_password(self, new_password: str):
        """Update the password with a new hash."""
        # if not self.validate_password_strength(new_password):
        #     raise ValueError("Password does not meet complexity requirements.")
        self.password = bcrypt.hashpw(new_password.encode("utf-8"), bcrypt.gensalt())

    def reset_password(self, current_password: str, new_password: str) -> bool:
        """Reset the password if the current password is verified."""
        if self.verify_password(current_password):
            self.update_password(new_password)
            # Log password reset success (replace with a proper logging system)
            print(f"Password reset successfully for user.")
            return True
        # Log failed reset attempt (replace with a proper logging system)
        print(f"Failed password reset attempt for user.")
        return False
