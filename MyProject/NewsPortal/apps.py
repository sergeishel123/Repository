from django.apps import AppConfig


class NewsportalConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'NewsPortal'


    def ready(self):
        from .tasks import send_mail
        from .scheduler import Appointment_scheduler
        print('Hello')
        Appointment_scheduler.add_job(
            id = 'mail send',
            func = send_mail,
            trigger = 'interval',
            weeks = 1,
        )
        Appointment_scheduler.start()
