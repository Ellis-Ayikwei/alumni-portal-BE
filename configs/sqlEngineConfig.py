import sqlalchemy
from sqlalchemy import create_engine
import os
"""Instantiate a DBStorage object"""

AP_MYSQL_USER = os.getenv("AP_MYSQL_USER")
AP_MYSQL_PWD = os.getenv("AP_MYSQL_PWD")
AP_MYSQL_HOST = os.getenv("AP_MYSQL_HOST")
AP_MYSQL_DB = os.getenv("AP_MYSQL_DB")
AP_MYSQL_PORT = os.getenv("AP_MYSQL_PORT")

db_url = f"mysql+mysqldb://{AP_MYSQL_USER}:{AP_MYSQL_PWD}@{AP_MYSQL_HOST}:{AP_MYSQL_PORT}/{AP_MYSQL_DB}"
