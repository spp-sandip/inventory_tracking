from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from inventory.models import Material

class Command(BaseCommand):
    help = 'Set up initial groups and permissions'

    def handle(self, *args, **kwargs):
        departments = ['Tape & Loom', 'FIBC', 'Lamination', 'Coating 1', 'Coating 2', 'Film', 'Fabrication', 'Oil & Liquid']
        roles = ['Production Engineer', 'Quality Engineer', 'Stock Keeper']

        # Create department-specific groups
        for department in departments:
            for role in roles:
                group_name = f"{department} {role}"
                group, created = Group.objects.get_or_create(name=group_name)

                if role == 'Production Engineer':
                    permissions = [
                        Permission.objects.get(codename='add_material'),
                        Permission.objects.get(codename='view_material'),
                        Permission.objects.get(codename='change_material')
                    ]
                elif role == 'Quality Engineer':
                    permissions = [
                        Permission.objects.get(codename='view_material'),
                        Permission.objects.get(codename='change_material')
                    ]
                elif role == 'Stock Keeper':
                    permissions = [
                        Permission.objects.get(codename='add_material'),
                        Permission.objects.get(codename='view_material')
                    ]

                group.permissions.set(permissions)

        # Create general groups
        internal_audit_group, created = Group.objects.get_or_create(name='Internal Audit')
        operations_group, created = Group.objects.get_or_create(name='Operations')
        plant_head_group, created = Group.objects.get_or_create(name='Plant Head')

        # General permissions
        general_permissions = [
            Permission.objects.get(codename='add_material'),
            Permission.objects.get(codename='change_material'),
            Permission.objects.get(codename='view_material'),
            Permission.objects.get(codename='delete_material')
        ]

        internal_audit_group.permissions.set(general_permissions)
        operations_group.permissions.set(general_permissions)
        plant_head_group.permissions.set(general_permissions)

        self.stdout.write(self.style.SUCCESS('Successfully set up groups and permissions'))
