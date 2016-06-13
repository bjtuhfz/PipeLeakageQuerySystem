# -*- coding: utf-8 -*-
"""
Created on Thu Apr 21 15:47:37 2016

@author: huanc

Classify tweets

Models used: Naive Bayes, Max Entropy, SVM

"""

try:
    import nltk
    from nltk.corpus import stopwords
    from nltk.metrics import *
except ImportError or ValueError as e:
    print(e)

try:
    import sklearn
    from sklearn import svm
except ImportError as e:
    print(e)

import re
import pickle


stopwords_set = []
stopwords_set.extend(stopwords.words('english'))
for i in range(len(stopwords_set)):
    stopwords_set[i] = str(stopwords_set[i])
stopwords_set.append('URL')
stopwords_set.append('AT_USER')

# num_stop_words = len(stopwords_set)
# for i in range(num_stop_words):
#     print stopwords_set[i],
#     i += 1
#     if i % 10 == 0:
#         print


# Utility Function implementations
def process_tweet(tweet):
    tweet = tweet.lower()
    # convert www.* or https?://* to URL
    tweet = re.sub('((www\.[^\s]+)|(https?://[^\s]+))', 'URL', tweet)
    # convert @username to AT_USER
    tweet = re.sub('@[^\s]', 'AT_USER', tweet)
    # remove additional white spaces
    tweet = re.sub('[\s]+', ' ', tweet)
    # remove #word with word
    tweet = re.sub(r'#([^\s]+)', r'\1', tweet)
    # trim
    tweet = tweet.strip('\'"')
    return tweet


# remove 2 or more repetitions of chars
def replace_twoOrMore(s):
    pattern = re.compile(r'(.)\1{1,}', re.DOTALL)
    return pattern.sub(r'\1\1', s)


def get_feature_vector(tweet):
    featureVector = []
    tweet = process_tweet(tweet)
    words = tweet.split()   # split tweet into words
    for w in words:
        # replace two or more with two occurrences
        w = replace_twoOrMore(w)
        # strip punctuation
        w = w.strip('\'"?,.!')
        # check if the word stats with an alphabet
        val = re.search(r"^[a-zA-Z][a-zA-Z0-9]*$", w)
        # ignore stop word
        if w in stopwords_set or val is None or len(w) <= 3:
            continue
        else:
            featureVector.append(w.lower())
    return featureVector


def getAllWords(tweets):
    all_words = []
    for (words, label) in tweets:
        all_words.extend(words)
    return all_words


def get_distinct_features(wordlist):
    wordlist = nltk.FreqDist(wordlist)
    return wordlist.keys()


def extract_features(document):
    document_words = set(document)  # remove duplicate features
    features = {}
    for word in word_features:
        features['contains(%s)' % word] = (word in document_words)
    return features     # True/False list


def load_labelled_tweets(filename):
    tweets = []
    try:
        f = open(filename, 'r')
        lineCnt = 0
        try:
            line = f.readline()
        except UnicodeDecodeError as e:
            print(e)
            line = None
        while line:
            comma_pos = line.rfind(',')
            if comma_pos >= 0:
                # tweet = process_tweet(line[: comma_pos])
                tweet = line[: comma_pos]
                label = line[comma_pos + 1:] # rm '\n'
                label = label.rstrip('\r\n')
                tweets.append((tweet, label))
                lineCnt += 1
            line = f.readline()
        # print("Loaded %s tweets from %s" % (lineCnt, filename))
#        lines = f.read().splitlines()
#        print len(lines), 'tweets in ', filename
#        # parse lines
#        for line in lines:
#            comma_pos = line.rfind(',')
#            if comma_pos >= 0:
#                tweet = process_tweet(line[: comma_pos])
#                label = line[comma_pos + 1:]
#                tweets.append((tweet, label))
        f.close()
#        print tweets
    except IOError:
        print('Error! Cannot load file ', filename)
    return tweets


# @raw_tweets: tuples of (tweet, label)
# @return list of (features, label)
def convert_tweets_to_words(raw_tweets):
    tweets = []
    for (tweet, label) in raw_tweets:
        features = get_feature_vector(tweet)
#        if len(features) > 1:
        tweets.append((features, label))
#    print tweets
    return tweets


def show_performance(labels_GT, labels_result):
    a = accuracy(labels_GT, labels_result)
    r = recall(set(labels_GT), set(labels_result))
    f = f_measure(set(labels_GT), set(labels_result))
    print('Accuracy:', a, ', Recall:', r, ', F-measure:', f)


