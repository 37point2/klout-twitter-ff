#!/usr/bin/python

import tweepy
import pyklout
import json
import sys

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



def main():

  userName = sys.argv[1]


if __name__ == '__main__':
  main()
