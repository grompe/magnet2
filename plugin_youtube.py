# Magnet2 by Grom PE. Public domain.
import urllib2
import urlparse
from magnet_api import *
from magnet_utils import *

def getyoutubeinfo(yid):
  try:
    site = urllib2.urlopen('http://www.youtube.com/get_video_info?video_id='+yid)
  except urllib2.HTTPError, e:
    if e.code == 404:
      return 'The video is not available or is being processed.'
    elif e.code == 400:
      return 'Malformed video ID.'
    else:
      return 'Error %s.'%(e.code)

  rec = site.read()
  site.close()
  res = urlparse.parse_qs(rec)

  title = res.get("title", ["???"])[0]
  author = res.get("author", ["???"])[0]
  duration = int(res.get("length_seconds", [-1])[0])
  views = int(res.get("view_count", [-1])[0])
  
  min = duration / 60
  sec = duration - min * 60

  return "%s [by %s, %02d:%02d, %d views]"%(title, author, min, sec, views)

def event_room_message(bot, (message, room, nick)):
  if message.getType() == 'groupchat':
    target = room
  else:
    target = room+'/'+nick

  text = message.getBody()
  if text:
    # allow identifying youtube links from self messages but prevent infinite loop
    if nick == bot.self_nick[room] and "'s YouTube link: " in text:
      return

    yid = None
    p = text.find('www.youtube.com/watch')
    if p != -1:
      p = text.find('v=', p)
      if p != -1:
        yid = text[p+2:p+2+11]
    if not yid:
      p = text.find('http://youtu.be/')
      if p != -1:
        yid = text[p+16:p+16+11]

    if yid and len(yid) == 11:
      try:
        res = "%s's YouTube link: %s"%(nick, getyoutubeinfo(yid))
        bot.send_room_message(target, res)
      except Exception, e:
        bot.log_warn('Error getting youtube video "%s" info: %s' % (yid, str(e)))

def load(bot):
  pass

def unload(bot):
  pass

def info(bot):
  return 'Youtube plugin v1.0.4'
