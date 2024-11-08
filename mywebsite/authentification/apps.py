from django.apps import AppConfig
from django.core.exceptions import ObjectDoesNotExist
from django.db import connection

class AuthentificationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'authentification'

    def ready(self):
            from frontend.models import CustomUser
            if 'frontend_customuser' in connection.introspection.table_names():
                try:
                    users = CustomUser.objects.all()
                    for user in users:
                        user.active_sessions = 0
                        user.save()
                except Exception as e:
                    print(f"An error occurred: {e}")
