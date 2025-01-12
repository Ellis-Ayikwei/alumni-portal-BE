from sqlalchemy import Column, String, Boolean, ForeignKey, Enum
from sqlalchemy.orm import relationship
from models.alumni_group import Fore
from models.basemodel import BaseModel, Base
import enum


class ResourceType(enum.Enum):
    USER = "user"
    ALUMNI_GROUP = "alumni_group"
    GROUP_MEMBER = "group_member"
    AMENDMENT = "amendment"
    CONTRACT = "contract"
    CONTRACT_MEMBER = "contract_member"
    INSURANCE_PACKAGE = "insurance_package"
    PAYMENT = "payment"
    PAYMENT_METHOD = "payment_method"
    BENEFICIARY = "beneficiary"
    INVOICE = "invoice"
    AUDIT = "audit"
    FILE = "file"

class Action(enum.Enum):
    VIEW = "view"
    ADD = "add"
    CHANGE = "change"
    DELETE = "delete"
    MANAGE = "manage"
    GENERATE = "generate"
    VALIDATE = "validate"
    SEND = "send"
    DOWNLOAD = "download"



class Permission(BaseModel, Base):
    # from models import user_permission
    __tablename__ = 'permissions'

    id = Column(String(60), primary_key=True)
    name = Column(String(100), nullable=False)
    resource_type = Column(Enum(ResourceType), nullable=False)
    action = Column(Enum(Action), nullable=False)
    description = Column(String(255))
    
    
    # user_id = Column(String(60), ForeignKey('users.id'))
    
    users = relationship("User",
                        secondary="user_permission",
                        back_populates="permissions",
                        lazy="joined"
                        )


    def to_dict(self, save_fs=None):
        dict_data = super().to_dict(save_fs)
        dict_data["resource_type"] = self.resource_type.name
        dict_data["action"] = self.action.name
        dict_data["users"] = [user.id for user in self.users]
        return dict_data
    

    @classmethod
    def get_role_permissions(cls):
        """Define permissions for each role"""
        return {
            
            
            
            'SUPER_ADMIN': [
                # Has all permissions
                (resource.value, action.value) 
                for resource in ResourceType 
                for action in Action
            ],
            'ADMIN': [
                # Alumni Group permissions
                # (ResourceType.ALUMNI_GROUP.value, Action.ADD.value),
                # (ResourceType.ALUMNI_GROUP.value, Action.VIEW.value),
                # (ResourceType.ALUMNI_GROUP.value, Action.CHANGE.value),
                # (ResourceType.ALUMNI_GROUP.value, Action.DELETE.value),
                # # Group Member permissions
                # (ResourceType.GROUP_MEMBER.value, Action.ADD.value),
                # (ResourceType.GROUP_MEMBER.value, Action.VIEW.value),
                # (ResourceType.GROUP_MEMBER.value, Action.CHANGE.value),
                # (ResourceType.GROUP_MEMBER.value, Action.VALIDATE.value),
                # # Contract permissions
                # (ResourceType.CONTRACT.value, Action.VIEW.value),
                # # Amendment permissions
                # (ResourceType.AMENDMENT.value, Action.ADD.value),
                # (ResourceType.AMENDMENT.value, Action.VIEW.value),
                # # User permissions
                # (ResourceType.USER.value, Action.ADD.value),
                # (ResourceType.USER.value, Action.VIEW.value),
                # (ResourceType.USER.value, Action.CHANGE.value),
                (resource.value, action.value)
                for resource in ResourceType
                for action in Action
            ],
            'REGULAR': [  # President of Group
                # Alumni Group permissions (own group only)
                (ResourceType.ALUMNI_GROUP.value, Action.VIEW.value),
                (ResourceType.ALUMNI_GROUP.value, Action.CHANGE.value),
                # Group Member permissions
                (ResourceType.GROUP_MEMBER.value, Action.ADD.value),
                (ResourceType.GROUP_MEMBER.value, Action.VIEW.value),
                (ResourceType.GROUP_MEMBER.value, Action.DELETE.value),
                # Payment permissions
                (ResourceType.PAYMENT.value, Action.ADD.value),
                (ResourceType.PAYMENT.value, Action.VIEW.value),
                # Invoice permissions
                (ResourceType.INVOICE.value, Action.VIEW.value),
            ],
            'UNDERWRITER': [
                # Contract permissions
                (ResourceType.CONTRACT.value, Action.ADD.value),
                (ResourceType.CONTRACT.value, Action.VIEW.value),
                (ResourceType.CONTRACT.value, Action.CHANGE.value),
                # Contract Member permissions
                (ResourceType.CONTRACT_MEMBER.value, Action.ADD.value),
                (ResourceType.CONTRACT_MEMBER.value, Action.VIEW.value),
            ],
            'PREMIUM_ADMIN': [
                # Alumni Group permissions
                (ResourceType.ALUMNI_GROUP.value, Action.VIEW.value),
                (ResourceType.ALUMNI_GROUP.value, Action.CHANGE.value),
                # Group Member permissions
                (ResourceType.GROUP_MEMBER.value, Action.VALIDATE.value),
                (ResourceType.GROUP_MEMBER.value, Action.VIEW.value),
            ],
            'SALES': [
                # Alumni Group permissions
                (ResourceType.ALUMNI_GROUP.value, Action.ADD.value),
                (ResourceType.ALUMNI_GROUP.value, Action.VIEW.value),
                # Group Member permissions
                (ResourceType.GROUP_MEMBER.value, Action.ADD.value),
                (ResourceType.GROUP_MEMBER.value, Action.VIEW.value),
            ],
            'MEMBER': [
                # Basic view permissions
                (ResourceType.ALUMNI_GROUP.value, Action.VIEW.value),
                (ResourceType.CONTRACT.value, Action.VIEW.value),
                # Beneficiary permissions
                (ResourceType.BENEFICIARY.value, Action.ADD.value),
                (ResourceType.BENEFICIARY.value, Action.VIEW.value),
                (ResourceType.BENEFICIARY.value, Action.CHANGE.value),
            ]
        }

