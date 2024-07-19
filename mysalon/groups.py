# groups.py
from django.contrib.auth.models import Group, Permission

def create_groups():
    normal_user_group, _ = Group.objects.get_or_create(name='Normal User')
    staff_admin_group, _ = Group.objects.get_or_create(name='Staff Admin')
    super_admin_group, _ = Group.objects.get_or_create(name='Super Admin')

    # Assign permissions to groups
    normal_user_permissions = Permission.objects.filter(name__icontains='user')
    staff_admin_permissions = Permission.objects.filter(name__icontains='staff')
    super_admin_permissions = Permission.objects.all()

    normal_user_group.permissions.set(normal_user_permissions)
    staff_admin_group.permissions.set(staff_admin_permissions)
    super_admin_group.permissions.set(super_admin_permissions)
