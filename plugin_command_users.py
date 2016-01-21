# Magnet2 by Grom PE. Public domain.
from magnet_api import *
from magnet_utils import *

def command_users(bot, room, nick, access_level, parameters, message):
  aff = {'none': ' ', 'member': 'm', 'admin': 'A', 'owner': 'O'}
  role = {'visitor': ' ', 'participant': '+', 'moderator': '@'}
  rolen = {'visitor': 0, 'participant': 1, 'moderator': 2}
  output = '%d users:'%(len(bot.roster[room]))
  sortednicks = bot.roster[room].keys()

  def cmpnicks(x, y):
    rolex = rolen.get(bot.roster[room][x][ROSTER_ROLE], 0)
    roley = rolen.get(bot.roster[room][y][ROSTER_ROLE], 0)
    if rolex == roley:
      return cmp(x.lower(), y.lower())
    return roley-rolex
  
  sortednicks.sort(cmpnicks)
  for i in sortednicks:
    show = bot.roster[room][i][ROSTER_STATUS]
    status = bot.roster[room][i][ROSTER_STATUS_TEXT]
    if status:
      p = status.find('\n')
      if p != -1: status = status[:p]+' [...]'
      if len(status) > 70: status = status[:64]+' [...]'
      full_status = '%s (%s)'%(show, status)
    else:
      full_status = show
    if access_level < LEVEL_MODERATOR or not parameters:
      user = i
    else:
      user = '%s (%s)'%(i, bot.roster[room][i][ROSTER_JID])
    output += '\n%s%s %s | %s'%(
      role.get(bot.roster[room][i][ROSTER_ROLE], '?'),
      aff.get(bot.roster[room][i][ROSTER_AFFILIATION], '?'),
      user, full_status
    )
  bot.send_room_message('%s/%s'%(room, nick), output)

def load(bot):
  bot.add_command('users', command_users, LEVEL_IGNORED)

def unload(bot):
  pass

def info(bot):
  return 'Users plugin v1.0'
