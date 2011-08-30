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
from magnet_api import *
import re, socket

def command_dns(bot, room, nick, access_level, parameters, message):
  if not parameters: return "Expected IP or domain name"
  if re.match(r'\d+\.\d+\.\d+\.\d+', parameters):
    ip = parameters
    try: res = socket.gethostbyaddr(ip)[0]
    except: res = 'Non-existent domain.'
  else:
    domain = parameters
    try: res = socket.gethostbyname(domain)
    except: res = 'No IP address found.'
  return res

def load(bot):
  bot.add_command('dns', command_dns, LEVEL_MEMBER, 'dns')
  pass

def unload(bot):
  pass

def info(bot):
  return 'DNS plugin v1.0'
