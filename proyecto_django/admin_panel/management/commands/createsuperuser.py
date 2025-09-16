from django.contrib.auth.management.commands import createsuperuser
from admin_panel.models import CustomUser

class Command(createsuperuser.Command):
    def handle(self, *args, **options):
        options['is_admin'] = True  # Agrega este campo automáticamente
        options['is_staff'] = True
        options['is_superuser'] = True
        super().handle(*args, **options)