class PermissionManager:
    @staticmethod
    def check_permission(user, resource_type, action):
        """Check if user has permission for specific resource and action"""
        from models.user import UserRole
        
        if user.role == UserRole.SUPER_ADMIN:
            return True
        
        print(f"{Fore.RED} - Reached the the check permission {Fore.RESET}")
        print(user.full_name)
        print(user.permissions[0].resource_type)
        return any(
            perm.resource_type.value == resource_type and perm.action.value == action
            for perm in user.permissions
        )


    @staticmethod
    def add_permissions_to_user(user, new_permissions):
        """Add new permissions to user"""
        from models import storage
        
        session = storage.get_session()
        existing_permissions = {(perm.resource_type.value, perm.action.value) for perm in user.permissions}
        for resource_type, action in new_permissions:
            if (resource_type, action) not in existing_permissions:
                permission = session.query(Permission).filter_by(resource_type=ResourceType(resource_type), action=Action(action)).first()
                if permission:
                    user.permissions.append(permission)
        session.commit()
        
    @staticmethod
    def add_permissions_to_user(user, new_permissions):
        """
        Add new permissions to a user with row-level locking to avoid race conditions.
        """
        from models import storage
        from models.user import User

        session = storage.get_session()
        try:
            # Lock the user row
            locked_user = session.query(User).filter_by(id=user.id).with_for_update().one()
            valid_permissions = [perm for perm in new_permissions if perm and perm.id]

            for permission in valid_permissions:
                if permission not in locked_user.permissions:
                    locked_user.permissions.append(permission)
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

        
    @staticmethod
    def setup_user_permissions(user):
        from models import storage
        
        session  = storage.get_session()
        role_permissions = Permission.get_role_permissions().get(user.role.name, [])
        
        user.permissions = []
        session.commit()

        for resource_type, action in role_permissions:
            permission = session.query(Permission).filter_by(resource_type=ResourceType(resource_type), action=Action(action)).first()
            if not permission:
                try:
                    permission = Permission(
                        name=f"Can {action} {resource_type}",
                        resource_type=ResourceType(resource_type),
                        action=Action(action),
                        description=f"Can {action} {resource_type}",
                    )
                    session.add(permission)
                    session.commit()
                except Exception:
                    session.rollback()
                    permission = session.query(Permission).filter_by(resource_type=ResourceType(resource_type), action=Action(action)).first()
            user.permissions.append(permission)
        session.commit()
        
        
    @staticmethod
    def remove_permissions_from_user(user, permissions_to_remove):
        """
        Remove permissions from a user.
        :param user: User object.
        :param permissions_to_remove: List of Permission objects to remove.
        """
        from models import storage

        session = storage.get_session()
        try:
            for permission in permissions_to_remove:
                if permission and permission in user.permissions:
                    user.permissions.remove(permission)
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
  
    @staticmethod
    def setup_all_permissions():
        from models.user import UserRole
        from models import storage
        
        session  = storage.get_session()
        for role in UserRole:
            # role_permissions = Permission.get_role_permissions().get(role.name, [])
            role_permissions = [(resource.value, action.value) for resource in ResourceType for action in Action]
            
            for resource_type, action in role_permissions:
                permission = session.query(Permission).filter_by(resource_type=ResourceType(resource_type), action=Action(action)).first()
                if not permission:
                    try:
                        permission = Permission(
                            name=f"Can {action} {resource_type}",
                            resource_type=ResourceType(resource_type),
                            action=Action(action),
                            description=f"Can {action} {resource_type}",
                        )
                        session.add(permission)
                        session.commit()
                    except Exception:
                        session.rollback()
                        permission = session.query(Permission).filter_by(resource_type=ResourceType(resource_type), action=Action(action)).first()
                session.commit()

