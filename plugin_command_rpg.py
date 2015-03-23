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
import time, random, md5
from magnet_api import *

def command_roll(bot, room, nick, access_level, parameters, message):
  p = parameters.find('d')
  x = parameters.find('+')
  s = parameters.find(' ')
  if s != -1: parameters = parameters[:s]
  number = 0
  sides = 0
  add = 0
  if p == -1: p = len(parameters)
  try:
    if x == -1:
      sides = int(parameters[p+1:])
    else:
      sides = int(parameters[p+1:x])
      add = int(parameters[x+1:])
    number = int(parameters[:p])
  except:
    pass
  if number < 1: number = 1
  if number > 10: number = 10
  if sides < 2: sides = 6
  if sides > 100: sides = 100
  if add < -1000: add = -1000
  if add > 1000: add = 1000
  rolls = []
  for i in range(number): rolls.append(random.randint(1, sides))
  if add: rolls.append(add)
  output = '%s, %dd%d+%d roll: %s'%(nick, number, sides, add, '+'.join([str(i) for i in rolls]))
  if len(rolls) > 1: output += '=' + str(sum(rolls))
  return output

def command_flip(bot, room, nick, access_level, parameters, message):
  return nick+', '+random.choice(['Heads!', 'Tails!'])

def load(bot):
  bot.add_command('roll', command_roll, LEVEL_GUEST, 'rpg')
  bot.add_command('flip', command_flip, LEVEL_GUEST, 'rpg')

def unload(bot):
  pass

def info(bot):
  return 'RPG plugin v1.0'
