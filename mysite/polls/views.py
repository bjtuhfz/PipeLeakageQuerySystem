from django.shortcuts import render, get_object_or_404, render_to_response
from django.http import HttpResponse, Http404, HttpResponseRedirect
from .models import Tweet
from .models import Choice
from django.utils import timezone
from django.template import loader
from django.core.urlresolvers import reverse
from django.views import generic
import datetime
import json
import random
import sqlite3
import sys

from .models import Message, User

# Import machine learning classifier into current file
# We use SVM mainly because it has the highest accuracy
# We also have Max Entropy and Naive Bayes algorithm
from polls.classify_tweets import SVMDemo, load_classifier

# Get live tweets from Twitter Stream API
from polls.crawl_tweet import get_tweet_iterator

# Query historical tweets from SQLite database file and insert them into current Django's SQLite database
from polls.insert_tweet_sqlite3 import query_tweet, get_sql


# Create your views here.
# def index(request):
#     # Insert a record
#     # q = Question.objects.filter(question_text__startswith='What is wrong')
#     # q.delete()
#     # q = Question(question_text="What is wrong?", pub_date=timezone.now())
#     # q.save()
#     latest_question_list = Question.objects.order_by('-pub_date')[:5]
#     # output = '<br> '.join([q.question_text for q in latest_question_list])
#     # return HttpResponse(output)
#
#     # return HttpResponse("Hello, world. You are at the polls index.")
#
#     # Option 1
#     template = loader.get_template('polls/index.html')
#     # Option 2
#     context = {
#         'latest_question_list': latest_question_list,
#     }
#     # 1
#     # return HttpResponse(template.render(context, request))
#     # 2
#     return render(request, 'polls/index.html', context)
#
#
# def detail(request, question_id):
#     # try:
#     #     question = Question.objects.get(pk=question_id)
#     #     # return HttpResponse("You are looking for a question %s" % question_id)
#     # except Question.DoesNotExist:
#     #     raise Http404("Question does not exist")
#
#     # Shortcut
#     question = get_object_or_404(Question, pk=question_id)
#     return render(request, 'polls/detail.html', {'question': question})
#
#
# def results(request, question_id):
#     # response = "You are looking at the results of question %s" % question_id
#     # return HttpResponse(response % question_id)
#     question = get_object_or_404(Question, pk=question_id)
#     return render(request, 'polls/results.html', {'question': question})


def create_choices():
    tweet = create_tweet('This is a test tweet at MC.', timezone.now(), location='MC', label='Negative')
    tweet.save()
    tweet.choice_set.create(choice_text="No, there isn't", votes=0)
    tweet.choice_set.create(choice_text="I'm not sure", votes=0)
    choice = tweet.choice_set.create(choice_text="Yes, I agree", votes=1)
    choice.save()


def create_tweet(tweet_text, pub_date, location, label):
    return Tweet(tweet_text=tweet_text, pub_date=pub_date, location=location, label=label)


def clear_all_tweet():
    print('Deleting all tweets...')
    tweet = Tweet.objects.all()
    tweet.delete()


def create_sample_tweets():
    num_tweets = 50
    for i in range(num_tweets):
        if i % 2:
            location = 'MC'
        else:
            location = 'LA'
        if i % 10 < 3:
            label = 'Positive'
            tweet_text = (i + 1) * chr(97 + i % 26) + ": leaks at " + location
        else:
            label = 'Negative'
            tweet_text = (i + 1) * chr(97 + i % 26) + ": no leaks at " + location

        pub_date = timezone.now() - datetime.timedelta(days=150-i)
        # pub_date = pub_date.strftime('%Y%m%d')
        # print(pub_date)
        tweet = create_tweet(tweet_text, pub_date, location, label)
        tweet.save()
        tweet.choice_set.create(choice_text="No, there isn't", votes=0)
        tweet.choice_set.create(choice_text="I'm not sure", votes=0)
        choice = tweet.choice_set.create(choice_text="Yes, I agree", votes=1)
        choice.save()
        i += 1


def delete_sample_tweets():
    tweet = Tweet.objects.filter(tweet_text__endswith=' leaks at LA')
    tweet.delete()
    tweet = Tweet.objects.filter(tweet_text__endswith=' leaks at MC')
    tweet.delete()


def str_to_datetime(s):
    return datetime.strptime(s + str(random.randint(1, 28)), "%Y%m%d")


