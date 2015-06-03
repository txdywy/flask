import requests
import json

def shuffle():
    r = requests.get('http://deckofcardsapi.com/api/shuffle/?deck_count=6')
    d = json.loads(r.text)
    return d

def draw(deck_id, count=2):
    r = requests.get('http://deckofcardsapi.com/api/draw/%s/?count=%s' % (str(deck_id), str(count)))
    d = json.loads(r.text)
    return d

def reshuffle(deck_id):
    r = requests.get('http://deckofcardsapi.com/api/shuffle/%s/' % str(deck_id))
    d = json.loads(r.text)
    return d

def reshuffle():
    r = requests.get('http://deckofcardsapi.com/api/new')
    d = json.loads(r.text)
    return d
