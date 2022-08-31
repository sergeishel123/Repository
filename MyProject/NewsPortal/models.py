from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from datetime import datetime
class Author(models.Model):
    user = models.OneToOneField(User,on_delete = models.CASCADE)
    user_rating = models.IntegerField(default = 1)
    def name(self):
        self.user_rating = 0
        for i in self.post_set.all():
            self.user_rating += i.rating
            for k in i.comment_set.all():
                self.user_rating += k.rating
        for j in self.user.comment_set.all():
            self.user_rating += j.rating
        self.save()
    @staticmethod
    def best_user():
        user_list = Author.objects.all()
        t = [User.name() for User in user_list]
        user_rating_List = [User.user_rating for User in user_list]
        return (Author.objects.get(user_rating = max(user_rating_List)))

    def __str__(self):
        return f'{self.user.username}'





class Category(models.Model):
    name = models.CharField(max_length = 255,unique = True)

    def func(self):
        for i in self.usersubscriberscategory_set.all():
            print(i)

array = [('N','News'), ('A','Article')]
class Post(models.Model):
    author_post = models.ForeignKey(Author,on_delete = models.CASCADE)
    type = models.CharField(max_length = 1,choices = array)
    time_in = models.DateTimeField(default=datetime.utcnow())
    category_post = models.ManyToManyField(Category,through = 'PostCategory')
    heading = models.CharField(max_length = 255)
    text = models.TextField()
    rating = models.IntegerField(default = 0)

    def like(self):
        self.rating += 1
        self.save()

    def dislike(self):
        self.rating -= 1
        self.save()

    def preview(self):
        return f'{self.text[:124]}...'

    def __str__(self):
        return  f' "{self.text}"'
    @staticmethod
    def best_post():
        Posts_List = [POST.rating for POST in Post.objects.all()]
        return Post.objects.get(rating = max(Posts_List))

    def get_absolute_url(self):
        return reverse('post_detail', args=[str(self.id)])

    def user_category(self):
        for i in self.usersubscriberscategory_set.all():
            print(i)



class PostCategory(models.Model):
    post = models.ForeignKey(Post,on_delete = models.CASCADE)
    category = models.ForeignKey(Category,on_delete = models.CASCADE)


class Comment(models.Model):
    post = models.ForeignKey(Post,on_delete = models.CASCADE)
    user = models.ForeignKey(User,on_delete= models.CASCADE)
    text = models.TextField()
    time_in = models.DateTimeField(auto_now_add = True)
    rating = models.IntegerField(default = 0)

    def like(self):
        self.rating += 1
        self.save()
    def dislike(self):
        self.rating -= 1
        self.save()

class Usersubscriberscategory(models.Model):
    user = models.ForeignKey(User,on_delete = models.CASCADE)
    category = models.ForeignKey(Category,on_delete = models.CASCADE)


from allauth.account.forms import SignupForm
from django.contrib.auth.models import Group


class CommonSignupForm(SignupForm):

    def save(self, request):
        user = super(CommonSignupForm, self).save(request)
        common_group = Group.objects.get(name='common')
        common_group.user_set.add(user)
        return user




# Create your models here.
