import re
import time
import thread
import urllib2
import random

if __name__ != "__main__":
  from magnet_api import *
  from magnet_utils import *

try:
  try:
    from bs4 import BeautifulSoup
    soup_version = 4
  except ImportError:
    from BeautifulSoup import BeautifulSoup
    soup_version = 3
except ImportError:
  soup_version = None

# Known bugs:
# - when consecutive posts made within check period so that the last post
#   goes to the next page, only the last one will be notified about
# - can miss threads gone over to the second page of subforum over the check period
# - can miss threads that have posts deleted and added to be the same amount as last seen
# - can miss thread updates if watched thread is the only one that got updated
#   and there was an error loading subforum or that thread

really_down = False

last_check_times = {}#{"general": "Sep 14th 4:00am"}

# Format: thread_id: ("forum", last_post_id, timestamp)
watched_threads = {}#19669: ("general", 484700, "-")}

# Format: thread_id: "forum"
threads_to_start_watching = {}

available_forums = set(["general", "suggestions", "bugs", "artroom", "friendgames", "offtopic"])

forum_url = "http://drawception.com/forums/"
subforum_url = "http://drawception.com/forums/%s/"
last_page_url = "http://drawception.com/forums/%s/%s/-/?page=9999"


random_things = ['hobo', 'shoe', 'log', 'bun', 'sandwich', 'bull', 'beer', 'hair',
  'hill', 'beans', 'man', 'sofa', 'dinosaur', 'road', 'plank', 'hole', 'food',
  'hedgehog', 'pine', 'toad', 'tooth', 'candy', 'rock', 'drop', 'book', 'button', 'carpet',
  'wheel', 'computer', 'box', 'cat', 'rat', 'hook', 'chunk', 'boat', 'spade', 'sack',
  'hammer', 'face', 'soap', 'nose', 'finger', 'steam', 'spring', 'hand', 'fish',
  'elephant', 'dog', 'chair', 'bag', 'phone', 'robot', 'axe', 'grass', 'crack', 'teacher',
  'breadcrumb', 'fridge', 'worm', 'nut', 'cloth', 'apple', 'tongue', 'jar'];
random_acts = ['crazy from', 'thanks', 'hits', 'lies around on', 'sees', 'grows in',
  'attaches to', 'flies from', 'crawls from', 'chews', 'walks on', 'squishes', 'pecks',
  'wobbles in', 'smokes from', 'smokes', 'rides', 'eats', 'squeals from under',
  'is lost in', 'spins in', 'stuck in', 'hooks', 'angry at', 'bends', 'drips on',
  'rolls on', 'digs', 'crawls in', 'flies at', 'massages', 'dreams of', 'kills', 'pulls',
  "doesn't want", 'licks', 'shoots', 'falls off', 'falls in', 'crawls on', 'turns into',
  'stuck to', 'jumps on', 'hides', 'hides in', 'disassembles', 'rips', 'dissolves',
  'stretches', 'crushes', 'pushes', 'drowns in', 'pokes', 'runs away from', 'wants',
  'scratches', 'throws', 'and', 'confused by', 'unimpressed by'];
random_descs = ['white', 'concrete', 'shiny', 'ill', 'big', 'ex', 'fast', 'happy',
  'inside-out', 'hot', 'burning', 'thick', 'wooden', 'long', 'good', 'tattered', 'iron',
  'liquid', 'frozen', 'green', 'evil', 'bent', 'rough', 'pretty', 'red', 'round',
  'shaggy', 'bald', 'slow', 'wet', 'wrinkly', 'meaty', 'impudent', 'real', 'distraught',
  'sharp', 'plastic', 'gift', 'squished', 'chubby', 'crumbling', 'horned', 'angry',
  'sitting', 'stranded', 'dry', 'hard', 'thin', 'killer', 'walking', 'cold', 'wheezing',
  'grunting', 'chirping', 'wide', 'electric', 'nuclear', 'confused', 'unimpressed'];

random_draw = ['Draw', 'Paint', 'Scribble', 'Doodle', 'Make', 'Throw together', 'Sketch']

