#!/usr/bin/python3
import datetime
from colorama import init, Fore, Style

from models import storage
from datetime import date as dt

import models
from models.basemodel import BaseModel, Base
from models.beneficiary import Beneficiary
from models.user import User
from models.contract import Contract
from models.contract_member import ContractMember
from models.payment import Payment
from models.group_member import GroupMember
from models.alumni_group import AlumniGroup

# "013f6e28-855a-4c9b-8213-1a911aefe22c"

# storage.close()
init(autoreset=True)

storage.reload()


def add_new_users():
    for i in range(30):
        new_user = User(
            first_name=f"{i}FirstName",
            last_name=f"{i}LasttName",
            username=f"userNo.{i}",
            password="@Toshib123",
            dob=datetime.datetime.utcnow(),
            phone_number=f"123{i + 1}567{i}90",
            role="SUPER_ADMIN",
            address=f"1{i + 3}{i}3 Main St",
            occupation=f"{i}Occupation",
            email=f"userNo.{i}@example.com",
        )
        new_user.save()
    print(f"{Fore.BLUE}users successfully inserted!")


add_new_users()
