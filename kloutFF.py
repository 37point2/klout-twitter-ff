#!/usr/bin/python

import tweepy
import pyklout
import json
import sys
import types
import time
import math

#get API keys from file

api_keys = json.load(open('api.json', 'r'))

CONSUMER_KEY = api_keys['api']['twitter']['CONSUMER_KEY']
CONSUMER_SECRET = api_keys['api']['twitter']['CONSUMER_SECRET']

ACCESS_TOKEN = api_keys['api']['twitter']['ACCESS_TOKEN']
ACCESS_TOKEN_SECRET = api_keys['api']['twitter']['ACCESS_TOKEN_SECRET']

KLOUTAPIKEY = api_keys['api']['klout']['KEY']

#Klout API ref

Kapi = pyklout.Klout(KLOUTAPIKEY)

#Twitter API ref

auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)

Tapi = tweepy.API(auth)

#set up user class and methods

class User:
  numUsers = 0

  def __init__(self, name, platform):
    self.name = name
    self.platform = platform
#Klout returns 404 occasionally
#if 404, skip user
    try:
      self.id = Kapi.identity(name, platform)['id']
      User.numUsers += 1
    except:
      pass

#needs work
#Possibly can use the number of Influencees or who people influence to determine better algorithm

#  def getInfluences(self):
#    temp = Kapi.influences(self.id)
#    self.myInfluencersCount = temp['myInfluencersCount']
#    self.myInfluenceesCount = temp['myInfluenceesCount']

  def getScore(self):
    temp = Kapi.score(self.id)
    print self.name, temp['score']
    self.score = temp['score']
#Klout doesn't always return scoreDelta
    try:
      self.dayChange = temp['scoreDelta']['dayChange']
      self.monthChange = temp['scoreDelta']['monthChange']
      self.weekChange = temp['scoreDelta']['weekChange']
    except:
      self.dayChange = 0
      self.monthChange = 0
      self.weekChange = 0

  def setScore(self, var):
    self.score = 0
    self.dayChange = 0
    self.monthChange = 0
    self.weekChange = 0

  def getTopics(self):
    temp = Kapi.topics(self.id)
    self.topics = []
    for each in temp:
      self.topics.append(each['name'])

  def setTopics(self):
    self.topics = []

  def setRanking(self, val):
    self.ranking = val

#needs to be cleaned up, copy/pasted from previous utility

#get user timeline
#num = number of tweets to grab

def getTweets(user, num, api):
  tweetsRecv = 0
  tempTweets = []
  pageNum = 1
  numTweets = 0

#check total number of tweets and adjust num total tweets is less than num

  while numTweets == 0:
    try:
      numTweets = api.get_user(user).statuses_count
    except tweepy.error.TweepError as e:
      print e
      if e.response.status == 400:
        resetTime = api.rate_limit_status()['reset_time_in_seconds']
        sleepTimer(resetTime - time.time() + 60)
        continue
      if e.response.status == 503:
        continue
      if e.response.status == 404:
        break

  if num > numTweets:
    num = numTweets

#grab tweets 200 at a time until reached num

  while num > tweetsRecv:

    if (tweetsRecv + 200) > num:
      tempNum = num
      tweetsRecv += 200
    else:
      tempNum = 200
      tweetsRecv += 200

    try:
      [tempTweets.append(each) for each in api.user_timeline(user, page=pageNum, count=tempNum, include_entities='true', include_rts='true')]
      print user + ": " + str(pageNum)
      pageNum += 1
      print str(tweetsRecv) + ", " + str(num) + ", " + str(tempNum)
      print len(tempTweets)
    except tweepy.error.TweepError as e:
      print e
      if isinstance(e, types.NoneType):
        continue
        pageNum -= 1
        tweetsRecv -= 200
      if e.response.status == 400:
        resetTime = api.rate_limit_status()['reset_time_in_seconds']
        sleepTimer(resetTime - time.time() + 60)
        continue
      if e.response.status == 503:
        continue
      if e.response.status == 404:
        break

  return tempTweets