def load_historical_tweet():
    print('Loading historical tweets...')
    from datetime import datetime

    db_name = 'test2.db'
    import os
    cur_dir = os.path.dirname(__file__)
    db_name = os.path.join(cur_dir, db_name)
    conn = None  # connector object
    try:
        print('Connecting to DATABASE %s...' % db_name)
        conn = sqlite3.connect(db_name)
        conn.text_factory = str
    except sqlite3.OperationalError as e:
        print(e)
        print('Connecting to DATABASE %s failed...' % db_name)

    sql = get_sql(table_name='tweets', time_range='', location='', label='', count_flag=False)
    rows = query_tweet(conn, sql)   # json format
    try:
        num_tweet = len(rows)
        print("num_tweet = %d" % num_tweet)
        for i in range(num_tweet):
            pub_date = datetime.strptime(rows[i][1] + str(random.randint(1, 28)), "%Y%m%d")
            tweet_text = rows[i][3]
            if sys.version_info[0] == 2:
                tweet_text = unicode(tweet_text, errors='ignore')
            elif sys.version_info[0] == 3:
                tweet_text = str(tweet_text, errors='ignore')
            # print type(tweet_text)
            tweet = create_tweet(tweet_text=tweet_text, pub_date=pub_date, location=rows[i][2], label=rows[i][4])
            tweet.save()
            tweet.choice_set.create(choice_text="No, there isn't", votes=0)
            tweet.choice_set.create(choice_text="I'm not sure", votes=0)
            choice = tweet.choice_set.create(choice_text="Yes, I agree", votes=1)
            choice.save()
            i += 1
            if i % 1000 == 0:
                print('%d historical tweets loaded...' % i)
    except TypeError as e:
        print(e)
        # exit()
    conn.close()
    print('Disconnecting to DATABASE %s...' % db_name)


# Classify tweet with SVM classifier trained from 3 months' historical twitter data set
def label_tweet(tweet):
    return SVMDemo(tweet, load_classifier('SVM'))


# Naive way to filter relevant tweets
def label_tweet_naive(tweet):
    word_list = ['leak', 'broken', 'break', 'crack', 'flood']
    if tweet.find('water') > 0 and tweet.find('pipe') > 0:
        for w in word_list:
            if tweet.find(w) > 0:
                return 'Positive'
    return 'Negative'


def load_live_tweet():
    from datetime import datetime
    print("Loading live tweets...")
    # locations = "-74,40,-73,41" # New York
    # locations = "-118.5,33.5,-118,34.5"  # Los Angeles
    locations = "-77.7405, 38.6547, -76.7405, 39.6547"  # Montgomery County, MD
    iterator = get_tweet_iterator('water', locations)
    location = 'MC'

    num_tweet = 20     # Load 20 live tweets each time by default
    i = 0
    for tweet in iterator:
        i += 1
        # json.dumps(tweet, indent=4)
        if 'text' in tweet:
            pub_date = datetime.strptime(str(tweet['created_at']), '%a %b %d %H:%M:%S +0000 %Y');
            # print '(%d)' % tweet['id'], pub_date, tweet['text']
            label = label_tweet(tweet['text'])
            t = create_tweet(tweet['text'], pub_date, location, label)
            t.save()
            t.choice_set.create(choice_text="No, there isn't", votes=0)
            t.choice_set.create(choice_text="I'm not sure", votes=0)
            choice = t.choice_set.create(choice_text="Yes, I agree", votes=1)
            choice.save()
            i += 1
        if i > num_tweet:
            break


def alter_lowercase_label():
    tweets = Tweet.objects.filter(label__startswith='n')
    for t in tweets:
        t.label = 'Negative'
        t.save(update_fields=['label'])
    tweets = Tweet.objects.filter(label__startswith='p')
    for t in tweets:
        t.label = 'Positive'
        t.save(update_fields=['label'])


def create_users():
    num_user = 26
    for i in range(num_user):
        c = chr(97 + i % 26)
        user = User(username=c, password=8*c)
        user.save()


def create_user_report():
    # Generate message
    num_msg = 20
    for i in range(num_msg):
        c = chr(97 + i % 26)
        user = User.objects.get(username=c)
        content = "I saw water pipe broken at 2nd floor of DBH @" + c
        location = 'LA'
        pub_date = timezone.now()
        msg = Message(user=user, content=content, location=location, pub_date=pub_date)
        msg.save()


def clear_user_report():
    msg = Message.objects.all()
    msg.delete()


def update_msg_status():
    msgs = Message.objects.all()
    for m in msgs:
        if m.status == 'Unlabelled':
            m.status = label_tweet(m.content)
        if m.status == 'positive':
            m.status = 'Positive'
        elif m.status == 'negative':
            m.status = 'Negative'
        m.save(update_fields=['status'])
    tweets = Tweet.objects.filter(label='Unlabelled')
    for t in tweets:
        t.label = label_tweet(t.tweet_text)
        t.save(update_fields=['label'])