def get_SVM_featureVector_labels(tweets, featureList):
    sortedFeatures = sorted(featureList)
    map = {}
    feature_vector = []
    labels = []
    for t in tweets:
        label = 0
        map = {}
        for w in sortedFeatures:
            map[w] = 0

        tweet_words = t[0]
        tweet_opinion = t[1]
        # Fill the map
        for word in tweet_words:
            word = replace_twoOrMore(word)
            word = word.strip('\'"?,.')
            if word in map:
                map[word] = 1
        values = map.values()
        feature_vector.append(values)
        if (tweet_opinion == 'positive'):
            label = 0
        elif tweet_opinion == 'negative':
            label = 1
        elif tweet_opinion == 'neutral':
            label = 2
        labels.append(label)
    return {'feature_vector': feature_vector, 'labels': labels}


def get_labels_GT(tweets):
    labels_GT = []
    for (t, gt) in tweets:
        labels_GT.append(gt)
    return labels_GT


def save_classifier(fname, classifier):
    fname = 'classifier_' + fname + '.pickle'
    try:
        f = open(fname, 'w')
        pickle.dump(classifier, f)
        f.close()
    except IOError:
        print('save classifier failed!')


def load_classifier(fname):
    import os
    cur_dir = os.path.dirname(__file__)
    fname = 'classifier_' + fname + '.pickle'
    fname = os.path.join(cur_dir, fname)
    try:
        f = open(fname, 'r')
        classifier = pickle.load(f)
        f.close()
        return classifier
    except IOError:
        return None


def test_hello(msg):
    print("hello" + msg)


'''
pos_tweets = [('I love this car', 'positive'),
              ('This view is amazing', 'positive'),
            ('I feel great this morning', 'positive'),
            ('I am so excited about the concert', 'positive'),
            ('He is my best friend', 'positive')]
'''

# Text Mining Starts here
# Test in Django
import os
cur_dir = os.path.dirname(__file__)
train_file = os.path.join(cur_dir, 'data/joinedTrainedTweets.txt')
test_file = os.path.join(cur_dir, 'data/20160106-20160131_US_labelled.txt')

# Original values
# dataDir = 'data/[pattern]water_pipe/' # 05/13
# dataDir_US = 'data/[pattern]water_pipe_US/' # 05/12

#dataDir_US = 'data/[pattern]water_pipe_All/'

#train_file = 'twitter_train_example.txt'
#train_file = dataDir + 'joinedLabelledTweetsData.txt'
#test_file = dataDir_US + 'joinedLabelledTweetsData.txt'

# Original
# train_file = dataDir + 'joinedTrainedTweets.txt'
# test_file = dataDir_US + '20160106-20160131_US_labelled.txt'

# test each month in US respectively
#test_file = dataDir_US + '20160302-20160228_US_labelled.txt'
#test_file = dataDir_US + '20160301-20160330_US_labelled.txt'

# Test by location and month
#test_file = dataDir_US + '20160301-20160330_All_labelled.txt'
#test_file = dataDir + '20160106-20160131_MC_labelled.txt'

#test_file = 'twitter_test_example.txt'
#test_file_unlabeled = 'twitter_test_unlabeled.txt'
#test_tweets = load_tweets_wo_labels(test_file)
raw_train_tweets = load_labelled_tweets(train_file)
raw_test_tweets = load_labelled_tweets(test_file)

## Tokenization: sentence to tokens
## Stemming (Optional)
## Remove stop words and punctuations
## Indexing

# (words, label) tuples
train_tweets = convert_tweets_to_words(raw_train_tweets)
del raw_train_tweets # release memory
test_tweets = convert_tweets_to_words(raw_test_tweets)
del raw_test_tweets

# extract features
word_features = get_distinct_features(getAllWords(train_tweets))

trainning_set = nltk.classify.apply_features(extract_features, train_tweets)

labels_GT = get_labels_GT(test_tweets) # Ground truth labels


def show_numOfPositive(labels):
    posCnt = 0
    for i in range(len(labels)):
        if labels[i] == 'positive':
            posCnt += 1
    print('%d/%d' % (posCnt, len(labels_GT) - posCnt))


def classifyByNB():
    print("===== Naive Bayes =====")
#    classifier = nltk.NaiveBayesClassifier.train(trainning_set)

    fname = 'NB'
