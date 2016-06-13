# insert tweet entries into sqlite database

try:
    import sqlite3
except ImportError as e:
    print(e)
import time
import datetime
# from classify_tweets import load_labelled_tweets


# def create_table(table_name):
#     try:
#         conn.execute('''CREATE TABLE %s
#             (ID INT PRIMARY KEY NOT NULL,
#               Date	VARCHAR(10),
#               Location VARCHAR(10),
#               Tweet VARCHAR(150),
#               Label VARCHAR(10));''' % table_name)
#         conn.commit()
#         print 'Create TABLE %s success!' % table_name
#     except sqlite3.OperationalError as e:
#         print e
#         print 'Create TABLE %s failed!' % table_name
#
#
# def drop_table(table_name):
#     try:
#         conn.execute('''DROP TABLE %s''' % table_name)
#         conn.commit()
#         print 'Drop TABLE %s success!' % table_name
#     except IOError as e:
#         print e
#         print 'Drop TABLE %s failed!' % table_name
#
#
# def insert_tweet_to_DB(table_name, data_dir, time_ranges, locations):
#     cur = conn.cursor()
#
#     rows = cur.execute('SELECT COUNT(*) FROM %s' % table_name)
#     cur_tweet_cnt = rows.fetchall()
#     ID = cur_tweet_cnt[0][0] + 1
#
#     total_tweet_cnt = 0
#     for i in range(len(time_ranges)):
#         for j in range(len(locations)):
#             src_file = data_dir + time_ranges[i] + '_' + locations[j] + '_labelled.txt'
#             raw_tweets = load_labelled_tweets(src_file)
#             # raw_tweets = []
#             # print 'Loading entries from %s' % src_file
#             tweet_cnt = len(raw_tweets)
#             try:
#                 for k in range(0, tweet_cnt):
#                     Date = time_ranges[i][:6]
#                     Location = locations[j]
#                     Tweet = raw_tweets[k][0]
#                     Label = raw_tweets[k][1]
#                     # print type(Tweet), type(Label)
#                     # print (ID, Date, Location, Tweet, Label)
#                     cur.execute("INSERT INTO %s VALUES(?, ?, ?, ?, ?)" % table_name, (ID, Date, Location, Tweet, Label))
#                     conn.commit()
#                     ID += 1
#             except sqlite3.IntegrityError as e:
#                 print e
#                 tmp = 0
#             print '%d tweets inserted into TABLE %s' % (tweet_cnt, table_name)
#             total_tweet_cnt += tweet_cnt
#
#     print '***** %d tweets inserted into TABLE %s *****' % (total_tweet_cnt, table_name)


def get_sql(table_name, time_range, location, label, count_flag):
    sql = ""
    if count_flag:
        sql = "SELECT COUNT(*) from %s" % table_name
    else:
        sql = "SELECT * from %s" % table_name
    has_condition1 = False
    if time_range == '' and location == '' and label == '':
        return sql
    if time_range != '':
        sql += " WHERE Date = \'%s\'" % time_range
        has_condition1 = True
    if location != '':
        if has_condition1:
            sql += " and Location = \'%s\'" % location
        else:
            sql += " WHERE Location = \'%s\'" % location
            has_condition1 = True
    if label != '':
        if has_condition1:
            sql += " and Label = \'%s\'" % label
        else:
            sql += " WHERE Label = \'%s\'" % label
    return sql


def query_tweet(conn, sql):
    try:
        conn.text_factory = str
        cur = conn.cursor()
        rows = cur.execute(sql)
        conn.commit()
        results = []
        for r in rows:
            results.append(r)
            # print type(r)
        return results
    except sqlite3.OperationalError as e:
        print(e)
        return None

# db_name = 'test2.db'
# table_name = 'tweets'

# conn = None     # connector object
# try:
#     print 'Connecting to DATABASE %s...' % db_name
#     conn = sqlite3.connect(db_name)
#     conn.text_factory = str
# except sqlite3.OperationalError as e:
#     print e

# Create schema
# drop_table(table_name)
# create_table(table_name)
#
# time_ranges = ['20160106-20160131', '20160201-20160228', '20160301-20160330']
# data_dir = 'data/[pattern]water_pipe/'
# locations = ['LA', 'MC']
#
# insert_tweet_to_DB(table_name, data_dir, time_ranges, locations)
#
# data_dir = 'data/[pattern]water_pipe_US/'
# locations = ['US']
#
# insert_tweet_to_DB(table_name, data_dir, time_ranges, locations)

# time = '201601'
# loc = 'MC'
# l = 'negative'
# count_flag = True
# sql = get_sql(table_name, time, loc, l, count_flag)
# results = query_tweet(sql)
# print '%d records found!' % len(results)
#
# sql2 = get_sql(table_name, time_range='', location='MC', label='positive', count_flag=False)
# print sql2
# results = query_tweet(sql2)

# i = 0
# for r in results:
#     print r
#     i += 1
#     if i > 10:
#         break

# conn.close()
# print 'Disconnecting to DATABASE %s...' % db_name

# print 'Loading historical tweets...'
# sql = get_sql(table_name='tweets', time_range='', location='', label='', count_flag=False)
# rows = query_tweet(conn, sql) # json format
# num_tweet = len(rows)
# for k in range(20):
#     for i in range(len(rows[0])):
#         print rows[k][i],
#     print