#!/usr/bin/python

import tweepy
import pyklout
import json
import sys
import types
import time

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
    self.id = Kapi.identity(name, platform)['id']
    User.numUsers += 1

    print self.name, self.platform

#needs work

#  def getInfluences(self):
#    temp = Kapi.influences(self.id)
#    self.myInfluencersCount = temp['myInfluencersCount']
#    self.myInfluenceesCount = temp['myInfluenceesCount']

  def getScore(self):
    temp = Kapi.score(self.id)
    self.score = temp['score']
    self.dayChange = temp['scoreDelta']['dayChange']
    self.monthChange = temp['scoreDelta']['monthChange']
    self.weekChange = temp['scoreDelta']['weekChange']

  def getTopics(self):
    temp = Kapi.topics(self.id)
    self.topics = []
    for each in temp:
      self.topics.append(each['name'])

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
  userName = sys.argv[1]
  num = sys.argv[2]

  if userName and num:
    pass
  else:
    print "kloutFF.py <username> <number of tweets to grab>"
    sys.exit()

  userTimeline = []

  [userTimeline.append(each) for each in getTweets(userName, num, api)]


if __name__ == '__main__':
  main()
