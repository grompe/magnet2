# Magnet2 by Grom PE. Public domain.
from magnet_api import *

def command_alias(bot, room, nick, access_level, parameters, message):
  try: (new_command, call_command_parameters) = parameters.split(' ', 1)
  except:
    if not parameters:
      return (
        "Expected parameters: <new_command> <call_command> [call_parameters] where %s designates original parameters,"+
        "\nOr [alias_command] to see an existing alias."
      )
    alias = parameters
    if not room in bot.aliases or not alias in bot.aliases[room]:
      return "Unknown alias %s"%(alias)
    return "%s calls: %s %s"%(alias, bot.aliases[room][alias][0], bot.aliases[room][alias][1])
  try: (call_command, call_parameters) = call_command_parameters.split(' ', 1)
  except: (call_command, call_parameters) = (call_command_parameters, '')
  if new_command in bot.commands:
    return 'Command %s already exists.'%(new_command)
  if not call_command in bot.commands:
    return 'Command %s does not exist.'%(call_command)

  if bot.commands[call_command]['level'] > access_level:
    return 'Can not add an alias to higher level command.'

  if not room in bot.aliases: bot.aliases[room] = {}
  updating = new_command in bot.aliases[room]
    
  bot.aliases[room][new_command] = (call_command, call_parameters)
  return "Alias %s %s."%(new_command, ('added', 'updated')[updating])

def command_aliases(bot, room, nick, access_level, parameters, message):
  if not room in bot.aliases or len(bot.aliases[room]) == 0:
    return "No aliases for this room defined."
  return "Defined aliases for this room: %s."%(', '.join(bot.aliases[room].keys()))

def command_delalias(bot, room, nick, access_level, parameters, message):
  if parameters == '': return "Expected alias name."
  if not room in bot.aliases or not parameters in bot.aliases[room]:
    return "No alias %s found."%(parameters)
  del bot.aliases[room][parameters]
  return "Alias %s removed."%(parameters)

def load(bot):
  bot.aliases = bot.load_database('aliases') or {}
  bot.add_command('alias', command_alias, LEVEL_ADMIN)
  bot.add_command('aliases', command_aliases, LEVEL_ADMIN)
  bot.add_command('delalias', command_delalias, LEVEL_ADMIN)

def save(bot):
  bot.save_database('aliases', bot.aliases)

def unload(bot):
  del bot.aliases

def info(bot):
  return 'Alias plugin v1.0.1'