def command_draw(bot, room, nick, access_level, parameters, message):
  r = random.randint(1, 3)
  if r == 1:
    ch = [
      random.choice(random_descs),
      random.choice(random_things),
    ]
  elif r == 2:
    ch = [
      random.choice(random_descs),
      random.choice(random_things),
      random.choice(random_acts),
      random.choice(random_things),
    ]
  else:
    ch = [
      random.choice(random_descs),
      random.choice(random_things),
      random.choice(random_acts),
      random.choice(random_descs),
      random.choice(random_things),
    ]
  return "%s this: %s" % (random.choice(random_draw), ' '.join(ch))


def gethtml(url, ignore_errors=False):
  opener = urllib2.build_opener()
  opener.addheaders = [('User-agent', 'magnet2.py for Drawception chat')]
  if ignore_errors:
    try:
      f = opener.open(url)
      data = f.read()
      f.close()
    except urllib2.HTTPError as e:
      data = e.read()
  else:
    f = opener.open(url)
    data = f.read()
    f.close()
  return data

def new_message(text):
  thebot.send_room_message(theroom, text)

def site_is_down(down):
  global really_down
  if really_down != down:
    new_message("drawception.com is %s" % ("up!", "down.")[down])
  really_down = down

def parse_forum_url(url_or_text):
  m = re.search("(\w+)\W(\d+)", url_or_text)
  if not m: return "Couldn't extract forum and thread ID from that."
  forum = m.group(1)
  threadid = int(m.group(2))
  if not forum in available_forums: return "No such forum: '%s'." % forum
  return (forum, threadid)

def add_watch(url_or_text):
  res = parse_forum_url(url_or_text)
  if isinstance(res, str): return res
  forum, threadid = res
  if threadid in watched_threads: return "That thread is already watched."
  threads_to_start_watching[threadid] = forum
  return "Added forum thread %s/%d to watch." % (forum, threadid)

def remove_watch(url_or_text):
  res = parse_forum_url(url_or_text)
  if isinstance(res, str): return res
  forum, threadid = res
  res = "Thread %s/%d is not watched." % (forum, threadid)
  if threadid in threads_to_start_watching:
    threads_to_start_watching.pop(threadid)
    res = "Thread removed from watch."
  if threadid in watched_threads:
    watched_threads.pop(threadid)
    res = "Thread removed from watch."
  return res

def check_thread(forum, threadid, lastpostid, timestamp):
  url = last_page_url % (forum, threadid)
  html = gethtml(url)
  l = re.findall('div id="p(\d+)"', html)
  if not l: return
  newlastid = int(l[-1])
  watched_threads[threadid] = (forum, newlastid, timestamp)
  if lastpostid == newlastid: return # No new posts
  newposts = [x for x in l if int(x) > lastpostid]
  # Actual notification
  title = re.search('<title>(.+?)</title>', html).group(1)
  if not soup_version:
    new_message('New %s post(s) in %s forum thread "%s"' % (len(newposts), forum, title))
  else:
    if soup_version == 4:
      bs = BeautifulSoup(html)
    else:
      bs = BeautifulSoup(html, convertEntities=BeautifulSoup.HTML_ENTITIES)
    for newpost in newposts:
      post = bs.find("div", {"id": "p%s" % newpost})
      username = post.find("div", {"class": "comment-user"}).find("a").getText()
      text = post.find("div", {"class": "comment-body"}).getText(" ").strip("\n")
      if len(text) > 200: text = text[:195] + "[...]"
      page = int(timestamp) / 20 + 1 # "timestamp" is actually post count
      link = url.replace("?page=9999", "" if page == 1 else "?page=%d" % page)
      new_message('@%s posts in "%s" ( %s#p%s ):\n%s' % (username, title, link, newpost, text))

def check_thread_begin_watch(forum, threadid):
  url = last_page_url % (forum, threadid)
  html = gethtml(url)
  l = re.findall('div id="p(\d+)"', html)
  if not l: return
  lastpostid = int(l[-1])
  threads_to_start_watching.pop(threadid)
  watched_threads[threadid] = (forum, lastpostid, "-") # Timestamp will be added on the next check

