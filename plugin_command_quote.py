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
import xmpp, random, time
from magnet_api import *
from magnet_utils import *

quote_db = {}

def getquote(bot, room, number):
  if not room in quote_db: return
  if number > len(quote_db[room]) or number < 1: return
  return quote_db[room][number-1]

def addquote(bot, room, quotedic):
  if not room in quote_db: quote_db[room] = []
  if quotedic:
    quote_db[room].append(quotedic)

def delquote(bot, room, number):
  if not room in quote_db: return
  if number > len(quote_db[room]) or number < 1: return
  del quote_db[room][number-1]

def command_quote(bot, room, nick, access_level, parameters, message):
  if not room in quote_db or len(quote_db[room]) == 0:
    return 'No quotes added yet!'
  if not parameters:
    number = random.randint(1, len(quote_db[room]))
  else:
    try:
      number = int(parameters)
    except:
      search = parameters.lower()
      found = []
      for i in xrange(len(quote_db[room])):
        if search in quote_db[room][i]['quote'].lower():
          found.append(i)
      if len(found) == 0:
        return "No such text found in quotes."
      elif len(found) == 1:
        number = found[0]+1
      else:
        return "Text found in quotes %s."%(', '.join(['#%d'%(x+1) for x in found]))

  existent_quote = getquote(bot, room, number)
  if not existent_quote:
    return "There's no quote #%d, and there are %d quotes."%(number, len(quote_db[room]))

  res = 'Quote #%d: %s'%(number, existent_quote['quote'])
  if message.getType() != 'groupchat' and access_level >= LEVEL_ADMIN:
    t = timeformat(time.time()-existent_quote['time'])
    res = '%s\n(added by %s %s ago)'%(res, existent_quote['jid'], t)
  
  return res

def command_addquote(bot, room, nick, access_level, parameters, message):
  if not parameters: return 'Expected quote text to add.'
  quote = parameters

  jid = bot.roster[room][nick][ROSTER_JID]
  if jid != None: jid = xmpp.JID(jid).getStripped().lower()

  quotedic = {
    'quote': quote,
    'jid': jid,
    'time': time.time(),
  }
  addquote(bot, room, quotedic)
  number = len(quote_db[room])
  return "Quote #%d added."%(number)

def command_delquote(bot, room, nick, access_level, parameters, message):
  try: number = int(parameters)
  except: return 'Expected quote number to delete.'

  jid = bot.roster[room][nick][ROSTER_JID]
  if jid != None: jid = xmpp.JID(jid).getStripped().lower()

  if not room in quote_db or len(quote_db[room]) == 0:
    return 'No quotes added yet!'
    
  existent_quote = getquote(bot, room, number)
  if not existent_quote:
    return "There's no quote #%d, and there is total of %d quotes."%(number, len(quote_db[room]))
  
  if access_level < LEVEL_ADMIN:
    if not jid or existent_quote['jid'] != jid or time.time() - existent_quote['time'] > 3600:
      return "You can't delete quote #%d."%(number)
    
  delquote(bot, room, number)
  return "Quote #%d deleted."%(number)

def load(bot):
  global quote_db
  quote_db = bot.load_database('quote') or {}
  bot.add_command('quote', command_quote, LEVEL_GUEST, 'quote')
  bot.add_command('addquote', command_addquote, LEVEL_MEMBER, 'quote')
  bot.add_command('delquote', command_delquote, LEVEL_MEMBER, 'quote')

def unload(bot):
  bot.save_database('quote', quote_db)

def info(bot):
  return 'Quote plugin v1.0.2'
