#
#  This file is part of Magnet2.
#  Copyright (c) 2011  Grom PE
#
#  Magnet2 is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or     
#  (at your option) any later version.                                   
#
#  Magnet2 is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with Magnet2.  If not, see <http://www.gnu.org/licenses/>.
#
import xmpp, urllib2, StringIO, base64
from magnet_api import *
from magnet_utils import *
from PIL import Image

def getyoutubeinfo(yid):
  try:
    site = urllib2.urlopen('http://gdata.youtube.com/feeds/api/videos/'+yid)
  except urllib2.HTTPError, e:
    if e.code == 404:
      return ('The video is not available or is being processed.', None)
    elif e.code == 400:
      return ('Malformed video ID.', None)
    else:
      return ('Error %s.'%(e.code), None)

  rec = site.read()
  #writelog('_debug-youtube.txt', rec)
  site.close()
  p = rec.find("<title type='text'>")
  p2 = rec.find("</title>", p+19)
  title = unhtml(rec[p+19:p2].decode("utf-8"))

  p = rec.find("<author><name>", p2)
  author = '???'
  if p != -1:
    p2 = rec.find('<', p+14)
    author = rec[p+14:p2]
  
  # experimental: with thumbnail
  p = rec.find("<media:thumbnail url='", p2)
  if p != -1:
    p2 = rec.find("'", p+22)
    thumbnail = rec[p+22:p2]

  p = rec.find("<yt:duration seconds='", p2)
  min = 0
  sec = 0
  if p != -1:
    p2 = rec.find("'", p+22)
    sec = int(rec[p+22:p2])
    min = sec/60
    sec = sec-min*60

  p = rec.find("viewCount='", p2)
  views = 0
  if p != -1:
    p2 = rec.find("'", p+11)
    views = int(rec[p+11:p2])

  return ("%s [by %s, %02d:%02d, %d views]"%(title, author, min, sec, views), thumbnail)

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
    p = text.find('http://www.youtube.com/watch?')
    if p != -1:
      p = text.find('v=', p)
      if p != -1:
        yid = text[p+2:p+2+11]
    if not yid:
      p = text.find('http://youtu.be/')
      if p != -1:
        yid = text[p+16:p+16+11]

    if yid and len(yid) == 11:
      #try:
        (res, thumbnail) = getyoutubeinfo(yid)
        resprefix = "%s's YouTube link: "%(nick)
        if thumbnail:
          try:
            thumbdata = urllib2.urlopen(thumbnail).read()
          except urllib2.HTTPError:
            thumbnail = None
        if thumbnail:
          thumb = Image.open(StringIO.StringIO(thumbdata))
          thumb = thumb.resize((40, 30), Image.BILINEAR)
          output = StringIO.StringIO()
          thumb.save(output, format="JPEG")
          contents = output.getvalue()
          output.close()

          thumb = 'data:image/jpg;base64,%s'%(base64.b64encode(contents))

          xhtml = xmpp.Node('body', {'xmlns': 'http://www.w3.org/1999/xhtml'})

          #addChild(self, name=None, attrs={}, payload=[], namespace=None, node=None):
          xhtml.addChild('p', payload=[resprefix, ' '+res,
            xmpp.Node('img', {'src': thumb, 'height': '24', 'width': '32'})])

          #xhtml.setTagData('p', res)
          #xhtml.addChild('p').addChild('img',
          #  {'src': thumbnail, 'height': '90', 'width': '120'})

          bot.send_room_message_xhtml(target, res, xhtml)
        else:
          bot.send_room_message(target, resprefix+res)
      #except:
        pass

def load(bot):
  pass

def unload(bot):
  pass

def info(bot):
  return 'Youtube-t plugin v1.0 (with thumbnails, experimental)'
