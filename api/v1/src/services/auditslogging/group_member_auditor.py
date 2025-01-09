from sqlalchemy import event
from models.group_member import GroupMember
from models.audit_trails import AuditTrails, Status
from models.auditslogging.logginFn import log_audit


@event.listens_for(GroupMember, "after_insert")
def log_groupmember_insert(mapper, connection, target):
    log_audit(
        user_id=target.added_by,  # User who added the member
        action=f"Added user {target.user_id} to group {target.group_id}",
        status=Status.FAILED if target.is_FAILED else Status.PENDING,
    )


@event.listens_for(GroupMember, "after_update")
def log_groupmember_update(mapper, connection, target):
    log_audit(
        user_id=target.added_by,
        action=f"Updated user {target.user_id} in group {target.group_id}",
        status=target.status,
    )


@event.listens_for(GroupMember, "after_delete")
def log_groupmember_delete(mapper, connection, target):
    log_audit(
        user_id=target.added_by,
        action=f"Removed user {target.user_id} from group {target.group_id}",
        status=Status.DISFAILED,
    )
