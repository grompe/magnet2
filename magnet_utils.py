# Magnet2 by Grom PE. Public domain.
import xmpp, os, time, cPickle

try:
  from HTMLParser import HTMLParser
  htmlparser_available = True
except:
  htmlparser_available = False

def iq_set_affiliation(room, nick, affiliation, reason=None):
  iq = xmpp.Iq('set', xmpp.NS_MUC_ADMIN, {}, room)
  item = iq.getTag('query').setTag('item')
  item.setAttr('nick', nick)
  item.setAttr('affiliation', affiliation)
  if reason: item.addChild('reason', {}, reason)
  return iq

def iq_set_role(room, nick, role, reason=None):
  iq = xmpp.Iq('set', xmpp.NS_MUC_ADMIN, {}, room)
  item = iq.getTag('query').setTag('item')
  item.setAttr('nick', nick)
  item.setAttr('role', role)
  if reason: item.addChild('reason', {}, reason)
  return iq

def serialize(fname, data):
  f = open(fname, 'wb')
  result = cPickle.dump(data, f, 2)
  f.close()
  return result

def unserialize(fname):
  if not os.path.exists(fname): return False
  f = open(fname, 'rb')
  result = cPickle.load(f)
  f.close()
  return result

def writelog(filename, text):
  s = '[%s] %s\n'%(time.strftime('%d %b %Y %H:%M:%S'), text)
  f = open(filename, 'a')
  f.write(s.encode('utf-8'))
  f.close()

def hasbadwords(text):
  badwords = ['bitch', 'fuck', 'asshole', 'shit', 'cunt', 'whore', 'slut',
    'cocksuck', 'f*ck', 'b*tch', 'sh*t', 'sh!t', 'faggot', 'whor3',
    'b!tch', 'phuck', 'sh1t', 'nigger', 'wank', 'goddamn', 'dickhead',
    'bollocks', 'bastard', 'my dick', 'dafuq', 'biatch']
  
  textl = text.replace(u'\xad', '').lower()
  for word in badwords:
    if word in textl: return True
  return False

def unhtml(content):
  if htmlparser_available:
    return HTMLParser().unescape(content)
  content = content.replace('&lt;', '<')
  content = content.replace('&gt;', '>')
  content = content.replace('&quot;', '"')
  content = content.replace('&#39;', "'")
  return content.replace('&amp;', '&')

def timeformat(s):
  s = s//1 # Rounding
  days = s//86400
  s -= days*86400
  hours = s//3600
  s -= hours*3600
  minutes = s//60
  s -= minutes*60
  result = ''
  limit = 0
  if days>0:
    result += ' %d day%s'%(days, ('', 's')[days>1])
    limit = 2
  if hours>0:
    result += ' %d hour%s'%(hours, ('', 's')[hours>1])
    limit += 1
  if limit<2 and minutes>0:
    result += ' %d minute%s'%(minutes, ('', 's')[minutes>1])
  if limit<1 and s>0:
    result += ' %d second%s'%(s, ('', 's')[s>1])
  return result[1:]

def separate_target_reason(bot, room, parameters):
  target = parameters
  reason = None
  if not target in bot.roster[room]:
    p = len(parameters)
    while True:
      p = parameters.rfind(' ', 0, p)
      if p == -1:
        if parameters.find(' ') != -1:
          (target, reason) = parameters.split(' ', 1)
        break
      if parameters[:p] in bot.roster[room]:
        target = parameters[:p]
        reason = parameters[p+1:]
        break
  return (target, reason)

def force_directory(dirname):
  if not os.path.exists(dirname): 
    os.makedirs(dirname, 0755)

if __name__ == "__main__":
  pass
