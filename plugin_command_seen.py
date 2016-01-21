# Magnet2 by Grom PE. Public domain.
import xmpp, time, re
from magnet_api import *
from magnet_utils import *

seen_db = {}

def seenify_nick(nick):
  """
    - convert to lowercase
    - remove the leading "the ", "a ", "an ", "dr.", "mr.", "mrs.", "ms."
    - pick the first word or two with space in between, not counting the space
    - remove all trailing underscores
  """
  nick = nick.lower()
#  r = re.compile(r'(?:(?:the )|(?:a )|(?:an )|(?:dr\.)|(?:mr\.)|(?:mrs\.)|(?:ms\.)|(?:\W))*(\w+?)(?:_+)?\b')
  r = re.compile(r'(?:(?:the )|(?:a )|(?:an )|(?:dr\.)|(?:mr\.)|(?:mrs\.)|(?:ms\.)|(?:\W))*(\w+?)(?:(?: )(\w+))?(?:_+)?\b')
  match = r.match(nick)
  if not match: return ''
  return '%s%s'%(match.group(1), match.group(2) or '')

def addseen(bot, room, nick, jid, typ, data=None):
  if not 'seen' in bot.get_config(room, 'options'): return

  orignick = nick
  nick = seenify_nick(nick)
  if not nick: return

  if jid: jid = xmpp.JID(jid).getStripped().lower()
  if not room in seen_db: seen_db[room] = {}
  if not nick in seen_db[room]: seen_db[room][nick] = {}
  if typ == 'message':
    seen_db[room][nick].update({
      'message': data,
      'messagetime': time.time(),
      'messagenick': orignick
    })
  seen_db[room][nick].update({
    'time': time.time(),
    'type': typ,
    'data': data,
    'nick': orignick,
  })
  if jid: seen_db[room][nick].update({'jid': jid})

def event_room_message(bot, (message, room, nick)):
  text = message.getBody()
  if message.getType() == 'groupchat' and text and nick in bot.roster[room]:
    addseen(bot, room, nick, bot.roster[room][nick][ROSTER_JID], 'message', text)

def event_nick_changed(bot, (presence, room, nick, newnick)):
  addseen(bot, room, nick, bot.roster[room][nick][ROSTER_JID], 'nick', newnick)

def event_kicked(bot, (presence, room, nick, actor, reason)):
  addseen(bot, room, nick, None, 'kick', reason)

def event_banned(bot, (presence, room, nick, actor, reason)):
  addseen(bot, room, nick, None, 'ban', reason)

def event_removed_by_affiliation(bot, (presence, room, nick)):
  addseen(bot, room, nick, None, 'kick')

def event_removed_by_membersonly(bot, (presence, room, nick)):
  addseen(bot, room, nick, None, 'kick')

def event_removed_by_shutdown(bot, (presence, room, nick)):
  addseen(bot, room, nick, None, 'quit', 'User has been removed from the room due to service shutdown.')

def event_left(bot, (presence, room, nick, jid)):
  addseen(bot, room, nick, jid, 'quit', presence.getTagData('status'))

def event_status_changed(bot, (presence, room, nick, jid, status, status_text)):
  addseen(bot, room, nick, jid, 'status', (status, status_text))

def event_joined(bot, (presence, room, nick, jid, role, affiliation, status, status_text)):
  addseen(bot, room, nick, jid, 'join', (status, status_text))

def command_seen(bot, room, nick, access_level, parameters, message):
  if not parameters: return 'Whom are you looking for?'
  target = parameters
  if target == nick: return 'Are you looking for yourself?'
  
  seennick = seenify_nick(target)
  if not seennick: return "I don't remember such weird nicks."

  if not room in seen_db or not seennick in seen_db[room]:
    if bot.in_roster(room, target):
      return "%s is in the room, somewhere."%(target)
    else:
      return "I don't remember seeing %s."%(target)

  seconds = time.time()-seen_db[room][seennick]['time']
  ago = timeformat(seconds)
  typ = seen_db[room][seennick]['type']
  data = seen_db[room][seennick]['data']
  orignick = seen_db[room][seennick]['nick']

  if seconds <= 300:
    if typ == 'join':
      res = '%s has just joined with status %s.'%(orignick, data[0])
    elif typ == 'status':
      res = '%s has just changed status to %s.'%(orignick, data[0])
    elif typ == 'message':
      res = '%s is still active.'%(orignick)
    elif typ == 'nick':
      res = '%s has just changed nick to %s.'%(orignick, data)
    elif typ == 'quit':
      res = '%s has just left.'%(orignick)
    elif typ == 'ban':
      res = '%s has just been banned.'%(orignick)
    elif typ == 'kick':
      res = '%s has just been kicked.'%(orignick)
    else:
      res = '%s just did something unknown.'%(orignick)
  else:
    if typ == 'join':
      res = '%s has joined with status %s %s ago.'%(orignick, data[0], ago)
    elif typ =='status':
      res = '%s has changed status to %s %s ago.'%(orignick, data[0], ago)
    elif typ =='message':
      res = '%s has responded %s ago.'%(orignick, ago)
    elif typ == 'nick':
      res = '%s has changed nick to %s %s ago.'%(orignick, data, ago)
    elif typ =='quit':
      res = '%s has left %s ago.'%(orignick, ago)
    elif typ =='ban':
      res = '%s has been banned %s ago.'%(orignick, ago)
    elif typ == 'kick':
      res = '%s has been kicked %s ago.'%(orignick, ago)
    else:
      res = '%s did something unknown %s ago.'%(orignick, ago)

  if message.getType() != 'groupchat':
    if access_level >= LEVEL_MEMBER:
      if 'message' in seen_db[room][seennick]:
        text = seen_db[room][seennick]['message']
        messagetime = seen_db[room][seennick]['messagetime']
        messagenick = seen_db[room][seennick]['messagenick']
        messageago = timeformat(time.time() - messagetime)
        if text[:4]=='/me ':
          post = '* %s %s'%(messagenick, text[4:])
        else:
          post = '<%s> %s'%(messagenick, text)
        res += '\nLast message from %s ago: %s'%(messageago, post)
    if access_level >= LEVEL_ADMIN:
      jid = seen_db[room][seennick]['jid']
      if jid:
        res += '\nJID: %s'%(jid)

  return res

def command_seenjid(bot, room, nick, access_level, parameters, message):
  if not parameters: return 'Expected JID to look for.'
  look_jid = parameters
  if not '@' in look_jid: return 'Expected JID in form of user@host.'
  look_jid = look_jid.lower()
  if not room in seen_db or len(seen_db[room]) == 0:
    return 'The seen database is empty.'
  found = []
  for look_nick in seen_db[room]:
    if seen_db[room][look_nick].get('jid', None) == look_jid:
      found.append(look_nick)
  if len(found) == 0:
    return "I don't remember seeing anyone with JID %s."%(look_jid)
  return 'These nicks were seen with JID %s: %s'%(look_jid, ', '.join(found))

def load(bot):
  global seen_db
  seen_db = bot.load_database('seen') or {}
  bot.add_command('seen', command_seen, LEVEL_GUEST, 'seen')
  bot.add_command('seenjid', command_seenjid, LEVEL_ADMIN, 'seenjid')

def save(bot):
  bot.save_database('seen', seen_db)

def unload(bot):
  pass

def info(bot):
  return 'Seen plugin v1.0.7'
