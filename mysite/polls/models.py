from __future__ import unicode_literals
from django.db import models
import datetime
from django.utils import timezone


# Create your models here.
# class Question(models.Model):
#     question_text = models.CharField(max_length=200)
#     pub_date = models.DateTimeField('date published')
#
#     def __str__(self):
#         return self.question_text
#
#     def was_published_recently(self):
#         # return self.pub_date >= timezone.now() - datetime.timedelta(days=1)
#         now = timezone.now()
#         return now - datetime.timedelta(days=1) <= self.pub_date <= now


class Tweet(models.Model):
    tweet_text = models.CharField(max_length=150)
    # pub_date = models.CharField(max_length=15)
    pub_date = models.DateTimeField()
    location = models.CharField(max_length=10)
    label = models.CharField(max_length=10)

    def __str__(self):
        return self.tweet_text

    def was_published_recently(self):
        # return self.pub_date >= timezone.now() - datetime.timedelta(days=1)
        now = timezone.now()
        return now - datetime.timedelta(days=1) <= self.pub_date <= now


class Choice(models.Model):
    tweet = models.ForeignKey(Tweet, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=100)
    votes = models.IntegerField(default=0)

    def __str__(self):
        return self.choice_text

# Wei Wang

class User(models.Model):
    username = models.CharField(max_length=100)
    password = models.CharField(max_length=100)
    def __str__(self):
        return self.username

class Message(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.CharField(max_length=300)
    location = models.CharField(max_length=30,default="")
    pub_date = models.DateTimeField('date published')
    status = models.CharField(max_length=100,default="Unlabelled")
    def __str__(self):
        return self.content
    def was_published_recently(self):
        return self.pub_date >= timezone.now() - datetime.timedelta(days=1)