def sleepTimer(seconds):
  while (seconds > 0):
    print seconds/60
    time.sleep(60)
    seconds -= 60

#done copy/paste

def main():

#get user name and number of tweets to grab

  try:
    numberOfFFTweets = int(sys.argv[1])
    userName = Tapi.me().screen_name
    num = 1000
    print userName, num, numberOfFFTweets
  except:
    print "kloutFF.py <Number of #FF Tweets>"
    sys.exit()

#get user's timeline
  print "\nGetting last 1000 Tweets\n"
  userTimeline = []

  [userTimeline.append(each) for each in getTweets(userName, num, Tapi)]

  print len(userTimeline)

#determine the number of interactions for each user in userTimeline
#TODO Implement time cutoff, possibly 1 month

  interactions = {}

#set cutoff to 30 days prior to current time

  timeCutoff = time.time() - (3600*24*30)

  for each in userTimeline:
    if time.mktime(each.created_at.timetuple()) > timeCutoff:
      for x in range(0,len(each.entities['user_mentions'])):
        try:
          interactions[str(each.entities['user_mentions'][x]['screen_name'])] += 1
        except:
          interactions[str(each.entities['user_mentions'][x]['screen_name'])] = 1
    else:
      pass

#remove self from list

  del interactions[userName]

  print len(interactions)

#determine Klout score, topics for each in interactions
  print "\nDetermining Klout score and topics\nThis may take awhile...\n"
  users = []
  platform = 'twitter'

  for each in interactions.keys():
#Klout returns 404 occasionally, haven't looked into why yet
#if 404 return, skip user
    try:
      temp = User(each, platform)
      users.append(temp)
    except:
      pass

  for each in users:
    if hasattr(each, 'id'):
      each.getTopics()
      each.getScore()
    else:
      each.setScore(0)
      each.setTopics()
      print each.name + " has no id attribute.\n"

#ranking for #FF = Interactions * Klout score^2
#later version will factor in interactions with topics to score for #FF
  print "Ranking users\n"
  for each in users:
    val = math.pow(each.score, 2) * interactions[each.name]
    each.setRanking(val)

#    print each.name, each.ranking

#print out and write to file users with ranking from high to low
  print "Sorting users and writing to file"
  f = open('ranking.txt', 'w')
  f.write("Name,Ranking\n")

  users.sort(key = lambda x: x.ranking, reverse=True)

  for each in users:
    f.write(str(each.name) + "," + str(each.ranking) + "\n")
    print each.name, each.ranking

  f.close()

#build tweets, 3 tweets - 140 chars or less
#alphabetize users per Tweet
#possibly use topics to develop tweets in future version
  print "Building Tweets for #FF"
  tweets = []
  y = 0

#append names until next would append would make length of string > 140 chars
  for x in range(0,numberOfFFTweets):
    tweets.append("#FF")
    if len(tweets[x]) < 140:
      flag = True
    if y == len(users):
      tweets.pop(x)
      break
    elif users[y].ranking == 0.0:
      tweets.pop(x)
      break
    while flag:
      if y == len(users):
        flag = False
      elif users[y].ranking == 0.0:
        flag = False
      else:
        if len(tweets[x]) + len(users[y].name) +2 < 140:
          tweets[x] = tweets[x] + " @" + users[y].name
          y += 1
        else:
          flag = False

#alphabetize the names

  for x in range(0, len(tweets)):
    temp = []
    [temp.append(each) for each in tweets[x].split()]
    tweets[x] = (temp[0])
    temp.sort(key=lambda var:var.lower())
    for each in temp[1:]:
      tweets[x] = tweets[x] + " " + each

#post tweets

#uncomment next two lines to post to Twitter
#  for each in tweets:
#    Tapi.update_status(each)

  for each in tweets:
    print each


if __name__ == '__main__':
  main()
