#!/usr/bin/env python
#coding=utf-8
#
#  Magnet2
#  Python XMPP MUC entertainment, informational and administration bot
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

import xmpp, time, os, sys, socket, traceback
from magnet_api import *
from magnet_utils import *
from magnet_config import *

require_level_string = {
  LEVEL_IGNORED         : '',
  LEVEL_DEVOICED_GUEST  : '',
  LEVEL_GUEST           : '',
  LEVEL_DEVOICED_MEMBER : 'You must be a member to access this command.',
  LEVEL_MEMBER          : 'You must be a member to access this command.',
  LEVEL_MODERATOR       : 'You must be a moderator to access this command.',
  LEVEL_ADMIN           : 'You must be an admin to access this command.',
  LEVEL_OWNER           : 'You must be an owner to access this command.',
  LEVEL_BOT_OWNER       : 'You must be a bot owner to access this command.',
}

access_level_string = {
  LEVEL_IGNORED         : 'ignored',
  LEVEL_DEVOICED_GUEST  : 'devoiced guest',
  LEVEL_GUEST           : 'guest',
  LEVEL_DEVOICED_MEMBER : 'devoiced member',
  LEVEL_MEMBER          : 'member',
  LEVEL_MODERATOR       : 'moderator',
  LEVEL_ADMIN           : 'admin',
  LEVEL_OWNER           : 'owner',
  LEVEL_BOT_OWNER       : 'bot owner',
}

