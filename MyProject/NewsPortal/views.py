from .forms import PostForm
from .models import Post,PostCategory,Category,Usersubscriberscategory,Author
import datetime
from django.views.generic import ListView,DetailView,CreateView,UpdateView,DeleteView,TemplateView,View
from .filters import NewsFilter
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin,PermissionRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.shortcuts import redirect,render,reverse
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.http import HttpResponse


# РАБОТА С ОТПРАВКОЙ ПИСЕМ НА ПОЧТУ НАХОДИТЬСЯ В POSTCREATE в ФУНКЦИИ POST
class PostsList(LoginRequiredMixin,ListView):

    model = Post

    ordering = 'time_in'

    template_name = 'post_list.html'

    context_object_name = 'posts'

    paginate_by = 2



    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['time_now'] = datetime.datetime.utcnow()
        context['is_not_author'] = not (self.request.user.groups.filter(name = 'authors').exists())
        return context



class PostDetail(DetailView):

    model = Post

    template_name = 'post_detail.html'

    context_object_name = 'post'



class PostSearch(ListView):

    model = Post

    template_name = 'post_search.html'

    context_object_name = 'posts'



    def get_queryset(self):

        queryset = super().get_queryset()

        self.filterset = NewsFilter(self.request.GET,queryset)

        return self.filterset.qs

    def get_context_data(self):

        context = super().get_context_data()

        context['filterset'] = self.filterset

        return context


class PostCreate(LoginRequiredMixin,PermissionRequiredMixin,CreateView):
    form_class = PostForm
    model = Post
    template_name = 'post_edit.html'
    permission_required = ('NewsPortal.add_post')


    def form_valid(self, form):
        post = form.save(commit=False)
        value = super().form_valid(form).url
        MASSIV = value.split('/')
        post.type = MASSIV[1]
        #########

        return super().form_valid(form)

    def post(self, request, *args, **kwargs):
        post = self.request.POST

        auth_user, text, heading = request.user.id, post['text'], post['heading']

        #ЛОВИМ ИНСТАНС КЛАССА
        New = Post(author_post=Author.objects.get(user = auth_user), text=text, heading=heading,)

        count = 0
        # ПРОВЕРКА, ЧТО У ПОЛЬЗОВАТЕЛЯ НЕ БОЛЕЕ 3 СТАТЕЙ НА СЕГОДНЯШНИЙ ДЕНЬ
        for i in Post.objects.filter(author_post = Author.objects.get(user = auth_user)):
            now_time = datetime.datetime.today()
            i_time = i.time_in
            #СВЕРЯЕМ ДЕНЬ , МЕСЯЦ, ГОД ПУБЛИКАЦИИ С СЕГОДНЯШНЕМ
            if now_time.day == i_time.day and now_time.day == i_time.day and now_time.year == i_time.year:
                count += 1
            print(count)
        if count < 3:
            New.save()
        else:
            return HttpResponse('ВЫ НЕ МОЖЕТЕ ПУБЛИКОВАТЬ БОЛЕЕ ТРЁХ НОВОСТЕЙ В ДЕНЬ')

        id = Post.objects.order_by('-id')[1].id

        name = post['Category']
        Categor = Category.objects.get(name=name)


        #ОТПРАВКА ПИСЬМА ВСЕМ ПОЛЬЗОВАТЕЛЯМ, КОТОРЫЕ ПОДПИСАНЫ НА ИЗМЕНЕНИЯ В КАКОЙ-ТО КАТЕГОРИИ
        for i in Categor.usersubscriberscategory_set.all():
            html_content = render_to_string(
                'make_post.html',
                {
                    'New': New,
                    'User': i.user
                }
            )
            user = i.user

            msg = EmailMultiAlternatives(
                subject=f'{New.heading}',
                body=New.text,
                from_email='sergeiazharkov@yandex.ru',
                to=[user.email]
            )

            msg.attach_alternative(html_content, 'text/html')

            msg.send(user.email)

        #ВОЗВРАЩАЕМ НА СТРАНИЦУ СОЗДАННОЙ НОВОСТИ
        return redirect(New.get_absolute_url())









class PostUpdate(PermissionRequiredMixin,LoginRequiredMixin,UpdateView):
    form_class = PostForm
    model = Post
    template_name = 'post_edit.html'
    permission_required = ('NewsPortal.change_post')


class PostDelete(PermissionRequiredMixin,LoginRequiredMixin,DeleteView):
    model = Post
    template_name = 'post_delete.html'
    success_url = reverse_lazy('post_list')
    permission_required = ('NewsPortal._post')


class Error(TemplateView):
    template_name = 'flatpages/error.html'


@login_required
def become_an_author(request):
    user = request.user
    author_group = Group.objects.get(name = 'authors')
    if not request.user.groups.filter(name = 'authors').exists():
        author_group.user_set.add(user)
    return redirect('/')


class CategoryView(ListView):
    model = Category

    template_name = 'category.html'

    context_object_name = 'categories'

    def post(self,request,*args,**kwargs):
        category_id = request.POST['category_id']
        print(category_id)
        user_id = request.user.id
        flag = True
        if Usersubscriberscategory.objects.filter(category=category_id, user=self.request.user).exists():
            flag = False
        if  flag:
            User_subscribers_Category_obj = Usersubscriberscategory(category_id = category_id,
                                                                  user_id = user_id)
            User_subscribers_Category_obj.save()
        else:
            return HttpResponse('Вы уже подписаны на эту категорию!'.upper())

        return redirect('/news')



