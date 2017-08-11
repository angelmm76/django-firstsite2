from django.db import models
from django.contrib.auth.models import User
from django.utils.encoding import python_2_unicode_compatible
from django.urls import reverse

@python_2_unicode_compatible  # only if you need to support Python 2
class BlogPost(models.Model):
    blogpost_title = models.CharField(max_length=200)
    blogpost_content = models.TextField(max_length=2000)
    pub_date = models.DateTimeField('date published')
    image = models.ImageField(blank=True, upload_to='blogimages')  # /%Y/%m/%d')
    likes = models.IntegerField(default=0)
    dislikes = models.IntegerField(default=0)
    author = models.ForeignKey(User, related_name='blogposts')
    # author = models.ForeignKey('UserProfile')

    def __str__(self):
        return self.blogpost_title

    def get_absolute_url(self):
        return reverse('blog:detail', args=[str(self.id)])

@python_2_unicode_compatible  # only if you need to support Python 2
class UserProfile(models.Model):
    user = models.OneToOneField(User)
    votes = models.IntegerField(default=0)
    occupation = models.CharField(max_length=50)
    city = models.CharField(max_length=30)
    province = models.CharField(max_length=50)
    sex = models.CharField(max_length=1)

    def __str__(self):
        return self.blogpost_title

@python_2_unicode_compatible  # only if you need to support Python 2
class Comment(models.Model):
    blogpost = models.ForeignKey(BlogPost, related_name='comments')
    # user = models.OneToOneField(User)
    user = models.ForeignKey(User, related_name='comments')
    comment_content = models.TextField(max_length=2000)
    votes = models.IntegerField(default=0)
    created = models.DateTimeField('created')