def add_choices_to_msg():
    msgs = Message.objects.all()
    for m in msgs:
        m.choice_set.create(choice_text="No, there isn't", votes=0)
        m.choice_set.create(choice_text="I'm not sure", votes=0)
        choice = m.choice_set.create(choice_text="Yes, I agree", votes=1)
        choice.save()


class IndexView(generic.ListView):
    template_name = 'polls/index.html'
    # context_object_name = 'tweet_list'

    # Add msg_list as return
    context_object_name = 'data_list'

    def get_queryset(self):
        """Return the most recent 20 tweets by default"""
        num_recent = 20
        # clear_all_tweet()

        # create_choices()

        # create_sample_tweets()

        # delete_sample_tweets()

        load_live_tweet()

        # Created..
        # create_users()

        # clear_user_report()
        # create_user_report()

        update_msg_status()

        # Choices already added
        # add_choices_to_msg()

        # Historical data set has been loaded, around 10k selected tweets from 01/2016 to 03/2016
        # load_historical_tweet()
        # alter_lowercase_label()

        return {
            'tweet_list':Tweet.objects.filter(pub_date__lte=timezone.now()).order_by('-pub_date')[:num_recent],
            'msg_list': Message.objects.all().order_by('-pub_date')[:num_recent],
        }


class DetailView(generic.DetailView):
    model = Tweet
    template_name = 'polls/detail.html'

    def get_queryset(self):
        """
        Excludes any tweets that aren't published yet
        :return:
        """
        return Tweet.objects.filter(pub_date__lte=timezone.now())


class ResultsView(generic.DetailView):
    model = Tweet
    template_name = 'polls/results.html'


# class QueryTweetsView(generic.ListView):
#     model = Tweet
#     template_name = 'polls/query.html'


def query(request):
    try:
        print('request.GET: ', request.GET)
        tweet = Tweet.objects.all()
        if request.GET['location'] != '':
            tweet = tweet.filter(location__exact=request.GET['location'])
        if request.GET['pub_date'] != '':
            m = int(request.GET['pub_date'][4:])
            # print 'month = %d' % m
            tweet = tweet.filter(pub_date__month=m)
        if request.GET['label'] != 'All':
            tweet = tweet.filter(label__exact=request.GET['label'])
        # if request.GET['count_flag'] == 'True':
        #     tweet_count = tweet.count()

    except (KeyError, Tweet.DoesNotExist):
        return render(request, 'polls/index.html',
                      {'info_msg': 'No relevant entries found!'})
    else:
        return render(request, 'polls/query.html', {
            'tweet_list': tweet,
            'count_flag': request.GET['count_flag'],
            'request_GET': request.GET,
        })


def vote(request, tweet_id):
    # return HttpResponse("You are voting for tweet %s" % tweet_id)
    tweet = get_object_or_404(Tweet, pk=tweet_id)
    try:
        selected_choice = tweet.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        # Redisplay tweet
        return render(request, 'polls/detail.html',
                  {'tweet': tweet,
                   'error_message': 'You didn\'t select any option',})
    else:
        selected_choice.votes += 1
        selected_choice.save()
        return HttpResponseRedirect(reverse('polls:results', args=(tweet.id,)))


# Wei Wang: send message to database

# For test use only
# # for test the app register
# def reg(request):
#     return render_to_response('regforapp.html')
#
# # for test the app login
# def logg(request):
#     return render_to_response('loginforapp.html')
#
# # for test the app login
# def content(request):
#     return render_to_response('contentforapp.html')

# for the app use
def regforapp(request):
    username = request.POST['username']
    password = request.POST['password']
    user = User.objects.filter(username__exact=username)
    if user:
        return HttpResponse(status='300')
    else:
        newuser = User()
        newuser.username = username
        newuser.password = password
        newuser.save()
        return HttpResponse(status='200')

#for the app use
def loginforapp(request):
    # print request

    username = request.POST['username']
    password = request.POST['password']
    user = User.objects.filter(username__exact=username, password__exact=password)
    if user:
        request.session['username'] = username
        return HttpResponse(status="200")
    else:
        return HttpResponse(status="300")

#for the app use
def contentforapp(request):
    from datetime import datetime
    print('Content for app', request)
    username = request.session.get('username', 'anybody')
    content = request.POST['content']
    location = request.POST['location']
    user = User.objects.get(username__exact=username)
    message = Message(user=user, content=content, location=location, pub_date=datetime.now())
    message.save()
    # Add msg to Tweet database
    msg_to_tweet = Tweet(tweet_text=message.content, pub_date=message.pub_date, location=message.location, label=message.status)
    msg_to_tweet.save()
    return HttpResponse(status='200')
