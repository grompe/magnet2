# Magnet2 by Grom PE. Public domain.
import time

LEVEL_IGNORED         = 0
LEVEL_DEVOICED_GUEST  = 1
LEVEL_GUEST           = 2
LEVEL_DEVOICED_MEMBER = 3
LEVEL_MEMBER          = 4
LEVEL_MODERATOR       = 5
LEVEL_ADMIN           = 6
LEVEL_OWNER           = 7
LEVEL_BOT_OWNER       = 8

ROSTER_AFFILIATION = 0
ROSTER_ROLE        = 1
ROSTER_JID         = 2
ROSTER_STATUS      = 3
ROSTER_STATUS_TEXT = 4

class Event(object):
  
  def __init__(self):
    self.handlers = []
  
  def add(self, handler):
    self.handlers.append(handler)
    return self
  
  def remove(self, handler):
    self.handlers.remove(handler)
    return self
  
  def try_handler(self, handler, sender, arg=None):
    if hasattr(sender, 'exception_in'):
      try: handler(sender, arg)
      except: sender.exception_in(handler)
    else:
      return handler(sender, arg)

  def fire(self, sender, arg=None):
    for handler in self.handlers:
      if self.try_handler(handler, sender, arg): break
  
  __call__ = fire


class TimedEventHandler(object):

  def __init__(self, handler, period):
    self.lastcall = 0
    self.handler = handler
    self.period = period

  def fire(self, sender, arg=None):
    self.handler(sender, arg)

  __call__ = fire


class TimedEvent(Event):

  def add(self, handler):
    if not isinstance(handler, TimedEventHandler):
      raise ValueError('handler must be an instance of TimedEventHandler')
    self.handlers.append(handler)
    return self
  
  def fire(self, sender, arg=None):
    timenow = time.time()
    for handler in self.handlers:
      if timenow - handler.lastcall > handler.period:
        handler.lastcall = timenow
        if self.try_handler(handler, sender, arg): break

  __call__ = fire
