#!/usr/bin/python3
from api.v1.src.views.alumni_group_bp import require_permission
from models.engine.db_storage import DBStorage

storage = DBStorage()
storage.reload()
