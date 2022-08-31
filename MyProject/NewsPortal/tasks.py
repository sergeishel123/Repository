from django.contrib.auth.models import User
from .models import Usersubscriberscategory,Category,PostCategory
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

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








