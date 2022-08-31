import logging

from django.conf import settings

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from django.core.management.base import BaseCommand
from django_apscheduler.jobstores import DjangoJobStore
from django_apscheduler.models import DjangoJobExecution


from NewsPortal.models import Usersubscriberscategory, Category, PostCategory
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

from django.core.mail import send_mail
logger = logging.getLogger(__name__)


# наша задача по выводу текста на экран
def my_job():
    #  Your job processing logic here...
    print('GGGGGGGGGGGGGGGGGGGGGGGGGGGGGG')
    def send_mail():
        user_massiv = []
        for category in Category.objects.all():
            for user_category in category.usersubscriberscategory_set.all():
                user_massiv.append(user_category.user)
        for user in user_massiv:
            category_user_obj = Usersubscriberscategory.objects.filter(user = user)
            for i in category_user_obj:
                if PostCategory.objects.filter(category=i.category).exists():
                    html_content = render_to_string(
                        'categories_every_week.html',
                        {
                            'Category': i.category,
                            'User': user,
                            'Posts': [k.post for k in PostCategory.objects.filter(category = i.category)]
                        }
                    )

                    msg = EmailMultiAlternatives(
                        subject = 'Обновления в категории',
                        body = '',
                        from_email = 'sergeiazharkov@yandex.ru',
                        to = [user.email]
                    )
                    msg.attach_alternative(html_content,'text/html')

                    msg.send(user.email)
        send_mail()


# функция, которая будет удалять неактуальные задачи
def delete_old_job_executions(max_age=604_800):
    """This job deletes all apscheduler job executions older than `max_age` from the database."""
    DjangoJobExecution.objects.delete_old_job_executions(max_age)


class Command(BaseCommand):
    help = "Runs apscheduler."

    def handle(self, *args, **options):
        scheduler = BlockingScheduler(timezone=settings.TIME_ZONE)
        scheduler.add_jobstore(DjangoJobStore(), "default")

        # добавляем работу нашему задачнику
        scheduler.add_job(
            my_job,
            trigger=CronTrigger(minute="*/1"),
            # То же, что и интервал, но задача тригера таким образом более понятна django
            id="my_job",  # уникальный айди
            max_instances=1,
            replace_existing=True,
        )
        logger.info("Added job 'my_job'.")

        scheduler.add_job(
            delete_old_job_executions,
            trigger=CronTrigger(
                day_of_week="mon", hour="00", minute="00"
            ),
            # Каждую неделю будут удаляться старые задачи, которые либо не удалось выполнить, либо уже выполнять не надо.
            id="delete_old_job_executions",
            max_instances=1,
            replace_existing=True,
        )
        logger.info(
            "Added weekly job: 'delete_old_job_executions'."
        )

        try:
            logger.info("Starting scheduler...")
            scheduler.start()
        except KeyboardInterrupt:
            logger.info("Stopping scheduler...")
            scheduler.shutdown()
            logger.info("Scheduler shut down successfully!")