#    save_classifier(fname, classifier)
    classifier = load_classifier(fname)

    labels_result = []
    for (t, gt) in test_tweets:
        label = classifier.classify(extract_features(t))
        labels_result.append(label)

    show_numOfPositive(labels_result)
    show_performance(labels_GT, labels_result)
#    classifier.show_most_informative_features(10)


def classifyByMaxEnt():
    print('===== Max Entropy ===== ')
#    classifier = nltk.classify.maxent.MaxentClassifier.train(trainning_set, \
#        'GIS', trace=3, encoding=None, labels=None, \
#    #    sparse=True,
#        gaussian_prior_sigma=0, \
#        max_iter = 10)

    fname = 'MaxEnt'
#    save_classifier(fname, classifier)
    classifier = load_classifier(fname)

    labels_result = []
    for (t, gt) in test_tweets:
        label = classifier.classify(extract_features(t))
        labels_result.append(label)

    show_numOfPositive(labels_result)
    show_performance(labels_GT, labels_result)
    classifier.show_most_informative_features(10)


def classifyBySVM():
    print('===== SVM =====')
    result = get_SVM_featureVector_labels(train_tweets, word_features)
#    classifier = svm.SVC()
#    classifier = svm.SVC(C=1000000,kernel='linear')

#    classifier = svm.LinearSVC(penalty='l1', loss='squared_hinge', dual=False, C=10)
#    classifier.fit(result['feature_vector'], result['labels'])

    fname = 'SVM'
#    save_classifier(fname, classifier)
    classifier = load_classifier(fname)

    testSet = get_SVM_featureVector_labels(test_tweets, word_features)
    labels_result = classifier.predict(testSet['feature_vector'])
    show_performance(testSet['labels'], labels_result)
    decisionFuncs = classifier.decision_function(testSet['feature_vector'])
    print(len(labels_result) - sum(labels_result), '/', sum(labels_result))
#    print '# of positive:',
#    print '# of negative:',

#    print labels_result
#    print decisionFuncs
#    fname = 'outputPosTweets.txt'
#    fw = open(fname, 'w')
#    for i in range(len(labels_result)):
#        if labels_result[i] == 0:
#            fw.write(test_tweets[i][0])
#    fw.close()


def SVMDemo(t_input, classifier):
    # print '***** SVM *****'
    t_raw = [(t_input, 'Positive')]
    t = convert_tweets_to_words(t_raw)
#    print t
    test = get_SVM_featureVector_labels(t, word_features)
#    print test, len(test['feature_vector'][0]), len(word_features)
    l = classifier.predict(test['feature_vector'])
    label = ''
    if sum(test['feature_vector'][0]) > 0:
        if l[0] == 0:
            label = 'Positive'
        elif l[0] == 1:
            label = 'Negative'
    else:
        label = 'Neutral'
#    print t_input, ':', label
#     print label
    decisionFunc = classifier.decision_function(test['feature_vector'])
    return label

def NaiveBayesDemo(t_input, classifier):
    # print '***** Naive Bayes *****'
    t_raw = [(t_input, 'positive')]
    t = convert_tweets_to_words(t_raw)
    for (tweet, gt) in t:
        if len(tweet) > 0:
            label = classifier.classify(extract_features(tweet))
        else:
            label = 'neutral'
#        print t_input, ':', label
        print(label)
    return label


def MaxEntDemo(t_input, classifier):
    # print '***** Max Entropy *****'
    t_raw = [(t_input, 'positive')]
    t = convert_tweets_to_words(t_raw)
    for (tweet, gt) in t:
        if len(tweet) > 0:
            label = classifier.classify(extract_features(tweet))
        else:
            label = 'neutral'
#        print t_input, ':', label
        print(label)
    return label


def DemoATweet():
    t_input = 'I saw the water pipe crack at the back yard of my house https://tinyurl.5bcc.com'
#    t_input = 'There is no water in the tank of my car, maybe the pipe is not working...'

    t_raw = [(t_input, 'positive')]
    t = convert_tweets_to_words(t_raw)
    print('Input tweet:', t_input)
    print('Processed tweet:', t)
    NaiveBayesDemo(t_input, load_classifier('NB'))

    MaxEntDemo(t_input, load_classifier('MaxEnt'))

    SVMDemo(t_input, load_classifier('SVM'))

# DemoATweet()

# print '===== Ground Truth ====='
# show_numOfPositive(labels_GT)
#------------#------------#------------#------------

# classifyByNB()
# classifyByMaxEnt()
# classifyBySVM()

#------------#------------#------------#------------
