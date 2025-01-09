#!/usr/bin/python3
"""logging the audit trail"""
from flask import request, abort

import datetime


def log_audit(user_id, action, status="PENDING", details=None, item_audited=None):
    """Logs an audit trail entry."""
    from models.audit_trails import AuditTrails

    print("reached the log audit")
    try:
        # Create a new AuditTrails entry
        audit_entry = AuditTrails(
            user_id=user_id,
            action=action,
            status=status,
            created_at=datetime.datetime.now(datetime.timezone.utc),
            details=details or {},
            item_audited_id=item_audited,
        )
        # Save to the database
        audit_entry.save()
        user_name = audit_entry.user.full_name
        return user_name
    except Exception as e:
        # Handle database save failures
        app_auth_error_logger.error(f"Error saving audit trail: {str(e)}")


import logging
from logging.handlers import RotatingFileHandler


# Function to set up a logger with a unique file
def setup_logger(name, log_file, level=logging.INFO):
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # File handler for this logger
    file_handler = RotatingFileHandler(
        log_file, maxBytes=5 * 1024 * 1024, backupCount=3
    )
    file_handler.setFormatter(
        logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    )

    # console handler
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(
        logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    )

    # Attach handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)

    return logger


# Set up separate loggers with different log files and levels
app_views_info_logger = setup_logger(
    "app_views", "app_views_info.log", level=logging.INFO
)
app_views_debug_logger = setup_logger(
    "app_views", "app_views_debug.log", level=logging.DEBUG
)
app_views_error_logger = setup_logger(
    "app_views", "app_views_debug.log", level=logging.ERROR
)
app_auth_info_logger = setup_logger("app_auth", "app_auth_info.log", level=logging.INFO)
app_auth_error_logger = setup_logger(
    "app_auth", "app_auth_error.log", level=logging.ERROR
)