class Magnet2Bot(object):

  def __init__(self, configuration):
    self.version = '2.0'
    self.configuration = {}
    self.timed_events = TimedEvent()
    self.roster = {}
    self.joined_rooms = []
    self.self_nick = {}
    self.plugins = {}
    self.plugin_commands = {'__main__': []}
    self.configuration = configuration 
    self.auth_success = False

    # general events
    self.event_room_presence = Event()
    self.event_room_message = Event()
    self.event_room_iq = Event()

    # additional events - presence
    self.event_nick_changed = Event()
    self.event_kicked = Event()
    self.event_banned = Event()
    self.event_removed_by_affiliation = Event()
    self.event_removed_by_membersonly = Event()
    self.event_removed_by_shutdown = Event()
    self.event_left = Event()
    self.event_role_affiliation_changed = Event()
    self.event_affiliation_changed = Event()
    self.event_role_changed = Event()
    self.event_status_changed = Event()
    self.event_joined = Event()
    self.event_room_roster = Event()

    self.event_unhandled_command = Event()
    
    force_directory(DATA_PATH)
    force_directory(LOG_PATH)
    
    self.commands = {}
    #self.add_command('crash', self.command_crash, LEVEL_BOT_OWNER)
    self.add_command('quit', self.command_quit, LEVEL_BOT_OWNER)
    self.add_command('eval', self.command_eval, LEVEL_BOT_OWNER)
    self.add_command('exec', self.command_exec, LEVEL_BOT_OWNER)
    self.add_command('setnick', self.command_setnick, LEVEL_ADMIN)
    self.add_command('setstatus', self.command_setstatus, LEVEL_ADMIN)
    self.add_command('option', self.command_option, LEVEL_ADMIN)
    self.add_command('options', self.command_options, LEVEL_ADMIN)
    self.add_command('access', self.command_access, LEVEL_GUEST)
    self.add_command('list', self.command_list, LEVEL_GUEST)

    jid = xmpp.JID(self.configuration['jid'])
    self.client = xmpp.Client(jid.getDomain(), debug=[]) #'socket'
    if not self.client.connect():
      self.log_error('Could not connect to the server.')
      return
    self.auth_success = True
    self.client.RegisterHandler('message', self.got_message)
    self.client.RegisterHandler('presence', self.got_presence)
    self.client.RegisterHandler('iq', self.got_iq)
    self.load_plugins()
    self.client.auth(jid.getNode(), self.configuration['password'], jid.getResource())
    self.join_rooms()

    self.keepalive_timer = TimedEventHandler(self.timer_keepalive, 600)
    self.timed_events.add(self.keepalive_timer)

  def run(self):
    if self.auth_success:
      try:
        while 1:
          try:
            self.client.Process(1)
          except KeyboardInterrupt:
            self.shutdown()
          self.timed_events(self)
          if not self.client.isConnected():
            self.log_warn('Connection broke, reconnecting...')
            self.client.reconnectAndReauth()
            self.join_rooms()
      except:
        self.shutdown("Crashed!")

  def timer_keepalive(self, sender, arg):
    self.client.send(' ')

  def load_plugins(self):
    for plugin in self.configuration['plugins']:
      self.load_plugin('plugin_%s'%(plugin))

  def load_plugin(self, plugin):
    if plugin in self.plugins:
      return self.reload_plugin(plugin)
    try:
      p = __import__(plugin)
      reload(p) # FIXME: weird, but works
      self.plugin_commands[plugin] = []
      for x in dir(p):
        if x[:6] == 'event_':
          self.__getattribute__(x).add(p.__getattribute__(x))
      p.load(self)
      self.log_info('Plugin %s loaded: %s'%(plugin, p.info(self)))
      if len(self.plugin_commands[plugin]) > 0:
        self.log_info('Plugin %s added commands %s'%(plugin, self.plugin_commands[plugin]))
      self.plugins[plugin] = p
      return p
    except:
      self.log_error('Plugin %s raised an exception and was not loaded\n%s'%
        (plugin, traceback.format_exc()))

  def reload_plugin(self, plugin):
    if not plugin in self.plugins:
      return self.load_plugin(plugin)
    self.unload_plugin(plugin)
    return self.load_plugin(plugin)

  def unload_plugins(self):
    for plugin in self.plugins.keys():
      self.unload_plugin(plugin)

  def unload_plugin(self, plugin):
    p = self.plugins[plugin]
    p.unload(self)
    for x in dir(p):
      if x[:6] == 'event_':
        self.__getattribute__(x).remove(p.__getattribute__(x))

    if len(self.plugin_commands[plugin]) > 0:
      self.log_info('Removing plugin %s commands %s'%(plugin, self.plugin_commands[plugin]))
      for command in self.plugin_commands[plugin]:
        if command in self.commands:
          del self.commands[command]
        else:
          self.log_warn('Could not find command %s to remove'%(command))

    del self.plugin_commands[plugin]  

    self.log_info('Plugin %s unloaded: %s'%(plugin, p.info(self)))
    del self.plugins[plugin]

  def exception_in(self, handler):
    plugin = handler.__module__
    if plugin in self.plugins:
      unload_message = ''
      if self.configuration['unload_plugin_on_error']:
        self.unload_plugin(plugin)
        unload_message = ' and was unloaded'
      self.log_error('Plugin %s raised an exception%s\n%s'%
        (plugin, unload_message, traceback.format_exc()))
    else:
      self.log_error('Module %s raised an exception\n%s'%
        (plugin, traceback.format_exc()))

  def add_command(self, command, handler, access_level, option=None):
    plugin = handler.__module__
    if command in self.commands:
      self.log_warn('Command %s is overridden by the module %s'%(command, plugin))
    self.plugin_commands[plugin].append(command)
    self.commands[command] = {
      'handler': handler,
      'level': access_level,
      'option': option
    }

  def save_database(self, name, data):
    serialize('%s%s.db'%(DATA_PATH, name), data)

  def load_database(self, name):
    return unserialize('%s%s.db'%(DATA_PATH, name))
  
  def writelog(self, filename, text):
    writelog(LOG_PATH+filename, text)

  def log_debug(self, message):
    if self.configuration['log_level'] >= 4:
      res = 'DEBUG: %s'%(message)
      self.writelog(self.configuration['info_file'], res)
      if self.configuration['echo_log']:
        try: print res
        except: pass

  def log_info(self, message):
    if self.configuration['log_level'] >= 3:
      res = 'INFO: %s'%(message)
      self.writelog(self.configuration['info_file'], res)
      if self.configuration['echo_log']:
        try: print res
        except: pass

  def log_warn(self, message):
    if self.configuration['log_level'] >= 2:
      res = 'WARNING: %s'%(message)
      self.writelog(self.configuration['info_file'], res)
      if self.configuration['echo_log']:
        try: print res
        except: pass

  def log_error(self, message):
    if self.configuration['log_level'] >= 1:
      res = 'ERROR: %s'%(message)
      self.writelog(self.configuration['error_file'], res)
      if self.configuration['echo_log']:
        try: print res
        except: pass

  def get_config(self, room, config):
    if room in self.configuration['mucs'] and config in self.configuration['mucs'][room]:
      return self.configuration['mucs'][room][config]
    elif config in self.configuration:
      return self.configuration[config]
    else:
      return None
  
  def in_roster(self, room, nick):
    return room in self.roster and nick in self.roster[room]

  def is_bot_owner(self, room, nick):
    jid = self.roster[room][nick][ROSTER_JID]
    if jid != None: jid = xmpp.JID(jid).getStripped().lower()
    return jid in self.configuration['bot_owners']

  def presence_room_bot(self, room, show='chat', status="I'm a bot [:]"):
    p = xmpp.Presence(
      '%s/%s'%(room, self.self_nick[room]),
      show=show,
      status=status
    )
    c = p.setTag('c', namespace = xmpp.NS_CAPS)
    c.setAttr('node', 'magnet2.py and not japyt')
    c.setAttr('ver', self.version)
    avatar_hash = self.configuration['avatar_hash']
    if avatar_hash:
      p.setTag(name='x', namespace=xmpp.NS_VCARD_UPDATE).setTag(name='photo').setData(avatar_hash)

    return p

  def join_rooms(self):
    for room in self.configuration['mucs']:
      self.join_room(room)

  def join_room(self, room, nick=None):
    self.self_nick[room] = nick or self.get_config(room, 'nick')
    self.roster[room] = {}
    p = self.presence_room_bot(room)
    p.setTag('x', namespace = xmpp.NS_MUC).setTagData('password', '')
    p.getTag('x', namespace = xmpp.NS_MUC).addChild('history', {'maxchars': '0', 'maxstanzas': '0'})
    self.client.send(p)

  def check_command_room_option(self, room, command):
    option = self.commands[command]['option']
    if option and not option in self.get_config(room, 'options'): return False
    return True
    
  def got_message(self, sess, message):
    jid = message.getFrom()
    nick = jid.getResource()
    room = jid.getStripped()
    text = message.getBody()
    if not room in self.configuration['mucs']:
      self.log_debug('Unexpected message from %s: %s'%(jid, message))
      return
    self.event_room_message(self, (message, room, nick))
    if not nick: return
    if not text: return
    if not room in self.roster: return
    if not nick in self.roster[room]: return
    if nick == self.self_nick[room]: return

    self.handle_command(text, message, room, nick)

  def handle_command(self, text, message, room, nick):
    # parse command and parameters:
    # allow to skip prefix in PM or when message begins with Nick: or Nick,
    s = text.split(' ', 1)
    cut = s[0]
    rest = len(s)>1 and s[1] or ''

    command = ''
    prefix = self.get_config(room, 'command_prefix')
    if cut and cut[0] == prefix: command = cut[1:]
    elif message.getType() == 'chat': command = cut
    if rest and cut == self.self_nick[room]+':' or cut == self.self_nick[room]+',':
      s = rest.split(' ', 1)
      cut = s[0]
      rest = len(s)>1 and s[1] or ''
      if cut and cut[0] == prefix: command = cut[1:]
      else: command = cut
    # also allow blahblah [command parameters] blahblah
    if not command:
      p = text.find('[')
      if p != -1:
        p2 = text.find(']')
        if p2 != -1:
          s = text[p+1:p2].split(' ', 1)
          cut = s[0]
          rest = len(s)>1 and s[1] or ''
          command = cut

    command = command.lower()
    
    parameters = rest
    if hasattr(self, 'aliases'):
      if room in self.aliases and command in self.aliases[room]:
        parameters = self.aliases[room][command][1].replace('%s', parameters)
        command = self.aliases[room][command][0]

    aff = self.roster[room][nick][ROSTER_AFFILIATION]
    role = self.roster[room][nick][ROSTER_ROLE]
    jid = self.roster[room][nick][ROSTER_JID]
    if jid != None: jid = xmpp.JID(jid).getStripped().lower()
    access_level = LEVEL_IGNORED
    ignored = False

    if hasattr(self, 'ignore_db'):
      prefix = self.get_config(room, 'db_prefix')
      if prefix in self.ignore_db:
        if nick in self.ignore_db[prefix]: ignored = True
        elif jid != None and jid in self.ignore_db[prefix]: ignored = True
    
    if not ignored:
      if role == 'visitor': access_level = LEVEL_DEVOICED_GUEST
      if role == 'participant': access_level = LEVEL_GUEST
      if aff == 'member' and role == 'visitor': access_level = LEVEL_DEVOICED_MEMBER
      if aff == 'member' and role == 'participant': access_level = LEVEL_MEMBER

    if role == 'moderator': access_level = LEVEL_MODERATOR
    if aff == 'admin': access_level = LEVEL_ADMIN
    if aff == 'owner': access_level = LEVEL_OWNER
    if jid in self.configuration['bot_owners']: access_level = LEVEL_BOT_OWNER

    disabled = self.get_config(room, 'commands_disabled')
    if command in self.commands and not command in disabled and self.check_command_room_option(room, command):
      command_level = self.commands[command]['level']
      ovr = self.get_config(room, 'commands_level_overrides')
      if command in ovr: command_level = ovr[command]
      response = None
      if access_level < command_level:
        if not ignored:
          response = require_level_string[command_level]
      else:
        handler = self.commands[command]['handler']
        if handler.__module__!='__main__':
          try:
            response = handler(self, room, nick, access_level, parameters, message)
          except:
            self.exception_in(handler)
            response = 'Command caused plugin to crash.'
        else:
          response = handler(room, nick, access_level, parameters, message)
      
      if response:
        pm_only = self.get_config(room, 'commands_pm_only')
        if message.getType() == 'groupchat' and not command in pm_only:
          self.send_room_message(room, response)
        else:
          self.send_room_message('%s/%s'%(room, nick), response)
    else:
      self.event_unhandled_command(self, (room, nick, command, access_level, parameters, message))

  def got_presence(self, sess, presence):
    jid = presence.getFrom()
    nick = jid.getResource()
    room = jid.getStripped()
    if not room in self.configuration['mucs']:
      self.log_debug('Unexpected presence from %s: %s'%(jid, presence))
      return
    self.event_room_presence(self, (presence, room, nick))

    user_x = presence.getTag('x', {}, xmpp.NS_MUC_USER)
    if user_x:
      self.handle_user_presence(presence, user_x, room, nick)
    else:
      if presence.getType() == 'error':
        code = presence.getTagAttr('error', 'code')
        if code == '401':
          self.log_warn('Cannot join room %s: password is required'%(room))
        elif code == '403':
          self.log_warn('Cannot join room %s: banned'%(room))
        elif code == '404':
          self.log_warn('Cannot join room %s: does not exist'%(room))
        elif code == '405':
          self.log_warn('Cannot join room %s: room creation is restricted'%(room))
        elif code == '406':
          self.log_warn('Cannot join room %s: reserved nick must be used'%(room))
        elif code == '407':
          self.log_warn('Cannot join room %s: not in member list'%(room))
        elif code == '409':
          if self.self_nick[room] == self.configuration['mucs'][room]['nick']:
            # try to rejoin with nick_ once
            self.join_room(room, self.self_nick[room]+'_')
          else:
            self.log_warn('Cannot join room %s: nickname is in use'%(room))
        elif code == '503':
          self.log_warn('Cannot join room %s: room is full'%(room))
      else:
        pass

  def got_iq(self, sess, iq):
    jid = iq.getFrom()
    nick = jid.getResource()
    room = jid.getStripped()
    if not room in self.configuration['mucs']:
      self.log_debug('Unexpected iq from %s: %s'%(jid, iq))
      return
    self.event_room_iq(self, (iq, room, nick))

  def handle_user_presence(self, presence, user_x, room, nick):
    item = user_x.getTag('item')
    status_code = user_x.getTags('status')
    status_codes = []
    if status_code: status_codes = [s.getAttr('code') for s in status_code]
    affiliation = item.getAttr('affiliation')
    role = item.getAttr('role')
    jid = item.getAttr('jid')
    actor = item.getTagData('actor')
    reason = item.getTagData('reason')

    if presence.getType() == 'unavailable':
      # user leaving
      if nick in self.roster[room]:
        if '303' in status_codes:
          newnick = item.getAttr('nick')
          self.roster[room][newnick] = self.roster[room][nick]
          self.event_nick_changed(self, (presence, room, nick, newnick))
        elif '307' in status_codes:
          self.event_kicked(self, (presence, room, nick, jid, actor, reason))
        elif '301' in status_codes:
          self.event_banned(self, (presence, room, nick, jid, actor, reason))
        elif '321' in status_codes:
          self.event_removed_by_affiliation(self, (presence, room, nick, jid))
        elif '322' in status_codes:
          self.event_removed_by_membersonly(self, (presence, room, nick, jid))
        elif '332' in status_codes:
          self.event_removed_by_shutdown(self, (presence, room, nick, jid))
        else:
          self.event_left(self, (presence, room, nick, jid))
        del self.roster[room][nick]
      else:
        self.log_warn('Unexpected unavailable presence from nick not in roster: %s'%(presence))
    else:
      # user joining or changing their status
      status = presence.getTagData('show') or 'online'
      status_text = presence.getTagData('status')

      if nick in self.roster[room]:
        if self.roster[room][nick][ROSTER_AFFILIATION] != affiliation:
          if self.roster[room][nick][ROSTER_ROLE] != role:
            self.event_role_affiliation_changed(self, (presence, room, nick, jid, role, affiliation))
          else:
            self.event_affiliation_changed(self, (presence, room, nick, jid, affiliation))
        elif self.roster[room][nick][ROSTER_ROLE] != role:
          self.event_role_changed(self, (presence, room, nick, jid, role))
        if self.roster[room][nick][ROSTER_STATUS] != status or self.roster[room][nick][ROSTER_STATUS_TEXT] != status_text:
          self.event_status_changed(self, (presence, room, nick, jid, status, status_text))
      else:
        # user joining
        if room in self.joined_rooms:
          self.event_joined(self, (presence, room, nick, jid, role, affiliation, status, status_text))
        else:
          self.event_room_roster(self, (presence, room, nick, jid, role, affiliation, status, status_text))
          # joining, getting room roster, self-presence
          if nick == self.self_nick[room]:
            #and '110' in status_codes
            # ejabberd doesn't attach status code 110
            self.joined_rooms.append(room)
            self.log_info('Joined room %s'%(room))

      self.roster[room][nick] = [affiliation, role, jid, status, status_text]

  def send_room_message(self, target, message):
    typ = 'groupchat'
    if target.find('/') != -1: typ = 'chat'
    self.client.send(xmpp.Message(target, message, typ))
    
  def send_room_message_xhtml(self, target, message, xhtmlbody):
    typ = 'groupchat'
    if target.find('/') != -1: typ = 'chat'
    m = xmpp.Message(target, message, typ)
    m.setTag('html', namespace=xmpp.NS_XHTML_IM).addChild(node=xhtmlbody)
    self.client.send(m)

  def command_crash(self, room, nick, access_level, parameters, message):
    self.herpderpadasdasdasfkalsjfakjqweuqwhfajh

  def command_quit(self, room, nick, access_level, parameters, message):
    self.shutdown()

  def command_options(self, room, nick, access_level, parameters, message):
    return 'Options for this room: %s'%(', '.join(self.configuration['mucs'][room]['options']))

  def command_option(self, room, nick, access_level, parameters, message):
    if parameters == '': return "Expected <option> [on|off]"
    try: (option, toggle) = parameters.split(' ', 1)
    except: (option, toggle) = (parameters, '')
    hasoption = option in self.configuration['mucs'][room]['options']
    if not toggle:
      if hasoption:
        return 'Option %s status: set.'%(option)
      else:
        return 'Option %s status: not set.'%(option)
    if toggle == 'on':
      if hasoption:
        return 'Option %s is already set.'%(option)
      self.configuration['mucs'][room]['options'].append(option)
      return 'Option %s added.'%(option)
    elif toggle =='off':
      if not hasoption:
        return 'Option %s is not set.'%(option)
      self.configuration['mucs'][room]['options'].remove(option)
      return 'Option %s removed.'%(option)
    else:
      return 'Can only "on" or "off" the option, not "%s" it.'%(toggle)

  def command_setnick(self, room, nick, access_level, parameters, message):
    if parameters == '': return "Can't set an empty nick."
    self.self_nick[room] = parameters
    self.client.send(self.presence_room_bot(room))

  def command_setstatus(self, room, nick, access_level, parameters, message):
    try: (show, status) = parameters.split(' ', 1)
    except: return "Expected parameters: <show> <status>"
    self.client.send(self.presence_room_bot(room, show, status))

  def command_eval(self, room, nick, access_level, parameters, message):
    if parameters == '': return "Give something to eval."
    try:
      result = '%s'%(eval(parameters))
    except Exception, e:
      result = 'Error: ' + str(e)
    return result

  def command_exec(self, room, nick, access_level, parameters, message):
    if parameters == '': return "Give something to exec."
    try:
      exec 'def execfunc(): %s'%(parameters)
      result = '%s'%(execfunc())
    except Exception, e:
      result = 'Error: ' + str(e)
    return result
  
  def command_access(self, room, nick, access_level, parameters, message):
    if message.getType() == 'chat':
      nick = 'Your'
    return '%s access level: %s.'%(nick, access_level_string[access_level])

  def command_list(self, room, nick, access_level, parameters, message):
    cando = []
    disabled = self.get_config(room, 'commands_disabled')
    ovr = self.get_config(room, 'commands_level_overrides')
    for command in self.commands:
      if not command in disabled and self.check_command_room_option(room, command):
        command_level = self.commands[command]['level']
        if command in ovr: command_level = ovr[command]
        if access_level >= command_level:
          cando.append(command)
    output = 'Available commands for %s: %s.'%(access_level_string[access_level], ', '.join(cando))
    self.send_room_message('%s/%s'%(room, nick), output)
    return ''

  def shutdown(self, quit_message="Owner said goodbye!"):
    self.log_info('Shutting down...')
    self.unload_plugins()
    for room in self.joined_rooms:
      p = xmpp.Presence(
        room+'/'+self.self_nick[room],
        status=quit_message,
        typ="unavailable"
      )
      self.client.send(p)
    quit()

if __name__ == "__main__":
  socket.setdefaulttimeout(10)
  the_bot = Magnet2Bot(configuration1)
  the_bot.run()
