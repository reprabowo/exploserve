# main/permissions.py

def can_manage_user(manager, target):
    """
    Returns True if the manager (logged-in user) is allowed to manage the target user.
    Rules:
      - A user can always manage (read/update) their own profile.
      - System Owner can manage all users.
      - System Admin can manage Institution Admins, Researchers, Reviewers, Students, and Technicians.
      - Institutional Admin can only manage users within their own institution whose roles are in
        ['researcher', 'reviewer', 'student', 'technician'].
      - Researchers, Reviewers, Students, and Technicians can only manage their own profile.
    """
    try:
        manager_role = manager.profile.role
        target_role = target.profile.role
    except AttributeError:
        return False

    # Allow self-management.
    if manager == target:
        return True

    # If manager is one of the lower-level roles, they can only manage themselves.
    if manager_role in ["researcher", "reviewer", "student", "technician"]:
        return False

    # System Owner can manage all users.
    if manager_role == "system_owner":
        return True

    # System Admin can manage a broad set of roles.
    if manager_role == "system_admin":
        return target_role in ["institution_admin", "researcher", "reviewer", "student", "technician"]

    # Institutional Admin can only manage users in the same institution with allowed roles.
    if manager_role == "institution_admin":
        allowed_roles = ["researcher", "reviewer", "student", "technician"]
        return (target.profile.institution == manager.profile.institution) and (target_role in allowed_roles)

    return False


def can_delete_user(manager, target):
    """
    Returns True if the manager is allowed to delete the target user.

    Rules:
      - A user cannot delete their own account.
      - System Owner can delete any user.
      - System Admin can delete users except:
        * other System Admins
        * System Owners
      - Institutional Admin can delete users in their own institution
        if the target’s role is one of:
        ['researcher', 'reviewer', 'student', 'technician']
      - Lower roles cannot delete anyone.
    """
    # Prevent self-deletion
    if manager == target:
        return False

    try:
        manager_role = manager.profile.role
        target_role = target.profile.role
    except AttributeError:
        return False

    # System Owner can delete anyone
    if manager_role == "system_owner":
        return True

    # System Admin can delete anyone except other admins
    if manager_role == "system_admin":
        return target_role not in ["system_owner", "system_admin"]

    # Institutional Admin can delete users in their own institution with lower roles
    if manager_role == "institution_admin":
        if target.profile.institution != manager.profile.institution:
            return False
        return target_role in ["researcher", "reviewer", "student", "technician"]

    # Other roles cannot delete
    return False