def check_subforum(checkforum):
  reallycheck = set([])
  for threadid, v in watched_threads.items():
    forum, lastpostid, timestamp = v
    if forum == checkforum: reallycheck.add(forum)
  if not reallycheck: return # No watched threads in that subforum
  html = gethtml(subforum_url % checkforum)
  #timestamps = re.findall('<span class="muted">\(last post (.+?)\)', html)
  timestamps = re.findall('(\d+) replies <span class="muted">', html)
  if not timestamps: return
  threads = re.findall('<b><a href="/forums/\w+/(\d+)/', html)
  if not threads: return
  for threadid, timestamp in zip(threads, timestamps):
    threadid = int(threadid)
    if threadid in watched_threads:
      forum, lastpostid, ts = watched_threads[threadid]
      if ts != timestamp:
        check_thread(forum, threadid, lastpostid, timestamp)

def check_forum_mainpage():
  # check mainpage first so in case of failure can abandon
  html = gethtml(forum_url, True)
  l = re.findall("forums/(\w+).+?last post (.+?)\)", html)
  if not l:
    if html.find("<h1>There appears to be an error with this site.</h1>") != -1:
      site_is_down(True)
    return
  # Add to-be-watched threads to watched
  for threadid, forum in threads_to_start_watching.items():
    check_thread_begin_watch(forum, threadid)
  # For each subforum:
    # Check last post time
    # If has fresher time than last check AND has watched threads in that subforum, check subforum
  forumstocheck = set([])
  for forum, timestamp in l:
    if not forum in last_check_times or last_check_times[forum] != timestamp:
      forumstocheck.add(forum)
  if not forumstocheck: return # No updates
  for forum in forumstocheck:
    check_subforum(forum)
  # update timestamps last so no updates will be lost in case of page load error
  for forum, timestamp in l:
    last_check_times[forum] = timestamp
  site_is_down(False)

def timer_checkforum(bot, arg):
  thread.start_new_thread(check_forum_mainpage, ())

def command_watch(bot, room, nick, access_level, parameters, message):
  if not parameters: return 'Expected Drawception forum thread URL.'
  if message.getType() != 'groupchat':
    return 'Sneaky! This works only in the groupchat.'
  return add_watch(parameters)

def command_unwatch(bot, room, nick, access_level, parameters, message):
  if not parameters: return 'Expected Drawception forum thread URL.'
  if message.getType() != 'groupchat':
    return 'Sneaky! This works only in the groupchat.'
  return remove_watch(parameters)

def load(bot):
  global watched_threads, checkforum_timer, thebot, theroom
  thebot = bot
  theroom = "drawception@chat.grompe.org.ru"
  watched_threads = bot.load_database('dcforum') or {}
  bot.add_command('watch', command_watch, LEVEL_MEMBER)
  bot.add_command('unwatch', command_unwatch, LEVEL_MEMBER)
  bot.add_command('draw', command_draw, LEVEL_GUEST)
  checkforum_timer = TimedEventHandler(timer_checkforum, 240)
  bot.timed_events.add(checkforum_timer)

def save(bot):
  bot.save_database('dcforum', watched_threads)

def unload(bot):
  bot.timed_events.remove(checkforum_timer)

def info(bot):
  return 'Drawception forum watch plugin v1.0.3'

if __name__ == "__main__":

  def input_loop():
    while 1:
      s = raw_input("")
      if s.startswith("watch "):
        print add_watch(s[6:])
      elif s.startswith("unwatch "):
        print remove_watch(s[8:])
      else: print "Error: unknown command"

  lastcall = 0
  def sim_loop():
    global lastcall
    print "Watching Drawception forum now."
    print "Enter a command ([un]watch <URL>) or Ctrl+C to quit:"
    thread.start_new_thread(input_loop, ())
    while 1:
      timenow = time.time()
      if timenow - lastcall > 240:
        lastcall = timenow
        print "(Checking the forum...)"
        thread.start_new_thread(check_forum_mainpage, ())
      time.sleep(0.1)

  def print_new_message(text):
    print text

  new_message = print_new_message
  sim_loop()
