#!/usr/bin/python3
""" Blueprints for API """
import logging
from flask import Blueprint

# Create Blueprints
app_views = Blueprint(
    "app_views", __name__, url_prefix="/alumni/api/v1", template_folder="../templates"
)
app_auth = Blueprint(
    "app_auth",
    __name__,
    url_prefix="/alumni/api/v1/auth",
    template_folder="../templates",
)

"""Import for the views"""
from .index_bp import *
from .user_bp import *
from .alumni_group_bp import *
from .group_member_bp import *
from .amemdemt_bp import *
from .contract_members_bp import *
from .insurance_package_bp import *
from .paymets_bp import *
from .payment_methods_bp import *
from .contracts_bp import *
from .beneficiary_bp import *
from .authentication.register_bp import *
from .authentication.login_bp import *
from .authentication.logout_bp import *
from .authentication.recorver_password_bp import *
from .audit_trails_bp import *
from .invoices_bp import *


# from .authentication.auth_utility import *
