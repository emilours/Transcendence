from django.apps import AppConfig

class AuthentificationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'authentification'

    def ready(self):
        from frontend.models import CustomUser
        print(f"RREEEEEEADDDDDDYYYYY")
        users = CustomUser.objects.all()
        if users is None:
            print(f"users is None in ready()")
            return
        for user in users:
            user.active_sessions = 0
        # CustomUser.objects.update(active_sessions=0)