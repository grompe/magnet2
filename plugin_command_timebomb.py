# Magnet2 by Grom PE. Public domain.
import random, time
from magnet_api import *
from magnet_utils import *

WIRE_COLORS = ("red", "orange", "yellow", "green", "blue", "indigo",
  "violet", "black", "white", "grey", "brown", "pink", "mauve", "beige",
  "aquamarine", "chartreuse", "bisque", "crimson", "fuchsia", "gold",
  "ivory", "khaki", "lavender", "lime", "magenta", "maroon", "navy",
  "olive", "plum", "silver", "tan", "teal", "turquoise")

lastbombed = {}
timebombed = {}

def timer_timebomb(bot, arg):
  for room in timebombed.keys():
    if time.time() >= timebombed[room]['time']:
      nick = timebombed[room]['nick']
      if bot.in_roster(room, nick):
        if timebombed[room]['dud']:
          bot.send_room_message(room,
            "%s is lucky! The bomb was dud!"%(nick))
        else:
          bot.send_room_message(room,
            "%s has failed to cut the wire in time! The bomb explodes!"%(nick))
      else:
        if timebombed[room]['dud']:
          bot.send_room_message(room,
            "Looks like %s ran away with a dud bomb."%(nick))
        else:
          bot.send_room_message(room,
            "You hear %s explode somewhere far away."%(nick))
      del timebombed[room]

timebomb_timer = TimedEventHandler(timer_timebomb, 2)

def event_nick_changed(bot, (presence, room, nick, newnick)):
  # bug/feature: reattaching the bomb to different person if original
  # has left and someone else changed their nick to timebombed person
  if room in timebombed and nick == timebombed[room]['nick']:
    timebombed[room]['nick'] = newnick

def command_timebomb(bot, room, nick, access_level, parameters, message):
  if not parameters: return 'Target expected.'
  if message.getType() != 'groupchat':
    return 'Sneaky! This works only in the groupchat.'
  if room in timebombed:
    if nick == timebombed[room]['nick']:
      return 'You have to take care of your own first.'
    return 'Only one victim at a time!'
  target = parameters
  if target[-1] == ' ': target = target[0:-1]
  if target == bot.self_nick[room]:
    return "Don't even think about it."
  if target == nick:
    return 'I am not designed to help in committing suicide.'
  if not bot.in_roster(room, target):
    return "I don't see %s here."%(target)
  if room in lastbombed and target in lastbombed[room]:
    return 'Give them a break! Pick someone else.'

  bombtimer = random.randint(15, 60)
  bombtime = time.time() + bombtimer

  bombwires = []
  for i in range(random.randint(2, 8)):
    bombwires.append(random.choice(WIRE_COLORS))

  lastbombed[room] = target
  timebombed[room] = {
    'nick': target,
    'dud': random.getrandbits(1),
    'time': bombtime,
    'wires': bombwires
  }
  return (
    "/me stuffs the bomb into %s's pants. The display reads %d seconds.\r\n"+
    "Defuse the bomb by cutting the correct wire (!cutwire color).\r\n"+
    "There are %d wires: %s."
  )%(target, bombtimer, len(bombwires), ', '.join(bombwires))


def command_cutwire(bot, room, nick, access_level, parameters, message):
  if not room in timebombed:
    return 'No bomb here but your imagination.'
  if not parameters: return 'Color expected.'
  if message.getType() != 'groupchat':
    return 'Sneaky! This works only in the groupchat.'
  if nick != timebombed[room]['nick']:
    return '%s is the only hope!'%(timebombed[room]['nick'])
  wire = parameters.lower()
  if wire[-1] == ' ': wire = wire[0:-1]
  if wire in timebombed[room]['wires']:
    timebombed[room]['wires'].remove(wire)

    result = random.randint(1, 3)
    if not timebombed[room]['wires']: result = 2
    if result == 1:
      return "That wire didn't do anything!"
    elif result == 2:
      timeleft = timebombed[room]['time']-time.time()
      if timeleft > 2:
        res = "You defused the bomb with %d seconds remaining!"%(timeleft)
      else:
        res = "You defused the bomb just in the last moment!"
      del timebombed[room]
      return res
    else:
      del timebombed[room]
      return "Wrong wire! The bomb explodes!"
  else:
    return 'There is no such wire colored "%s"!'%(wire)

def command_defuse(bot, room, nick, access_level, parameters, message):
  if not room in timebombed:
    return 'No bomb here but your imagination.'
  del timebombed[room]
  return 'The bomb has been defused.'

def load(bot):
  bot.add_command('timebomb', command_timebomb, LEVEL_GUEST, 'timebomb')
  bot.add_command('cutwire', command_cutwire, LEVEL_GUEST, 'timebomb')
  bot.add_command('defuse', command_defuse, LEVEL_ADMIN, 'timebomb')
  bot.timed_events.add(timebomb_timer)

def unload(bot):
  bot.timed_events.remove(timebomb_timer)
  
def info(bot):
  return 'Timebomb plugin v1.0.1'
